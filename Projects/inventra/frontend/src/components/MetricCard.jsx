export default function MetricCard({
  label,
  value,
  helper,
  icon: Icon,
}) {
  return (
    <div className="metric-card">
      <div className="metric-icon">
        {Icon ? <Icon size={20} /> : null}
      </div>

      <div>
        <div className="metric-label">{label}</div>
        <div className="metric-value">{value ?? "—"}</div>
        {helper ? (
          <div className="metric-helper">{helper}</div>
        ) : null}
      </div>
    </div>
  );
}
