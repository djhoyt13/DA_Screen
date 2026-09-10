import { useEffect, useMemo, useState } from 'react';
import {
  ApiError,
  fetchInvite,
  fetchQuestions,
  getApiBase,
  markInviteAcknowledged,
  markInviteOpened,
  submitQuiz,
  updateInviteCandidate,
} from './api.js';
import { collectQuestionKeys, getTotalQuestions } from './progress.js';
import { readInviteTokenFromUrl } from './routing.js';
import { nowIso } from './timing.js';
import {
  countAnswered,
  inlineFieldError,
  validateSubmission,
} from './validation.js';
import CandidateForm from './components/CandidateForm.jsx';
import ProgressBar from './components/ProgressBar.jsx';
import QuestionSection from './components/QuestionSection.jsx';
import Results from './components/Results.jsx';

const EMPTY_CANDIDATE = {
  name: '',
  email: '',
  phone: '',
  recruiter_email: '',
};

const ROLE_COPY = {
  ds: {
    fallbackTitle: 'Data Scientist Technical Review',
    role: 'Data Scientist',
    domain: 'Data Science',
  },
  de: {
    fallbackTitle: 'Data Engineer Technical Review',
    role: 'Data Engineer',
    domain: 'Data Engineering',
  },
};

function fieldMessagesFromApi(error) {
  const messages = [];
  if (error?.fields && typeof error.fields === 'object') {
    for (const value of Object.values(error.fields)) {
      if (value) {
        messages.push(String(value));
      }
    }
  }
  if (error?.message && !messages.includes(error.message)) {
    const generic = /^Submit failed/i.test(error.message);
    if (!generic || messages.length === 0) {
      messages.push(error.message);
    }
  }
  return messages.length ? messages : ['Submit failed. Please try again.'];
}

