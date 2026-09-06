import client from "./client";

export const runSimulation = (horizon, adjustments = null) =>
  client.post("/api/simulations/run", { horizon, adjustments }).then((r) => r.data);

export const runWhatIf = (horizon, adjustments) =>
  client.post("/api/simulations/what-if", { horizon, adjustments }).then((r) => r.data);

export const compareLifePaths = (horizon, paths, labels) =>
  client.post("/api/simulations/compare-life-paths", { horizon, paths, labels }).then((r) => r.data);

export const listSimulations = (limit = 20) =>
  client.get("/api/simulations", { params: { limit } }).then((r) => r.data);
