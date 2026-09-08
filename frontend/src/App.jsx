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

export default function App() {
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

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setLoadError('');
      try {
        const data = await fetchQuestions();
        if (!cancelled) {
          setQuiz(data);
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
  }, []);

  const questionKeys = useMemo(() => collectQuestionKeys(quiz), [quiz]);
  const totalQuestions = getTotalQuestions(quiz, questionKeys);
  const answeredCount = countAnswered(answers, questionKeys);
  const locked = submitted || submitting;

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
    const clientErrors = validateSubmission(candidate, answers, questionKeys);
    setSubmitErrors(clientErrors);
    if (clientErrors.length) {
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
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

  const title = quiz?.title || 'Data Scientist Technical Review';

  return (
    <div className="page">
      <h1>{title}</h1>
      <ProgressBar answered={answeredCount} total={totalQuestions} />

      <div className="welcome-msg">
        Welcome to the Data Scientist technical review. The results of this review are
        only one data point in our team&apos;s hiring decision. This is{' '}
        <strong>
          <u>NOT</u>
        </strong>{' '}
        a pass/fail exam; it is used to assess your current strengths and areas for
        improvement in the domains of Data Science that are relevant to our
        organization.
      </div>

      <CandidateForm
        values={candidate}
        errors={fieldErrors}
        onChange={handleCandidateChange}
        disabled={locked}
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
              disabled={locked}
            />
          ))
        : null}

      {quiz ? <hr className="submit-divider" /> : null}

      {quiz && !submitted ? (
        <button
          type="button"
          className="btn-primary"
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Submitting…' : 'Submit Answers'}
        </button>
      ) : null}

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
