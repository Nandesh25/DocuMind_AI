from uuid import UUID

import asyncio

from app.rag.retriever import Retriever
from app.repositories.interfaces.i_document_repository import IDocumentRepository
from app.schemas.search_schema import SearchRequest, SearchResponse, SearchResult
from app.services.workspace_service import WorkspaceService


class SearchService:
    def __init__(
        self,
        retriever: Retriever,
        document_repo: IDocumentRepository,
        workspace_service: WorkspaceService,
    ):
        self._retriever = retriever
        self._documents = document_repo
        self._workspaces = workspace_service

    async def semantic_search(
        self, workspace_id: UUID, user_id: UUID, data: SearchRequest
    ) -> SearchResponse:
        await self._workspaces.require_member(workspace_id, user_id)

        # Embedding + vector query are blocking; run off the event loop.
        retrieved = await asyncio.to_thread(
            self._retriever.retrieve,
            workspace_id=workspace_id,
            query=data.query,
            top_k=data.top_k,
            document_ids=data.document_ids,
            min_score=data.min_score,
        )
        chunk_ids = [cid for cid, _, _ in retrieved]
        chunks = await self._documents.get_chunks_by_ids(chunk_ids)
        chunk_map = {c.id: c for c in chunks}

        title_cache: dict[UUID, str] = {}
        results: list[SearchResult] = []
        for cid, score, _ in retrieved:
            chunk = chunk_map.get(cid)
            if not chunk:
                continue
            if chunk.document_id not in title_cache:
                doc = await self._documents.get_by_id(chunk.document_id)
                title_cache[chunk.document_id] = doc.title if doc else "Unknown"
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_title=title_cache[chunk.document_id],
                    content=chunk.content,
                    score=round(score, 5),
                    page_number=chunk.page_number,
                )
            )
        return SearchResponse(query=data.query, results=results, total=len(results))
