import { Bot, User } from "lucide-react";

export default function ChatBubble({ role, text }) {
  const isUser = role === "user";

  return (
    <div
      className={`chat-row ${
        isUser ? "chat-row-user" : "chat-row-assistant"
      }`}
    >
      <div className="avatar">
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div
        className={`chat-bubble ${
          isUser ? "bubble-user" : "bubble-assistant"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
