from uuid import UUID

import asyncio

from app.ai.embeddings.minilm_embedder import get_embedder
from app.core.constants import DocumentStatus
from app.core.logging import get_logger
from app.database.session import AsyncSessionLocal
from app.models.document_chunk import DocumentChunk
from app.models.embedding_metadata import EmbeddingMetadata
from app.rag.chunker import estimate_tokens
from app.rag.pipeline import extract_and_chunk
from app.rag.retriever import collection_name
from app.repositories.implementations.document_repository import DocumentRepository
from app.repositories.implementations.vector_repository import ChromaVectorRepository

logger = get_logger(__name__)


class IngestionService:
    """Async pipeline: extract -> split -> store chunks + vectors.

    Runs as a background task with its own database session because the request
    session is already closed by the time it executes.
    """

    async def ingest(self, document_id: UUID) -> None:
        async with AsyncSessionLocal() as session:
            repo = DocumentRepository(session)
            document = await repo.get_by_id(document_id)
            if document is None:
                return
            try:
                document.status = DocumentStatus.PROCESSING
                await repo.update(document)
                await session.commit()

                # Step 1 + 2: extract text and split into overlapping chunks
                # (blocking file IO + splitting -> run off the event loop).
                extraction = await asyncio.to_thread(
                    extract_and_chunk, document.storage_path, document.mime_type
                )
                chunks = extraction.chunks
                if not chunks:
                    raise ValueError("No extractable text found in document.")

                embedder = get_embedder()
                vectors = ChromaVectorRepository()
                collection = collection_name(document.workspace_id)

                # Idempotency: clear any previously indexed chunks/vectors.
                existing_ids = await repo.get_chunk_ids_by_document(document.id)
                if existing_ids:
                    await asyncio.to_thread(
                        vectors.delete, collection, [str(i) for i in existing_ids]
                    )
                    await repo.delete_chunks_by_document(document.id)

                texts = [c.content for c in chunks]
                embeddings = await asyncio.to_thread(embedder.embed_documents, texts)

                # Step 3: store chunks.
                chunk_models = [
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=c.index,
                        content=c.content,
                        token_count=estimate_tokens(c.content),
                        page_number=c.page_number,
                    )
                    for c in chunks
                ]
                await repo.add_chunks(chunk_models)

                ids, metadatas = [], []
                for chunk_model in chunk_models:
                    vector_id = str(chunk_model.id)
                    ids.append(vector_id)
                    metadatas.append(
                        {
                            "chunk_id": vector_id,
                            "document_id": str(document.id),
                            "workspace_id": str(document.workspace_id),
                            "page_number": chunk_model.page_number or 0,
                        }
                    )
                    await repo.add_embedding(
                        EmbeddingMetadata(
                            chunk_id=chunk_model.id,
                            vector_id=vector_id,
                            collection_name=collection,
                        )
                    )

                await asyncio.to_thread(
                    vectors.upsert,
                    collection=collection,
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                )

                document.status = DocumentStatus.INDEXED
                document.error_message = None
                document.page_count = extraction.page_count
                document.chunk_count = extraction.chunk_count
                document.word_count = extraction.word_count
                await repo.update(document)
                await session.commit()
                logger.info(
                    "Indexed document %s (%d chunks, %d pages, %d words)",
                    document.id,
                    extraction.chunk_count,
                    extraction.page_count,
                    extraction.word_count,
                )
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                logger.error("Ingestion failed for %s: %s", document_id, exc)
                document = await repo.get_by_id(document_id)
                if document:
                    document.status = DocumentStatus.FAILED
                    document.error_message = str(exc)[:500]
                    await repo.update(document)
                    await session.commit()
