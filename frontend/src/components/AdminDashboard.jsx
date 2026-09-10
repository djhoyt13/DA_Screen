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

const STATUS_FILTER_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'sent', label: 'Sent' },
  { value: 'opened', label: 'Opened' },
  { value: 'opened_but_not_completed', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
];

const ASSESSMENT_FILTER_OPTIONS = [
  { value: '', label: 'All assessments' },
  { value: 'ds', label: 'Data Scientist' },
  { value: 'de', label: 'Data Engineer' },
];

const EMPTY_COLUMN_FILTERS = {
  assessment: '',
  status: '',
};

const DEFAULT_SORT = { key: 'sent', dir: 'desc' };

const TABLE_COLUMNS = [
  { key: 'candidate', label: 'Candidate', mode: 'sort' },
  { key: 'assessment', label: 'Assessment', mode: 'filter', filter: 'assessment' },
  { key: 'status', label: 'Status', mode: 'filter', filter: 'status' },
  { key: 'sent', label: 'Sent', mode: 'sort' },
  { key: 'opened', label: 'Opened', mode: 'sort' },
  { key: 'completed', label: 'Completed', mode: 'sort' },
  { key: 'score', label: 'Score', mode: 'sort' },
];

function formatWhen(value) {
  if (!value) return '—';
  return String(value).replace('T', ' ').slice(0, 19);
}

function assessmentLabel(assessment) {
  return assessment === 'de' ? 'Data Engineer' : 'Data Scientist';
}

function formatScore(value) {
  if (value == null || value === '') return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return '—';
  return `${num.toFixed(1)}%`;
}

function examRowKey(exam) {
  return exam.row_id || (exam.id != null ? String(exam.id) : '');
}

function sortValue(exam, key) {
  switch (key) {
    case 'candidate':
      return `${exam.name || ''} ${exam.email || ''}`.trim().toLowerCase();
    case 'assessment':
      return assessmentLabel(exam.assessment).toLowerCase();
    case 'status':
      return (exam.status_label || exam.status || '').toLowerCase();
    case 'sent':
      return exam.sent_at || '';
    case 'opened':
      return exam.opened_at || '';
    case 'completed':
      return exam.completed_at || '';
    case 'score':
      return exam.score_percentage == null || exam.score_percentage === ''
        ? null
        : Number(exam.score_percentage);
    default:
      return '';
  }
}

function compareSortValues(aVal, bVal, dir) {
  const aEmpty = aVal == null || aVal === '';
  const bEmpty = bVal == null || bVal === '';
  if (aEmpty && bEmpty) return 0;
  if (aEmpty) return 1;
  if (bEmpty) return -1;
  if (typeof aVal === 'number' && typeof bVal === 'number') {
    return dir === 'asc' ? aVal - bVal : bVal - aVal;
  }
  const aStr = String(aVal);
  const bStr = String(bVal);
  if (aStr < bStr) return dir === 'asc' ? -1 : 1;
  if (aStr > bStr) return dir === 'asc' ? 1 : -1;
  return 0;
}

