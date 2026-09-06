import client from "./client";

export const listGoals = (statusFilter) =>
  client.get("/api/goals", { params: statusFilter ? { status_filter: statusFilter } : {} }).then((r) => r.data);

export const createGoal = (payload) => client.post("/api/goals", payload).then((r) => r.data);
export const updateGoal = (id, payload) => client.patch(`/api/goals/${id}`, payload).then((r) => r.data);
export const deleteGoal = (id) => client.delete(`/api/goals/${id}`);
export const toggleTask = (goalId, taskId, isDone) =>
  client.patch(`/api/goals/${goalId}/tasks/${taskId}`, null, { params: { is_done: isDone } }).then((r) => r.data);
