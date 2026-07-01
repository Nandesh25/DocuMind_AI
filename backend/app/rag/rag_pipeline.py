"""Query-time Retrieval-Augmented Generation pipeline.

Orchestrates the RAG flow as a single cohesive, testable unit:
    retrieve -> assemble context -> generate -> cite.

Persistence stays in the service/repository layers; the pipeline receives a
`chunk_resolver` callback so it never depends on the database directly.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

from app.ai.llm.base import ILLMClient
from app.models.document_chunk import DocumentChunk
from app.rag.prompt_templates import build_rag_prompt
from app.rag.retriever import Retriever

ChunkResolver = Callable[[list[UUID]], Awaitable[list[DocumentChunk]]]


@dataclass
class RAGSource:
    chunk_id: UUID
    document_id: UUID
    score: float
    rank: int


@dataclass
class PreparedRAG:
    prompt: str
    sources: list[RAGSource]
    context_used: int


@dataclass
class RAGAnswer:
    answer: str
    model_name: str
    latency_ms: int
    context_used: int
    sources: list[RAGSource]


class RAGPipeline:
    def __init__(self, retriever: Retriever, llm: ILLMClient):
        self._retriever = retriever
        self._llm = llm

    @property
    def model_name(self) -> str:
        return self._llm.model_name

    async def prepare(
        self,
        *,
        workspace_id: UUID,
        question: str,
        top_k: int,
        chunk_resolver: ChunkResolver,
        document_ids: list[UUID] | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> PreparedRAG:
        """Retrieve context and build the grounded prompt + citations."""
        # 1. Retrieve — embedding + vector search run off the event loop.
        retrieved = await asyncio.to_thread(
            self._retriever.retrieve,
            workspace_id=workspace_id,
            query=question,
            top_k=top_k,
            document_ids=document_ids,
        )
        chunk_ids = [chunk_id for chunk_id, _, _ in retrieved]

        # 2. Resolve chunk text (via caller-provided repository lookup).
        chunks = await chunk_resolver(chunk_ids)
        chunk_map = {chunk.id: chunk for chunk in chunks}

        # 3. Assemble grounded context, preserving retrieval order.
        context_blocks = [
            chunk_map[chunk_id].content
            for chunk_id, _, _ in retrieved
            if chunk_id in chunk_map
        ]
        sources = [
            RAGSource(
                chunk_id=chunk_id,
                document_id=chunk_map[chunk_id].document_id,
                score=round(score, 5),
                rank=rank,
            )
            for rank, (chunk_id, score, _) in enumerate(retrieved, start=1)
            if chunk_id in chunk_map
        ]
        prompt = build_rag_prompt(question, context_blocks, history)
        return PreparedRAG(
            prompt=prompt, sources=sources, context_used=len(context_blocks)
        )

    async def answer(
        self,
        *,
        workspace_id: UUID,
        question: str,
        top_k: int,
        chunk_resolver: ChunkResolver,
        document_ids: list[UUID] | None = None,
        history: list[tuple[str, str]] | None = None,
    ) -> RAGAnswer:
        prepared = await self.prepare(
            workspace_id=workspace_id,
            question=question,
            top_k=top_k,
            chunk_resolver=chunk_resolver,
            document_ids=document_ids,
            history=history,
        )
        started = time.perf_counter()
        answer = await self._llm.generate(prepared.prompt)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return RAGAnswer(
            answer=answer,
            model_name=self._llm.model_name,
            latency_ms=latency_ms,
            context_used=prepared.context_used,
            sources=prepared.sources,
        )

    def stream(self, prepared: PreparedRAG):
        """Stream the answer tokens for an already-prepared prompt."""
        return self._llm.astream(prepared.prompt)
