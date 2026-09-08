function displayName(key) {
  return String(key || '')
    .replace(/^answer_/, '')
    .replace(/_/g, ' ');
}

function rowIsCorrect(row) {
  if (row.status) {
    return row.status === 'correct';
  }
  return Boolean(row.is_correct);
}

function normalizeRows(detailedResults) {
  if (!detailedResults) {
    return [];
  }
  if (Array.isArray(detailedResults)) {
    return detailedResults;
  }
  return Object.entries(detailedResults).map(([key, value]) => ({
    key,
    ...value,
  }));
}

export default function Results({ results }) {
  if (!results) {
    return null;
  }

  const correctCount = results.correct_count ?? 0;
  const total = results.total_questions ?? 0;
  const score = Number(results.score_percentage);
  const scoreText = Number.isFinite(score) ? `${score.toFixed(1)}%` : '—';
  const rows = normalizeRows(results.detailed_results);

  return (
    <section className="results">
      <h2>Your Results</h2>
      <div className="metrics">
        <div className="metric">
          <div className="metric-label">Questions Correct</div>
          <div className="metric-value">
            {correctCount}/{total}
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Total Score</div>
          <div className="metric-value">{scoreText}</div>
        </div>
      </div>
      <h3>Detailed Breakdown</h3>
      <div className="results-table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Question</th>
              <th>Your Answer</th>
              <th>Correct Answer</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const correct = rowIsCorrect(row);
              return (
                <tr key={row.key}>
                  <td className={correct ? 'status-correct' : 'status-incorrect'}>
                    {correct ? '✅' : '❌'}
                  </td>
                  <td>{displayName(row.key)}</td>
                  <td>{row.user_answer == null ? '' : String(row.user_answer)}</td>
                  <td>{row.correct_answer == null ? '' : String(row.correct_answer)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
