import client from "./client";

export const getDigitalTwin = () => client.get("/api/digital-twin").then((r) => r.data);
