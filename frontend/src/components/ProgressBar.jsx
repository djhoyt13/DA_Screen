export default function ProgressBar({ answered, total }) {
  const safeTotal = total > 0 ? total : 0;
  const ratio = safeTotal > 0 ? Math.min(answered / safeTotal, 1) : 0;
  const percent = Math.round(ratio * 100);

  return (
    <div className="progress-wrap" role="status" aria-live="polite">
      <div className="progress-label">
        Progress: {answered}/{safeTotal} questions answered
      </div>
      <div
        className="progress-track"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
        aria-label={`${answered} of ${safeTotal} questions answered`}
      >
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

