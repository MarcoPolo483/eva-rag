export type Doc = { id: string; text: string; metadata?: Record<string, unknown> };

export type Chunk = {
  id: string;
  docId: string;
  text: string;
  metadata?: Record<string, unknown>;
};

export interface Chunker {
  chunk(doc: Doc): Promise<Chunk[]>;
}

export interface Embeddings {
  embed(texts: string[], options?: Record<string, unknown>): Promise<number[][]>;
  dimensions?: number;
}

export type Vector = number[];

export interface VectorStore {
  upsert(items: { id: string; text: string; vector: Vector; metadata?: Record<string, unknown> }[]): Promise<void>;
  query(vector: Vector, k: number, filter?: Record<string, unknown>): Promise<{ id: string; score: number; metadata?: Record<string, unknown> }[]>;
}

export interface SparseIndex {
  add(chunks: Chunk[]): Promise<void>;
  search(query: string, k: number): Promise<{ id: string; score: number }[]>;
}

export type Retrieved = { id: string; score: number; text?: string; metadata?: Record<string, unknown> };

export interface Retriever {
  query(text: string, k: number, filter?: Record<string, unknown>): Promise<Retrieved[]>;
}

export interface Reranker {
  rerank(query: string, results: Retrieved[], topK: number): Promise<Retrieved[]>;
}