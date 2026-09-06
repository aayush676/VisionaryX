import client from "./client";

export const sendChatMessage = (message, mode) =>
  client.post("/api/chatbot/message", { message, mode }).then((r) => r.data);

export const listChatModes = () => client.get("/api/chatbot/modes").then((r) => r.data);
