import client from "./client";

export const logHabit = (payload) => client.post("/api/habits", payload).then((r) => r.data);
export const listHabits = (days = 30) => client.get("/api/habits", { params: { days } }).then((r) => r.data);
