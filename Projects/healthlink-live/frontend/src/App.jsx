import { useEffect, useRef, useState } from "react";
import BookingConfirmation from "./BookingConfirmation";
import {
  createConversation,
  getMessages,
  sendMessage,
} from "./api";

const STORAGE_KEY = "healthlink.conversationId";

export default function App() {
  const [conversationId, setConversationId] = useState(
    () => localStorage.getItem(STORAGE_KEY) || "",
  );
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyReady, setHistoryReady] = useState(false);
  const [error, setError] = useState("");

  const [bookingProposal, setBookingProposal] = useState(null);
  const [bookingBlocked, setBookingBlocked] = useState(false);

  const bottomRef = useRef(null);
  const requestInFlight = useRef(false);

  // Restore messages when the active conversation changes.
  useEffect(() => {
    let cancelled = false;

    setMessages([]);
    setHistoryReady(false);
    setError("");

    if (!conversationId) {
      return;
    }

    async function restoreHistory() {
      try {
        const data = await getMessages(conversationId);

        if (!cancelled) {
          setMessages(data.messages);
          setHistoryReady(true);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      }
    }

    restoreHistory();

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function startNewChat() {
    if (requestInFlight.current || busy || bookingBlocked) {
      return;
    }

    requestInFlight.current = true;
    setBusy(true);
    setError("");

    try {
      const conversation = await createConversation();

      localStorage.setItem(STORAGE_KEY, conversation.id);

      setBookingProposal(null);
      setBookingBlocked(false);
      setHistoryReady(false);
      setConversationId(conversation.id);
      setDraft("");
    } catch (err) {
      setError(err.message);
    } finally {
      requestInFlight.current = false;
      setBusy(false);
    }
  }

  async function handleSend(event) {
    event.preventDefault();

    const message = draft.trim();

    if (
      !message ||
      !conversationId ||
      !historyReady ||
      busy ||
      bookingBlocked ||
      requestInFlight.current
    ) {
      return;
    }

    requestInFlight.current = true;
    setBusy(true);
    setError("");

    // A new turn replaces any previous unconfirmed proposal.
    setBookingProposal(null);

    try {
      const result = await sendMessage(conversationId, message);

      setBookingProposal(result.booking_proposal ?? null);
      setDraft("");
    } catch (err) {
      setError(err.message);
    } finally {
      // Reload persisted messages even when the AI request fails.
      try {
        const data = await getMessages(conversationId);
        setMessages(data.messages);
      } catch {
        setHistoryReady(false);
        setError(
          "Could not reload history. Refresh before sending again.",
        );
      }

      requestInFlight.current = false;
      setBusy(false);
    }
  }

  function dismissBookingProposal() {
    if (bookingBlocked) {
      return;
    }

    setBookingProposal(null);
  }

  const chatDisabled =
    !conversationId || !historyReady || busy || bookingBlocked;

  return (
    <main className="chat-shell">
      <header>
        <div>
          <h1>HealthLink</h1>
          <p>Find relevant care through conversation.</p>
        </div>

        <button
          type="button"
          onClick={startNewChat}
          disabled={busy || bookingBlocked}
        >
          New chat
        </button>
      </header>

      <div className="notice">
        Demo patient · Care navigation, not a diagnosis service.
        Ask to book a slot, then review and confirm the appointment card.
      </div>

      <section className="messages" aria-label="Conversation">
        {!conversationId && (
          <div className="empty">
            <h2>How can we help?</h2>
            <p>Click New chat, then describe your concern.</p>
          </div>
        )}

        {conversationId && historyReady && messages.length === 0 && (
          <p className="empty">
            Tell us your concern, or ask to see dermatologists.
          </p>
        )}

        {messages.map((message) => (
          <article
            key={message.id}
            className={`message ${message.role}`}
          >
            <div className="message-meta">
              <strong>
                {message.role === "user" ? "You" : "HealthLink"}
              </strong>

              <time dateTime={message.created_at}>
                {new Date(message.created_at).toLocaleTimeString(
                  "en-IN",
                  {
                    timeZone: "Asia/Kolkata",
                    hour: "2-digit",
                    minute: "2-digit",
                  },
                )}{" "}
                IST
              </time>
            </div>

            <p>{message.content}</p>

            {message.status === "failed" && (
              <small className="failed">This turn failed.</small>
            )}

            {message.status === "pending" && (
              <small>Reply pending.</small>
            )}
          </article>
        ))}

        {busy && <p role="status">Working on your request…</p>}

        <div ref={bottomRef} />
      </section>

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSend}>
        <textarea
          aria-label="Your message"
          placeholder="Describe your concern…"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          maxLength={2000}
          rows={2}
          disabled={chatDisabled}
        />

        <button
          type="submit"
          disabled={chatDisabled || !draft.trim()}
        >
          Send
        </button>
      </form>

      {conversationId && bookingProposal && (
        <BookingConfirmation
          key={bookingProposal.proposal_id}
          conversationId={conversationId}
          proposal={bookingProposal}
          onBlockedChange={setBookingBlocked}
          onDismiss={dismissBookingProposal}
        />
      )}
    </main>
  );
}