export default function App({ assessmentId = 'ds', onChangeAssessment }) {
  const inviteToken = readInviteTokenFromUrl();
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [candidate, setCandidate] = useState(EMPTY_CANDIDATE);
  const [fieldErrors, setFieldErrors] = useState({});
  const [answers, setAnswers] = useState({});
  const [answerTimestamps, setAnswerTimestamps] = useState({});
  const [openedAt, setOpenedAt] = useState(null);
  const [acknowledgedAt, setAcknowledgedAt] = useState(null);
  const [submitErrors, setSubmitErrors] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [statementAcknowledged, setStatementAcknowledged] = useState(false);
  const [inviteCompleted, setInviteCompleted] = useState(false);

  const roleCopy = ROLE_COPY[assessmentId] || ROLE_COPY.ds;

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setLoadError('');
      setQuiz(null);
      setAnswers({});
      setAnswerTimestamps({});
      setOpenedAt(null);
      setAcknowledgedAt(null);
      setSubmitted(false);
      setResults(null);
      setStatementAcknowledged(false);
      setSubmitErrors([]);
      setInviteCompleted(false);
      setCandidate(EMPTY_CANDIDATE);
      try {
        if (inviteToken) {
          const invite = await fetchInvite(inviteToken);
          if (cancelled) return;
          if (invite.assessment && invite.assessment !== assessmentId) {
            setLoadError(
              `This invite is for the ${
                invite.assessment === 'de' ? 'Data Engineer' : 'Data Scientist'
              } assessment. Open the correct link.`
            );
            setLoading(false);
            return;
          }
          if (invite.completed) {
            setInviteCompleted(true);
          }
          setCandidate({
            name: invite.name || '',
            email: invite.email || '',
            phone: invite.phone || '',
            recruiter_email: invite.recruiter_email || '',
          });
        }

        const data = await fetchQuestions(assessmentId);
        if (!cancelled) {
          const opened = nowIso();
          setQuiz(data);
          setOpenedAt(opened);
          document.title = data?.title
            ? String(data.title).replace('Technical Review', 'Initial Assessment')
            : roleCopy.fallbackTitle.replace('Technical Review', 'Initial Assessment');
          if (inviteToken) {
            try {
              await markInviteOpened(inviteToken, opened);
            } catch {
              // Non-blocking: candidate can still take the exam.
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          const fallback = `Unable to load questions. Please check that the API is running at ${getApiBase() || window.location.origin}.`;
          setLoadError(err instanceof ApiError ? err.message || fallback : fallback);
          setQuiz(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [assessmentId, inviteToken, roleCopy.fallbackTitle]);

  const questionKeys = useMemo(() => collectQuestionKeys(quiz), [quiz]);
  const totalQuestions = getTotalQuestions(quiz, questionKeys);
  const answeredCount = countAnswered(answers, questionKeys);
  const locked = submitted || submitting || inviteCompleted;
  const assessmentOpen = statementAcknowledged && !locked;

  function handleCandidateChange(field, value) {
    if (inviteToken && field === 'recruiter_email') {
      return;
    }
    setCandidate((prev) => ({ ...prev, [field]: value }));
    setFieldErrors((prev) => ({ ...prev, [field]: inlineFieldError(field, value) }));
  }

  async function handleSaveInviteField(field, value) {
    if (!inviteToken) {
      return;
    }
    const data = await updateInviteCandidate(inviteToken, { [field]: value });
    setCandidate((prev) => ({
      ...prev,
      name: data.name ?? (field === 'name' ? value : prev.name),
      email: data.email ?? (field === 'email' ? value : prev.email),
      phone: data.phone ?? (field === 'phone' ? value : prev.phone),
      recruiter_email: data.recruiter_email ?? prev.recruiter_email,
    }));
    setFieldErrors((prev) => ({ ...prev, [field]: '' }));
  }

  function handleAnswer(key, value) {
    const stamped = nowIso();
    setAnswers((prev) => ({ ...prev, [key]: value }));
    setAnswerTimestamps((prev) => ({ ...prev, [key]: stamped }));
  }

  async function handleSubmit() {
    if (submitted || submitting || inviteCompleted) {
      return;
    }
    if (!statementAcknowledged) {
      setSubmitErrors(['Please confirm that you have read the welcome statement before continuing.']);
      return;
    }
    const clientErrors = validateSubmission(candidate, answers, questionKeys);
    setSubmitErrors(clientErrors);
    if (clientErrors.length) {
      return;
    }

    const submittedAt = nowIso();
    setSubmitting(true);
    try {
      const payload = {
        assessment: assessmentId,
        name: candidate.name.trim(),
        email: candidate.email.trim(),
        phone: candidate.phone.trim(),
        recruiter_email: candidate.recruiter_email.trim(),
        answers,
        timing: {
          opened_at: openedAt,
          acknowledged_at: acknowledgedAt,
          submitted_at: submittedAt,
          answers: answerTimestamps,
        },
      };
      if (inviteToken) {
        payload.invite_token = inviteToken;
      }
      const data = await submitQuiz(payload);
      setResults(data);
      setSubmitted(true);
      setSubmitErrors([]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setSubmitErrors(fieldMessagesFromApi(err));
      } else if (err instanceof ApiError) {
        setSubmitErrors([err.message]);
      } else {
        setSubmitErrors([
          `Unable to submit. Please check that the API is running at ${getApiBase() || window.location.origin}.`,
        ]);
      }
    } finally {
      setSubmitting(false);
    }
  }

  const title = quiz?.title || roleCopy.fallbackTitle;

  return (
    <div className="page">
      <header className="brand-bar">
        <div className="brand-lockup">
          <img
            className="brand-mark"
            src="/mantech-m.png"
            alt="MANTECH"
            width={42}
            height={42}
          />
          <div className="brand-text">
            <span className="brand-name">MANTECH</span>
            <span className="brand-mantra">Always Advancing™</span>
          </div>
        </div>
        <div className="brand-actions">
          {typeof onChangeAssessment === 'function' && !inviteToken ? (
            <button type="button" className="brand-link" onClick={onChangeAssessment}>
              Change assessment
            </button>
          ) : null}
          <span className="brand-pill">Initial Assessment</span>
        </div>
      </header>

      <h1>{title}</h1>
      <ProgressBar answered={answeredCount} total={totalQuestions} />

      {inviteCompleted ? (
        <div className="success-msg">
          This invite has already been completed. Contact your recruiter if you need a new link.
        </div>
      ) : null}

      <div className="welcome-msg">
        Welcome to the {roleCopy.role} technical review. The results of this review are
        only one data point in our team&apos;s hiring decision. This is{' '}
        <strong>
          <u>NOT</u>
        </strong>{' '}
        a pass/fail exam; it is used to assess your current strengths and areas for
        improvement in the domains of {roleCopy.domain} that are relevant to our
        organization.
      </div>

      <label className={`ack-check${statementAcknowledged ? ' is-checked' : ''}`}>
        <input
          type="checkbox"
          checked={statementAcknowledged}
          disabled={locked}
          onChange={(event) => {
            const checked = event.target.checked;
            setStatementAcknowledged(checked);
            const stamped = checked ? nowIso() : null;
            setAcknowledgedAt(stamped);
            if (checked) {
              setSubmitErrors((prev) =>
                prev.filter(
                  (message) =>
                    message !==
                    'Please confirm that you have read the welcome statement before continuing.',
                ),
              );
              if (inviteToken) {
                markInviteAcknowledged(inviteToken, stamped).catch(() => {});
              }
            }
          }}
        />
        <span className="ack-box" aria-hidden="true" />
        <span className="ack-label">I have read the above statement</span>
      </label>

      {!statementAcknowledged && !submitted && !inviteCompleted ? (
        <p className="ack-hint">Check the box above to begin the assessment.</p>
      ) : null}

      {inviteToken ? (
        <CandidateForm
          values={candidate}
          errors={fieldErrors}
          onChange={handleCandidateChange}
          disabled={false}
          examLocked={locked}
          inviteMode
          onSaveInviteField={handleSaveInviteField}
        />
      ) : null}

      <div
        className={
          !statementAcknowledged && !submitted && !inviteCompleted ? 'assessment-gated' : undefined
        }
      >
        {!inviteToken ? (
          <CandidateForm
            values={candidate}
            errors={fieldErrors}
            onChange={handleCandidateChange}
            disabled={!assessmentOpen}
            examLocked={locked}
            inviteMode={false}
          />
        ) : null}

        {loading ? <p className="status-copy">Loading questions…</p> : null}
        {loadError ? <div className="error-msg">{loadError}</div> : null}

        {quiz
          ? (quiz.sections || []).map((section) => (
              <QuestionSection
                key={section.name}
                section={section}
                answers={answers}
                onAnswer={handleAnswer}
                disabled={!assessmentOpen}
              />
            ))
          : null}

        {quiz ? <hr className="submit-divider" /> : null}

        {quiz && !submitted && !inviteCompleted ? (
          <button
            type="button"
            className="btn-primary"
            onClick={handleSubmit}
            disabled={!statementAcknowledged || submitting}
          >
            {submitting ? 'Submitting…' : 'Submit Answers'}
          </button>
        ) : null}
      </div>

      {submitted ? (
        <div className="success-msg">Thank you! Your quiz has been submitted.</div>
      ) : null}

      {submitErrors.map((message) => (
        <div key={message} className="error-msg">
          {message}
        </div>
      ))}

      {results?.email_warning ? (
        <div className="warning-msg">{results.email_warning}</div>
      ) : null}

      {submitted && results ? <Results results={results} /> : null}
    </div>
  );
}
