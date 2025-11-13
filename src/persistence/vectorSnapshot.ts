import { InMemoryVectorStore } from "../vector/inMemory.js";

export type VectorSnapshot = {
  items: { id: string; text: string; vector: number[]; metadata?: Record<string, unknown> }[];
};

export function snapshot(store: InMemoryVectorStore): VectorSnapshot {
  // @ts-expect-error access private map via JSON roundtrip - we expose via query/getText only,
  // so snapshot relies on a best-effort method below
  const ids: string[] = Array.from(store["data"]?.keys?.() ?? []);
  const items: VectorSnapshot["items"] = ids.map((id) => {
    // @ts-expect-error private access for snapshotting
    const e = store["data"].get(id);
    return { id: e.id, text: e.text, vector: e.vector, metadata: e.metadata };
  });
  return { items };
}

export async function restore(store: InMemoryVectorStore, snap: VectorSnapshot) {
  await store.upsert(snap.items.map((it) => ({ id: it.id, text: it.text, vector: it.vector, metadata: it.metadata })));
}