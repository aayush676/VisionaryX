import client from "./client";

export const listNotifications = (unreadOnly = false) =>
  client.get("/api/notifications", { params: { unread_only: unreadOnly } }).then((r) => r.data);

export const markNotificationRead = (id) => client.patch(`/api/notifications/${id}/read`).then((r) => r.data);
export const markAllNotificationsRead = () => client.patch("/api/notifications/read-all").then((r) => r.data);
