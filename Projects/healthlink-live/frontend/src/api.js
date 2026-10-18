async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, options);

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;

    const error = new Error(
      typeof detail === "string"
        ? detail
        : `Request failed (${response.status}). Please try again.`
    );
    error.status = response.status;
    throw error;
  }

  if (data === null) {
    throw new Error("Backend returned an unexpected response.");
  }

  return data;
}

export function createConversation() {
  return request("/conversations", {
    method: "POST",
  });
}

export function getMessages(conversationId) {
  return request(`/conversations/${conversationId}/messages`);
}

export function sendMessage(conversationId, message) {
  return request(`/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });
}


export function findDoctors(specialty) {
  return request(
    `/doctors?specialty=${encodeURIComponent(specialty.trim())}`
  );
}

export function getDoctorSlots(doctorId, date) {
  return request(
    `/doctors/${doctorId}/slots?on_date=${encodeURIComponent(date)}`
  );
}

export function bookAppointment(payload) {
  return request("/appointments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}