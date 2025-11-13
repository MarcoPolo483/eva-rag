import type { Chunker, Doc, Embeddings, VectorStore, SparseIndex, Retriever, Reranker, Retrieved } from "../types.js";
import { HybridRetriever } from "../retrieval/hybridRetriever.js";

export type RAGEngineOptions = {
  chunker: Chunker;
  embeddings: Embeddings;
  vectorStore: VectorStore;
  bm25: SparseIndex;
  alpha?: number;
  reranker?: Reranker;
};

export class RAGEngine {
  private retriever: Retriever;

  constructor(private readonly opts: RAGEngineOptions) {
    this.retriever = new HybridRetriever(opts.vectorStore, opts.embeddings, opts.bm25, { alpha: opts.alpha ?? 0.5 });
  }

  async ingest(docs: Doc[]): Promise<void> {
    for (const doc of docs) {
      const chunks = await this.opts.chunker.chunk(doc);
      const vectors = await this.opts.embeddings.embed(chunks.map((c) => c.text));
      await this.opts.vectorStore.upsert(
        chunks.map((c, i) => ({ id: c.id, text: c.text, vector: vectors[i], metadata: c.metadata }))
      );
      await this.opts.bm25.add(chunks);
    }
  }

  async retrieve(query: string, k: number, filter?: Record<string, unknown>): Promise<Retrieved[]> {
    const results = await this.retriever.query(query, k * 2, filter);
    if (this.opts.reranker) {
      return this.opts.reranker.rerank(query, results, k);
    }
    return results.slice(0, k);
  }
}