export default function AdminDashboard() {
  const [adminKey, setAdminKey] = useState(() => sessionStorage.getItem(ADMIN_KEY_STORAGE) || '');
  const [keyInput, setKeyInput] = useState(adminKey);
  const [exams, setExams] = useState([]);
  const [selectedKey, setSelectedKey] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createError, setCreateError] = useState('');
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    recruiter_email: '',
    assessment: 'ds',
  });
  const [createdUrl, setCreatedUrl] = useState('');
  const [emailOutcome, setEmailOutcome] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  const [columnFilters, setColumnFilters] = useState(EMPTY_COLUMN_FILTERS);
  const [sort, setSort] = useState(DEFAULT_SORT);

  const filtersActive = useMemo(
    () =>
      Object.values(columnFilters).some((value) => value !== '') ||
      sort.key !== DEFAULT_SORT.key ||
      sort.dir !== DEFAULT_SORT.dir,
    [columnFilters, sort]
  );

  const filtered = useMemo(() => {
    const rows = exams.filter((exam) => {
      if (columnFilters.assessment && exam.assessment !== columnFilters.assessment) {
        return false;
      }
      if (columnFilters.status && exam.status !== columnFilters.status) {
        return false;
      }
      return true;
    });

    return [...rows].sort((a, b) => {
      const primary = compareSortValues(sortValue(a, sort.key), sortValue(b, sort.key), sort.dir);
      if (primary !== 0) return primary;
      return (b.id || 0) - (a.id || 0);
    });
  }, [exams, columnFilters, sort]);

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
    setCreateError('');
    setFormErrors({});
    setCreatedUrl('');
    setEmailOutcome(null);
    try {
      const created = await adminCreateExam(adminKey, form);
      setCreatedUrl(created.invite_url || '');
      setEmailOutcome({
        email_sent: Boolean(created.email_sent),
        email_warning: created.email_warning || '',
      });
      setForm({
        name: '',
        email: '',
        phone: '',
        recruiter_email: '',
        assessment: form.assessment,
      });
      await loadExams();
      const detailKey = created.row_id || String(created.id);
      setSelectedKey(detailKey);
      const detailData = await adminExamDetail(adminKey, detailKey);
      setDetail(detailData);
    } catch (err) {
      if (err instanceof ApiError) {
        const fields =
          err.fields && typeof err.fields === 'object' ? { ...err.fields } : {};
        setFormErrors(fields);
        const fieldMessages = Object.values(fields).filter(Boolean).map(String);
        const message =
          fieldMessages.length > 0
            ? fieldMessages.join(' ')
            : err.message || 'Failed to send assessment';
        setCreateError(message);
      } else {
        setCreateError('Failed to send assessment');
      }
    }
  }

  async function openDetail(rowKey) {
    setSelectedKey(rowKey);
    setError('');
    try {
      const data = await adminExamDetail(adminKey, rowKey);
      setDetail(data);
    } catch (err) {
      setDetail(null);
      setError(err instanceof ApiError ? err.message : 'Failed to load detail');
    }
  }

  function updateColumnFilter(key, value) {
    setColumnFilters((prev) => ({ ...prev, [key]: value }));
  }

  function toggleSort(key) {
    setSort((prev) => {
      if (prev.key === key) {
        return { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' };
      }
      return { key, dir: key === 'candidate' ? 'asc' : 'desc' };
    });
  }

  function clearTableControls() {
    setColumnFilters(EMPTY_COLUMN_FILTERS);
    setSort(DEFAULT_SORT);
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
              setSelectedKey(null);
              setColumnFilters(EMPTY_COLUMN_FILTERS);
              setSort(DEFAULT_SORT);
            }}
          >
            Sign out
          </button>
          <span className="brand-pill">Admin</span>
        </div>
      </header>

      <h1>Assessment Admin</h1>
      <p className="chooser-lead">
        Send an assessment to a candidate, then track status through completion.
      </p>

      <section className="admin-create">
        <h2>Send assessment</h2>
        <p className="admin-create-lead">
          Enter the candidate&apos;s details and choose an assessment. We create their invite and
          email them the link.
        </p>
        <form className="admin-create-form" onSubmit={handleCreate}>
          <label className={formErrors.name ? 'has-field-error' : undefined}>
            Candidate name
            <input
              value={form.name}
              onChange={(event) => {
                setForm((prev) => ({ ...prev, name: event.target.value }));
                setFormErrors((prev) => ({ ...prev, name: undefined }));
              }}
              required
            />
            {formErrors.name ? <span className="field-error">{formErrors.name}</span> : null}
          </label>
          <label className={formErrors.email ? 'has-field-error' : undefined}>
            Candidate email
            <input
              type="email"
              value={form.email}
              onChange={(event) => {
                setForm((prev) => ({ ...prev, email: event.target.value }));
                setFormErrors((prev) => ({ ...prev, email: undefined }));
              }}
              required
            />
            {formErrors.email ? <span className="field-error">{formErrors.email}</span> : null}
          </label>
          <label className={formErrors.phone ? 'has-field-error' : undefined}>
            Candidate phone
            <input
              type="tel"
              value={form.phone}
              onChange={(event) => {
                setForm((prev) => ({ ...prev, phone: event.target.value }));
                setFormErrors((prev) => ({ ...prev, phone: undefined }));
              }}
              required
            />
            {formErrors.phone ? <span className="field-error">{formErrors.phone}</span> : null}
          </label>
          <label className={formErrors.assessment ? 'has-field-error' : undefined}>
            Assessment
            <select
              value={form.assessment}
              onChange={(event) => {
                setForm((prev) => ({ ...prev, assessment: event.target.value }));
                setFormErrors((prev) => ({ ...prev, assessment: undefined }));
              }}
              required
            >
              <option value="ds">Data Scientist</option>
              <option value="de">Data Engineer</option>
            </select>
            {formErrors.assessment ? (
              <span className="field-error">{formErrors.assessment}</span>
            ) : null}
          </label>
          <label className={formErrors.recruiter_email ? 'has-field-error' : undefined}>
            Recruiter email
            <input
              type="email"
              value={form.recruiter_email}
              onChange={(event) => {
                setForm((prev) => ({ ...prev, recruiter_email: event.target.value }));
                setFormErrors((prev) => ({ ...prev, recruiter_email: undefined }));
              }}
              required
            />
            {formErrors.recruiter_email ? (
              <span className="field-error">{formErrors.recruiter_email}</span>
            ) : null}
          </label>
          <button type="submit" className="btn-primary">
            Send assessment
          </button>
        </form>
        {createError ? <div className="error-msg">{createError}</div> : null}
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
            {emailOutcome?.email_sent ? (
              <div className="success-msg admin-email-status">
                Assessment email sent to the candidate.
              </div>
            ) : (
              <div className="warning-msg admin-email-status">
                {emailOutcome?.email_warning ||
                  'Email could not be sent. The invite link above still works — share it with the candidate manually.'}
              </div>
            )}
          </div>
        ) : null}
      </section>

      <section className="admin-list">
        <div className="admin-list-header">
          <h2>Exam status</h2>
          <div className="admin-filters">
            {filtersActive ? (
              <button type="button" className="brand-link" onClick={clearTableControls}>
                Clear filters
              </button>
            ) : null}
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
                {TABLE_COLUMNS.map((column) => {
                  if (column.mode === 'sort') {
                    const isActive = sort.key === column.key;
                    return (
                      <th key={column.key}>
                        <button
                          type="button"
                          className={`admin-sort-btn${isActive ? ' is-active' : ''}`}
                          onClick={() => toggleSort(column.key)}
                          aria-label={`Sort by ${column.label}`}
                        >
                          <span>{column.label}</span>
                          <span className="admin-sort-indicator" aria-hidden="true">
                            {isActive ? (sort.dir === 'asc' ? '▲' : '▼') : '↕'}
                          </span>
                        </button>
                      </th>
                    );
                  }
                  return <th key={column.key}>{column.label}</th>;
                })}
              </tr>
              <tr className="admin-filter-row">
                {TABLE_COLUMNS.map((column) => {
                  if (column.filter === 'assessment') {
                    return (
                      <th key={`${column.key}-filter`}>
                        <select
                          className="admin-col-filter"
                          aria-label="Filter assessment"
                          value={columnFilters.assessment}
                          onChange={(event) =>
                            updateColumnFilter('assessment', event.target.value)
                          }
                        >
                          {ASSESSMENT_FILTER_OPTIONS.map((option) => (
                            <option key={option.value || 'all'} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </th>
                    );
                  }
                  if (column.filter === 'status') {
                    return (
                      <th key={`${column.key}-filter`}>
                        <select
                          className="admin-col-filter"
                          aria-label="Filter status"
                          value={columnFilters.status}
                          onChange={(event) => updateColumnFilter('status', event.target.value)}
                        >
                          {STATUS_FILTER_OPTIONS.map((option) => (
                            <option key={option.value || 'all'} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </th>
                    );
                  }
                  return <th key={`${column.key}-filter`} className="admin-filter-spacer" />;
                })}
              </tr>
            </thead>
            <tbody>
              {filtered.map((exam) => {
                const rowKey = examRowKey(exam);
                return (
                  <tr
                    key={rowKey}
                    className={selectedKey === rowKey ? 'is-selected' : undefined}
                    onClick={() => openDetail(rowKey)}
                  >
                    <td>
                      <div className="admin-candidate-name">{exam.name}</div>
                      <div className="admin-candidate-email">{exam.email}</div>
                      {exam.phone ? (
                        <div className="admin-candidate-phone">{exam.phone}</div>
                      ) : null}
                    </td>
                    <td>{assessmentLabel(exam.assessment)}</td>
                    <td>
                      <span className={`admin-status ${STATUS_CLASS[exam.status] || ''}`}>
                        {exam.status_label}
                      </span>
                    </td>
                    <td>{formatWhen(exam.sent_at)}</td>
                    <td>{formatWhen(exam.opened_at)}</td>
                    <td>{formatWhen(exam.completed_at)}</td>
                    <td>{formatScore(exam.score_percentage)}</td>
                  </tr>
                );
              })}
              {!filtered.length && !loading ? (
                <tr>
                  <td colSpan={7}>
                    {exams.length && filtersActive
                      ? 'No exams match the current filters.'
                      : 'No exams yet. Create an invite or wait for past submissions to appear.'}
                  </td>
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
            {assessmentLabel(detail.assessment)}
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
