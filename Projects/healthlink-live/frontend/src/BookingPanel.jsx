import { useEffect, useRef, useState } from "react";
import {
  findDoctors,
  getDoctorSlots,
  bookAppointment,
} from "./api";

function clinicToday() {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());

  const values = Object.fromEntries(
    parts.map(({ type, value }) => [type, value])
  );

  return `${values.year}-${values.month}-${values.day}`;
}

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

export default function BookingPanel({
  conversationId,
  onBlockedChange,
}) {
  const [specialty, setSpecialty] = useState("Dermatology");
  const [doctors, setDoctors] = useState([]);
  const [doctorId, setDoctorId] = useState("");
  const [date, setDate] = useState(clinicToday);
  const [slots, setSlots] = useState([]);
  const [slotsLoaded, setSlotsLoaded] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [confirmation, setConfirmation] = useState(null);

  // Keep the exact request after an uncertain network/server failure.
  // Retrying uses the same idempotency key.
  const [pendingRequest, setPendingRequest] = useState(null);

  // Prevent two clicks before React updates the disabled button.
  const inFlight = useRef(false);

  const locked = busy || pendingRequest !== null;
  const selectedDoctor = doctors.find(
    (doctor) => String(doctor.id) === doctorId
  );

  useEffect(() => {
    onBlockedChange(locked);
  }, [locked, onBlockedChange]);

  function resetSlots() {
    setSlots([]);
    setSlotsLoaded(false);
    setSelectedSlot("");
    setConfirmation(null);
    setError("");
  }

  async function loadDoctors() {
    if (inFlight.current || pendingRequest || !specialty.trim()) return;

    inFlight.current = true;
    setBusy(true);
    setDoctors([]);
    setDoctorId("");
    resetSlots();

    try {
      const data = await findDoctors(specialty);
      setDoctors(data.doctors);

      if (data.doctors.length === 0) {
        setError("No doctors found for this specialty.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  async function loadSlots() {
    if (inFlight.current || pendingRequest || !doctorId || !date) return;

    inFlight.current = true;
    setBusy(true);
    resetSlots();

    try {
      const data = await getDoctorSlots(doctorId, date);
      setSlots(data.slots);
      setSlotsLoaded(true);
    } catch (err) {
      setError(err.message);
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  async function confirmBooking() {
    if (inFlight.current || !conversationId) return;
    if (!pendingRequest && !selectedSlot) return;

    const payload = pendingRequest ?? {
      conversation_id: conversationId,
      doctor_id: Number(doctorId),
      starts_at: selectedSlot,
      idempotency_key: crypto.randomUUID(),
    };

    inFlight.current = true;
    setPendingRequest(payload);
    setBusy(true);
    setError("");

    try {
      const result = await bookAppointment(payload);
      setConfirmation(result);
      setPendingRequest(null);
      setSelectedSlot("");
      setSlots([]);
      setSlotsLoaded(false);
    } catch (err) {
      if (err.status >= 400 && err.status < 500) {
        // Backend rejected the request. Allow a fresh selection.
        setPendingRequest(null);
        setSelectedSlot("");
        setSlots([]);
        setSlotsLoaded(false);
        setError(`${err.message} Load slots again before retrying.`);
      } else {
        // The server may have saved the appointment even if
        // the browser did not receive the response.
        setError(
          "Booking result could not be confirmed. Click Retry booking " +
          "to safely check the same request."
        );
      }
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  return (
    <details className="booking-panel">
      <summary>Book appointment</summary>

      <p>
        Choose a doctor and an available slot.
        All times are shown in IST.
      </p>

      <fieldset disabled={locked}>
        <label>
          Specialty
          <input
            value={specialty}
            maxLength={100}
            onChange={(event) => {
              setSpecialty(event.target.value);
              setDoctors([]);
              setDoctorId("");
              resetSlots();
            }}
            placeholder="For example, Dermatology"
          />
        </label>

        <button
          type="button"
          onClick={loadDoctors}
          disabled={!specialty.trim()}
        >
          Find doctors
        </button>

        <label>
          Doctor
          <select
            value={doctorId}
            onChange={(event) => {
              setDoctorId(event.target.value);
              resetSlots();
            }}
          >
            <option value="">Select a doctor</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.name} — {doctor.specialty} — {doctor.location}
              </option>
            ))}
          </select>
        </label>

        <label>
          Appointment date
          <input
            type="date"
            value={date}
            min={clinicToday()}
            onChange={(event) => {
              setDate(event.target.value);
              resetSlots();
            }}
          />
        </label>

        <small>Choose today or a date within the next 14 days.</small>

        <button
          type="button"
          onClick={loadSlots}
          disabled={!doctorId || !date}
        >
          Load available slots
        </button>

        {slotsLoaded && slots.length === 0 && (
          <p>No available slots. Try another date.</p>
        )}

        {slots.length > 0 && (
          <label>
            Available time
            <select
              value={selectedSlot}
              onChange={(event) => setSelectedSlot(event.target.value)}
            >
              <option value="">Select a slot</option>
              {slots.map((slot) => (
                <option key={slot.starts_at} value={slot.starts_at}>
                  {displayTime(slot.starts_at)} IST
                </option>
              ))}
            </select>
          </label>
        )}
      </fieldset>

      {selectedSlot && (
        <p>
          <strong>Confirm details:</strong>{" "}
          {selectedDoctor?.name} · {displayTime(selectedSlot)} IST
          {" "}· 30 minutes
        </p>
      )}

      {error && <p className="error" role="alert">{error}</p>}

      {(selectedSlot || pendingRequest) && (
        <button
          type="button"
          onClick={confirmBooking}
          disabled={busy}
        >
          {busy
            ? "Confirming…"
            : pendingRequest
              ? "Retry booking"
              : "Confirm booking"}
        </button>
      )}

      {busy && <p role="status">Processing request…</p>}

      {confirmation && (
        <div className="booking-success" role="status">
          <strong>Appointment confirmed</strong>
          <p>
            {selectedDoctor?.name} ·{" "}
            {displayTime(confirmation.starts_at)} IST
          </p>
          <p>Appointment ID: {confirmation.appointment_id}</p>
        </div>
      )}
    </details>
  );
}