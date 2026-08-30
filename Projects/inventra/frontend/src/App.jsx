import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  Boxes,
  CloudRain,
  DollarSign,
  RefreshCw,
  Send,
  Sparkles,
  Truck,
} from "lucide-react";

import ChatBubble from "./components/ChatBubble";
import FlowStep from "./components/FlowStep";
import MetricCard from "./components/MetricCard";
import StatusPill from "./components/StatusPill";
import { appConfig } from "./config/appConfig";
import {
  checkHealth,
  sendChatMessage,
} from "./services/api";

const starterQuestions = [
  "Should we reorder SKU001 tomorrow in North?",
  "Forecast demand for SKU001 tomorrow in North.",
  "What is the current stock of SKU001?",
  "What is our cash position in North?",
];

function buildThreadId() {
  const stored = sessionStorage.getItem(
    "inventra_thread_id"
  );

  if (stored) return stored;

  const id =
    globalThis.crypto?.randomUUID?.() ||
    `thread-${Date.now()}`;

  sessionStorage.setItem(
    "inventra_thread_id",
    id
  );

  return id;
}

export default function App() {
  const [threadId] = useState(buildThreadId);
  const [apiStatus, setApiStatus] =
    useState("checking");
  const [loading, setLoading] =
    useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text:
        "Hi, I’m Inventra. Ask me about demand, stock, reorder decisions, finance, or vendors.",
    },
  ]);

  const [lastResult, setLastResult] =
    useState(null);

  const chatEndRef = useRef(null);

  const activeFlow = useMemo(() => {
    const intent = lastResult?.intent;

    return {
      context: Boolean(lastResult),
      planner: Boolean(lastResult),
      forecast:
        intent === "forecast" ||
        intent === "reorder_decision",
      inventory:
        intent === "inventory" ||
        intent === "reorder_decision",
      decision:
        intent === "reorder_decision",
      finance:
        intent === "finance" ||
        lastResult?.reorder_needed === true,
      vendor:
        intent === "vendor" ||
        lastResult?.reorder_needed === true,
      response: Boolean(lastResult),
    };
  }, [lastResult]);

  useEffect(() => {
    async function ping() {
      try {
        await checkHealth();
        setApiStatus("online");
      } catch {
        setApiStatus("offline");
      }
    }

    ping();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  async function submitMessage(text) {
    const question = (text ?? input).trim();

    if (!question || loading) return;

    setMessages((items) => [
      ...items,
      {
        role: "user",
        text: question,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const result =
        await sendChatMessage({
          message: question,
          threadId,
        });

      setLastResult(result);

      setMessages((items) => [
        ...items,
        {
          role: "assistant",
          text:
            result.answer ||
            "No answer was returned.",
        },
      ]);
    } catch (error) {
      const detail =
        error?.response?.data?.detail ||
        error?.message ||
        "Unknown API error.";

      setMessages((items) => [
        ...items,
        {
          role: "assistant",
          text: `Request failed: ${detail}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function resetConversation() {
    const newId =
      globalThis.crypto?.randomUUID?.() ||
      `thread-${Date.now()}`;

    sessionStorage.setItem(
      "inventra_thread_id",
      newId
    );

    window.location.reload();
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand-row">
            <div className="brand-mark">
              <Sparkles size={22} />
            </div>

            <div>
              <h1>{appConfig.appName}</h1>
              <p>{appConfig.subtitle}</p>
            </div>
          </div>
        </div>

        <div className="topbar-actions">
          <StatusPill status={apiStatus} />

          <button
            className="secondary-button"
            onClick={resetConversation}
            type="button"
          >
            <RefreshCw size={16} />
            New session
          </button>
        </div>
      </header>

      <main className="page-grid">
        <section className="main-column">
          <div className="hero-card">
            <div>
              <span className="eyebrow">
                AGENTIC INVENTORY INTELLIGENCE
              </span>

              <h2>
                Predict demand. Check stock.
                Make smarter reorder decisions.
              </h2>

              <p>
                Inventra combines live weather,
                ML forecasting, inventory,
                finance, and vendor intelligence
                through a LangGraph + MCP workflow.
              </p>
            </div>

            <div className="hero-orbit">
              <div className="orbit-core">
                <Sparkles size={28} />
                <span>Inventra</span>
              </div>
            </div>
          </div>

          <div className="metrics-grid">
            <MetricCard
              label="Intent"
              value={
                lastResult?.intent || "Waiting"
              }
              helper="Planner classification"
              icon={Activity}
            />

            <MetricCard
              label="SKU"
              value={lastResult?.sku}
              helper="Current context"
              icon={Boxes}
            />

            <MetricCard
              label="Region"
              value={lastResult?.region}
              helper="Forecast location"
              icon={CloudRain}
            />

            <MetricCard
              label="Reorder"
              value={
                lastResult?.reorder_needed == null
                  ? "—"
                  : lastResult.reorder_needed
                  ? "Required"
                  : "Not required"
              }
              helper="Deterministic decision"
              icon={Truck}
            />
          </div>

          <div className="panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">
                  LIVE WORKFLOW
                </span>
                <h3>Agent execution path</h3>
              </div>

              <span className="thread-chip">
                {threadId.slice(0, 8)}
              </span>
            </div>

            <div className="flow-track">
              <FlowStep
                label="Context"
                complete={activeFlow.context}
              />
              <FlowStep
                label="Planner"
                complete={activeFlow.planner}
              />
              <FlowStep
                label="Forecast"
                complete={activeFlow.forecast}
              />
              <FlowStep
                label="Inventory"
                complete={activeFlow.inventory}
              />
              <FlowStep
                label="Reorder gate"
                complete={activeFlow.decision}
              />
              <FlowStep
                label="Finance"
                complete={activeFlow.finance}
              />
              <FlowStep
                label="Vendor"
                complete={activeFlow.vendor}
              />
              <FlowStep
                label="Response"
                complete={activeFlow.response}
              />
            </div>
          </div>

          <div className="panel architecture-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">
                  CAPABILITIES
                </span>
                <h3>Connected intelligence</h3>
              </div>
            </div>

            <div className="capability-grid">
              <div className="capability-card">
                <CloudRain size={20} />
                <div>
                  <strong>Weather</strong>
                  <span>OpenWeatherMap</span>
                </div>
              </div>

              <div className="capability-card">
                <Sparkles size={20} />
                <div>
                  <strong>Forecast</strong>
                  <span>XGBoost</span>
                </div>
              </div>

              <div className="capability-card">
                <Boxes size={20} />
                <div>
                  <strong>Inventory</strong>
                  <span>Stock + reorder risk</span>
                </div>
              </div>

              <div className="capability-card">
                <DollarSign size={20} />
                <div>
                  <strong>Finance</strong>
                  <span>Cash + margin</span>
                </div>
              </div>

              <div className="capability-card">
                <Truck size={20} />
                <div>
                  <strong>Vendor</strong>
                  <span>Lead time + score</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <aside className="chat-panel">
          <div className="chat-heading">
            <div>
              <span className="eyebrow">
                COPILOT
              </span>
              <h3>Ask Inventra</h3>
            </div>

            {loading ? (
              <span className="thinking">
                Thinking…
              </span>
            ) : null}
          </div>

          <div className="starter-list">
            {starterQuestions.map((question) => (
              <button
                type="button"
                key={question}
                onClick={() =>
                  submitMessage(question)
                }
                disabled={loading}
              >
                {question}
              </button>
            ))}
          </div>

          <div className="chat-body">
            {messages.map((message, index) => (
              <ChatBubble
                key={`${message.role}-${index}`}
                role={message.role}
                text={message.text}
              />
            ))}

            <div ref={chatEndRef} />
          </div>

          <form
            className="chat-input-row"
            onSubmit={(event) => {
              event.preventDefault();
              submitMessage();
            }}
          >
            <textarea
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              placeholder="Ask about demand, stock, reorder..."
              rows={2}
              disabled={loading}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();
                  submitMessage();
                }
              }}
            />

            <button
              className="send-button"
              type="submit"
              disabled={loading}
              aria-label="Send message"
            >
              <Send size={19} />
            </button>
          </form>
        </aside>
      </main>
    </div>
  );
}
