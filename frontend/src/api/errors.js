const API_TARGET = import.meta.env.VITE_API_URL || "the backend (via the dev proxy)";

/**
 * Turn an Axios error into something a user can act on.
 *
 * The important case is `err.response === undefined`: the request never got a
 * response at all (backend down, wrong API URL, or the browser blocked it for
 * CORS). Collapsing that into a generic "couldn't do the thing" message hides
 * the only detail that actually helps, so it gets its own message here.
 */
export function extractErrorMessage(err, fallback = "Something went wrong. Please try again.") {
  const detail = err?.response?.data?.detail;
  if (detail) return typeof detail === "string" ? detail : JSON.stringify(detail);

  if (err?.response) return `${fallback} (server responded ${err.response.status})`;

  return `Can't reach ${API_TARGET}. Check that the backend is running on port 8000.`;
}
