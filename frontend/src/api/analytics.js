import client from "./client";

export const createSnapshot = () => client.post("/api/analytics/snapshot").then((r) => r.data);
export const getAnalyticsHistory = (days = 30) =>
  client.get("/api/analytics/history", { params: { days } }).then((r) => r.data);
