import { useEffect, useMemo, useState } from 'react';
import { ApiError, fetchQuestions, getApiBase, submitQuiz } from './api.js';
import { collectQuestionKeys, getTotalQuestions } from './progress.js';
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
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [candidate, setCandidate] = useState(EMPTY_CANDIDATE);
  const [fieldErrors, setFieldErrors] = useState({});
  const [answers, setAnswers] = useState({});
  const [submitErrors, setSubmitErrors] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [statementAcknowledged, setStatementAcknowledged] = useState(false);

  const roleCopy = ROLE_COPY[assessmentId] || ROLE_COPY.ds;

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setLoadError('');
      setQuiz(null);
      setAnswers({});
      setSubmitted(false);
      setResults(null);
      setStatementAcknowledged(false);
      setSubmitErrors([]);
      try {
        const data = await fetchQuestions(assessmentId);
        if (!cancelled) {
          setQuiz(data);
          document.title = data?.title
            ? String(data.title).replace('Technical Review', 'Initial Assessment')
            : roleCopy.fallbackTitle.replace('Technical Review', 'Initial Assessment');
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
  }, [assessmentId, roleCopy.fallbackTitle]);

  const questionKeys = useMemo(() => collectQuestionKeys(quiz), [quiz]);
  const totalQuestions = getTotalQuestions(quiz, questionKeys);
  const answeredCount = countAnswered(answers, questionKeys);
  const locked = submitted || submitting;
  const assessmentOpen = statementAcknowledged && !locked;

  function handleCandidateChange(field, value) {
    setCandidate((prev) => ({ ...prev, [field]: value }));
    setFieldErrors((prev) => ({ ...prev, [field]: inlineFieldError(field, value) }));
  }

  function handleAnswer(key, value) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit() {
    if (submitted || submitting) {
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

    setSubmitting(true);
    try {
      const payload = {
        assessment: assessmentId,
        name: candidate.name.trim(),
        email: candidate.email.trim(),
        phone: candidate.phone.trim(),
        recruiter_email: candidate.recruiter_email.trim(),
        answers,
      };
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
          {typeof onChangeAssessment === 'function' ? (
            <button type="button" className="brand-link" onClick={onChangeAssessment}>
              Change assessment
            </button>
          ) : null}
          <span className="brand-pill">Initial Assessment</span>
        </div>
      </header>

      <h1>{title}</h1>
      <ProgressBar answered={answeredCount} total={totalQuestions} />

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
            setStatementAcknowledged(event.target.checked);
            if (event.target.checked) {
              setSubmitErrors((prev) =>
                prev.filter(
                  (message) =>
                    message !==
                    'Please confirm that you have read the welcome statement before continuing.',
                ),
              );
            }
          }}
        />
        <span className="ack-box" aria-hidden="true" />
        <span className="ack-label">I have read the above statement</span>
      </label>

      {!statementAcknowledged && !submitted ? (
        <p className="ack-hint">Check the box above to begin the assessment.</p>
      ) : null}

      <div className={!statementAcknowledged && !submitted ? 'assessment-gated' : undefined}>
        <CandidateForm
          values={candidate}
          errors={fieldErrors}
          onChange={handleCandidateChange}
          disabled={!assessmentOpen}
        />

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

        {quiz && !submitted ? (
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
