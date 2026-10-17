async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, options);
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    throw new Error(typeof detail === "string" ? detail :
      `Request failed (${response.status}). Please try again.`);
  }
  if (data === null) throw new Error("Backend returned an unexpected response.");
  return data;
}
export function createConversation() {
  return request("/conversations", { method: "POST" });
}
export function getMessages(conversationId) {
  return request(`/conversations/${conversationId}/messages`);
}
export function sendMessage(conversationId, message) {
  return request(`/conversations/${conversationId}/messages`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
}