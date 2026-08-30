export default function FlowStep({
  label,
  active = false,
  complete = false,
}) {
  return (
    <div
      className={`flow-step ${
        complete ? "flow-complete" : ""
      } ${active ? "flow-active" : ""}`}
    >
      <span className="flow-node" />
      <span>{label}</span>
    </div>
  );
}
