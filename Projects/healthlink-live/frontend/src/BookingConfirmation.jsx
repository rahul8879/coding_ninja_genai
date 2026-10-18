import { useEffect, useRef, useState } from "react";
import { bookAppointment } from "./api";

function displayTime(value) {
  return new Date(value).toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function BookingConfirmation({
  conversationId,
  proposal,
  onBlockedChange,
  onDismiss,
}) {
  const [busy, setBusy] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const [rejected, setRejected] = useState(false);
  const [error, setError] = useState("");
  const [appointment, setAppointment] = useState(null);
  const inFlight = useRef(false);

  useEffect(() => {
    onBlockedChange(busy || uncertain);
  }, [busy, uncertain, onBlockedChange]);

  async function confirm() {
    if (inFlight.current || appointment || rejected) return;

    inFlight.current = true;
    setBusy(true);
    setError("");

    try {
      const result = await bookAppointment({
        conversation_id: conversationId,
        doctor_id: proposal.doctor_id,
        starts_at: proposal.starts_at,

        // Reuse this key on every retry of this card.
        idempotency_key: proposal.proposal_id,
      });

      setAppointment(result);
      setUncertain(false);
    } catch (err) {
      if (err.status >= 400 && err.status < 500) {
        setUncertain(false);
        setRejected(true);
        setError(
          `${err.message} Dismiss this card and ask for available slots again.`
        );
      } else {
        setUncertain(true);
        setError(
          "Could not confirm the result. Click Retry confirmation. " +
          "The same request will be retried safely."
        );
      }
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  return (
    <section
      className="booking-panel"
      aria-label="Appointment confirmation"
    >
      <h3>
        {appointment ? "Appointment confirmed" : "Review appointment"}
      </h3>

      <p><strong>{proposal.doctor_name}</strong></p>
      <p>{displayTime(proposal.starts_at)} IST</p>
      <p>Duration: 30 minutes</p>

      {appointment ? (
        <div className="booking-success" role="status">
          Appointment ID: {appointment.appointment_id}
        </div>
      ) : (
        <p>The slot is checked again when you confirm.</p>
      )}

      {error && (
        <p className="error" role="alert">{error}</p>
      )}

      <div className="booking-actions">
        {!appointment && !rejected && (
          <button
            type="button"
            onClick={confirm}
            disabled={busy}
          >
            {busy
              ? "Confirming…"
              : uncertain
                ? "Retry confirmation"
                : "Confirm booking"}
          </button>
        )}

        <button
          type="button"
          onClick={onDismiss}
          disabled={busy || uncertain}
        >
          {appointment ? "Close" : "Dismiss"}
        </button>
      </div>
    </section>
  );
}