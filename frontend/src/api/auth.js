import client from "./client";

export const signup = (payload) => client.post("/api/auth/signup", payload).then((r) => r.data);
export const login = (payload) => client.post("/api/auth/login", payload).then((r) => r.data);
export const getMe = () => client.get("/api/auth/me").then((r) => r.data);
export const forgotPassword = (email) => client.post("/api/auth/forgot-password", { email }).then((r) => r.data);
export const resetPassword = (token, new_password) =>
  client.post("/api/auth/reset-password", { token, new_password }).then((r) => r.data);
export const verifyEmail = (token) => client.post("/api/auth/verify-email", { token }).then((r) => r.data);
export const updateProfile = (payload) => client.patch("/api/users/me", payload).then((r) => r.data);
