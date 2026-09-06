import client from "./client";

export const listMemory = (limit = 30) => client.get("/api/memory", { params: { limit } }).then((r) => r.data);
