import { useEffect, useMemo, useState } from 'react';
import {
  ApiError,
  adminCreateExam,
  adminExamDetail,
  adminListExams,
} from '../api.js';

const ADMIN_KEY_STORAGE = 'da_screen_admin_key';

const STATUS_CLASS = {
  sent: 'status-sent',
  opened: 'status-opened',
  opened_but_not_completed: 'status-inprogress',
  completed: 'status-completed',
};

function formatWhen(value) {
  if (!value) return '—';
  return String(value).replace('T', ' ').slice(0, 19);
}

export default function AdminDashboard() {
  const [adminKey, setAdminKey] = useState(() => sessionStorage.getItem(ADMIN_KEY_STORAGE) || '');
  const [keyInput, setKeyInput] = useState(adminKey);
  const [exams, setExams] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    recruiter_email: '',
    assessment: 'ds',
  });
  const [createdUrl, setCreatedUrl] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = useMemo(() => {
    if (filter === 'all') return exams;
    return exams.filter((exam) => exam.status === filter);
  }, [exams, filter]);

  async function loadExams(key = adminKey) {
    if (!key) return;
    setLoading(true);
    setError('');
    try {
      const data = await adminListExams(key);
      setExams(data.exams || []);
    } catch (err) {
      setExams([]);
      setError(err instanceof ApiError ? err.message : 'Failed to load exams');
      if (err instanceof ApiError && (err.status === 401 || err.status === 503)) {
        sessionStorage.removeItem(ADMIN_KEY_STORAGE);
        setAdminKey('');
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (adminKey) {
      loadExams(adminKey);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [adminKey]);

  async function handleLogin(event) {
    event.preventDefault();
    const next = keyInput.trim();
    if (!next) {
      setError('Enter the admin API key');
      return;
    }
    sessionStorage.setItem(ADMIN_KEY_STORAGE, next);
    setAdminKey(next);
  }

  async function handleCreate(event) {
    event.preventDefault();
    setError('');
    setCreatedUrl('');
    try {
      const created = await adminCreateExam(adminKey, form);
      setCreatedUrl(created.invite_url || '');
      setForm({
        name: '',
        email: '',
        phone: '',
        recruiter_email: '',
        assessment: form.assessment,
      });
      await loadExams();
      setSelectedId(created.id);
      const detailData = await adminExamDetail(adminKey, created.id);
      setDetail(detailData);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create invite');
    }
  }

  async function openDetail(id) {
    setSelectedId(id);
    setError('');
    try {
      const data = await adminExamDetail(adminKey, id);
      setDetail(data);
    } catch (err) {
      setDetail(null);
      setError(err instanceof ApiError ? err.message : 'Failed to load detail');
    }
  }

  if (!adminKey) {
    return (
      <div className="page admin-page">
        <header className="brand-bar">
          <div className="brand-lockup">
            <img className="brand-mark" src="/mantech-m.png" alt="MANTECH" width={42} height={42} />
            <div className="brand-text">
              <span className="brand-name">MANTECH</span>
              <span className="brand-mantra">Always Advancing™</span>
            </div>
          </div>
          <span className="brand-pill">Admin</span>
        </header>
        <h1>Assessment Admin</h1>
        <p className="chooser-lead">
          Sign in with the server <code>ADMIN_API_KEY</code> to track invites and review results.
        </p>
        <form className="admin-login" onSubmit={handleLogin}>
          <label htmlFor="admin-key">Admin API key</label>
          <input
            id="admin-key"
            type="password"
            value={keyInput}
            onChange={(event) => setKeyInput(event.target.value)}
            autoComplete="current-password"
          />
          <button type="submit" className="btn-primary">
            Enter dashboard
          </button>
        </form>
        {error ? <div className="error-msg">{error}</div> : null}
      </div>
    );
  }

  return (
    <div className="page admin-page">
      <header className="brand-bar">
        <div className="brand-lockup">
          <img className="brand-mark" src="/mantech-m.png" alt="MANTECH" width={42} height={42} />
          <div className="brand-text">
            <span className="brand-name">MANTECH</span>
            <span className="brand-mantra">Always Advancing™</span>
          </div>
        </div>
        <div className="brand-actions">
          <button
            type="button"
            className="brand-link"
            onClick={() => {
              sessionStorage.removeItem(ADMIN_KEY_STORAGE);
              setAdminKey('');
              setDetail(null);
              setExams([]);
            }}
          >
            Sign out
          </button>
          <span className="brand-pill">Admin</span>
        </div>
      </header>

      <h1>Assessment Admin</h1>
      <p className="chooser-lead">
        Create candidate invites, copy their unique exam links, and track status through completion.
      </p>

      <section className="admin-create">
        <h2>Create invite</h2>
        <form className="admin-create-form" onSubmit={handleCreate}>
          <label>
            Name
            <input
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
          </label>
          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
              required
            />
          </label>
          <label>
            Phone (optional)
            <input
              value={form.phone}
              onChange={(event) => setForm((prev) => ({ ...prev, phone: event.target.value }))}
            />
          </label>
          <label>
            Recruiter email (optional)
            <input
              type="email"
              value={form.recruiter_email}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, recruiter_email: event.target.value }))
              }
            />
          </label>
          <label>
            Assessment
            <select
              value={form.assessment}
              onChange={(event) => setForm((prev) => ({ ...prev, assessment: event.target.value }))}
            >
              <option value="ds">Data Scientist</option>
              <option value="de">Data Engineer</option>
            </select>
          </label>
          <button type="submit" className="btn-primary">
            Create &amp; get link
          </button>
        </form>
        {createdUrl ? (
          <div className="admin-link-box">
            <div className="admin-link-label">Candidate link</div>
            <code>{createdUrl}</code>
            <button
              type="button"
              className="brand-link"
              onClick={() => navigator.clipboard?.writeText(createdUrl)}
            >
              Copy
            </button>
          </div>
        ) : null}
      </section>

      <section className="admin-list">
        <div className="admin-list-header">
          <h2>Exam status</h2>
          <div className="admin-filters">
            {[
              ['all', 'All'],
              ['sent', 'Sent'],
              ['opened', 'Opened'],
              ['opened_but_not_completed', 'In progress'],
              ['completed', 'Completed'],
            ].map(([value, label]) => (
              <button
                key={value}
                type="button"
                className={`admin-filter${filter === value ? ' is-active' : ''}`}
                onClick={() => setFilter(value)}
              >
                {label}
              </button>
            ))}
            <button type="button" className="brand-link" onClick={() => loadExams()}>
              Refresh
            </button>
          </div>
        </div>

        {loading ? <p className="status-copy">Loading…</p> : null}
        {error ? <div className="error-msg">{error}</div> : null}

        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Assessment</th>
                <th>Status</th>
                <th>Sent</th>
                <th>Opened</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((exam) => (
                <tr
                  key={exam.id}
                  className={selectedId === exam.id ? 'is-selected' : undefined}
                  onClick={() => openDetail(exam.id)}
                >
                  <td>
                    <div className="admin-candidate-name">{exam.name}</div>
                    <div className="admin-candidate-email">{exam.email}</div>
                  </td>
                  <td>{exam.assessment === 'de' ? 'Data Engineer' : 'Data Scientist'}</td>
                  <td>
                    <span className={`admin-status ${STATUS_CLASS[exam.status] || ''}`}>
                      {exam.status_label}
                    </span>
                  </td>
                  <td>{formatWhen(exam.sent_at)}</td>
                  <td>{formatWhen(exam.opened_at)}</td>
                  <td>{formatWhen(exam.completed_at)}</td>
                </tr>
              ))}
              {!filtered.length && !loading ? (
                <tr>
                  <td colSpan={6}>No exams yet. Create an invite to get started.</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      {detail ? (
        <section className="admin-detail">
          <h2>
            {detail.name}{' '}
            <span className={`admin-status ${STATUS_CLASS[detail.status] || ''}`}>
              {detail.status_label}
            </span>
          </h2>
          <p className="admin-detail-meta">
            {detail.email}
            {detail.phone ? ` · ${detail.phone}` : ''}
            {' · '}
            {detail.assessment === 'de' ? 'Data Engineer' : 'Data Scientist'}
          </p>
          {detail.invite_url ? (
            <div className="admin-link-box">
              <div className="admin-link-label">Invite link</div>
              <code>{detail.invite_url}</code>
            </div>
          ) : null}

          <div className="admin-timing-grid">
            <div>
              <div className="metric-label">Sent</div>
              <div>{formatWhen(detail.sent_at)}</div>
            </div>
            <div>
              <div className="metric-label">Opened</div>
              <div>{formatWhen(detail.opened_at)}</div>
            </div>
            <div>
              <div className="metric-label">Acknowledged</div>
              <div>{formatWhen(detail.acknowledged_at)}</div>
            </div>
            <div>
              <div className="metric-label">Completed</div>
              <div>{formatWhen(detail.completed_at)}</div>
            </div>
          </div>

          {detail.results ? (
            <>
              <div className="metrics">
                <div className="metric">
                  <div className="metric-label">Questions Correct</div>
                  <div className="metric-value">
                    {detail.results.correct_count}/{detail.results.total_questions}
                  </div>
                </div>
                <div className="metric">
                  <div className="metric-label">Total Score</div>
                  <div className="metric-value">
                    {Number(detail.results.score_percentage).toFixed(1)}%
                  </div>
                </div>
              </div>
              <div className="results-table-wrap">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>Question</th>
                      <th>Answer</th>
                      <th>Correct</th>
                      <th>Answered at</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(detail.results.detailed_results || []).map((row) => (
                      <tr key={row.key}>
                        <td className={row.status === 'correct' ? 'status-correct' : 'status-incorrect'}>
                          {row.status === 'correct' ? '✅' : '❌'}
                        </td>
                        <td>{String(row.key || '').replace(/^answer_/, '').replace(/_/g, ' ')}</td>
                        <td>{row.user_answer == null ? '' : String(row.user_answer)}</td>
                        <td>{row.correct_answer == null ? '' : String(row.correct_answer)}</td>
                        <td>{formatWhen(row.answered_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="status-copy">No scored results yet for this candidate.</p>
          )}
        </section>
      ) : null}
    </div>
  );
}
