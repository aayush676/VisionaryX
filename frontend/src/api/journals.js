import client from "./client";

export const createJournal = (content) => client.post("/api/journals", { content }).then((r) => r.data);
export const listJournals = (days = 30) => client.get("/api/journals", { params: { days } }).then((r) => r.data);
