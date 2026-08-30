export default function StatusPill({ status }) {
  const label =
    status === "online"
      ? "API Online"
      : status === "offline"
      ? "API Offline"
      : "Checking API";

  return (
    <span className={`status-pill status-${status}`}>
      <span className="status-dot" />
      {label}
    </span>
  );
}
