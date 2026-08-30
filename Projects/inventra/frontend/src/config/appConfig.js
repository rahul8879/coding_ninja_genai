export const appConfig = {
  appName: import.meta.env.VITE_APP_NAME || "Inventra AI",
  subtitle:
    import.meta.env.VITE_APP_SUBTITLE ||
    "Weather-aware Inventory Intelligence",

  apiBaseUrl:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000",

  chatPath:
    import.meta.env.VITE_API_CHAT_PATH ||
    "/api/v1/chat",

  healthPath:
    import.meta.env.VITE_API_HEALTH_PATH ||
    "/api/v1/health",
};
