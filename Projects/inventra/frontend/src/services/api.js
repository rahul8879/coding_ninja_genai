import axios from "axios";
import { appConfig } from "../config/appConfig";

const api = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function checkHealth() {
  const response = await api.get(appConfig.healthPath);
  return response.data;
}

export async function sendChatMessage({ message, threadId }) {
  const response = await api.post(appConfig.chatPath, {
    message,
    thread_id: threadId,
  });

  return response.data;
}
