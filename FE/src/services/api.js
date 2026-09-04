const API_URL = "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) throw new Error("Backend request failed");
  return response.json();
}

export const getStatus = () => request("/status");
export const startAgent = (duration) =>
  request("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration: Number(duration) }),
  });
export const stopAgent = () => request("/stop", { method: "POST" });
