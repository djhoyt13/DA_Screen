import { ASSESSMENT_PATHS } from '../routing.js';

export default function AssessmentChooser({ onSelect, loadError }) {
  function handleSelect(event, id) {
    event.preventDefault();
    onSelect(id);
  }

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
        <span className="brand-pill">Initial Assessment</span>
      </header>

      <h1>Technical Initial Assessments</h1>
      <p className="chooser-lead">
        Choose the assessment that matches the role you are screening for. Each review
        uses the same format: candidate info, self-paced questions, auto-grading,
        and a recruiter results email.
      </p>

      <div className="chooser-grid">
        <a
          className="chooser-card"
          href={ASSESSMENT_PATHS.ds}
          onClick={(event) => handleSelect(event, 'ds')}
        >
          <span className="chooser-kicker">Role track</span>
          <span className="chooser-title">Data Scientist</span>
          <span className="chooser-copy">
            Python, ML concepts, probability, tooling, and agent protocols — 20 questions.
          </span>
          <span className="chooser-url">{ASSESSMENT_PATHS.ds}</span>
        </a>
        <a
          className="chooser-card"
          href={ASSESSMENT_PATHS.de}
          onClick={(event) => handleSelect(event, 'de')}
        >
          <span className="chooser-kicker">Role track</span>
          <span className="chooser-title">Data Engineer</span>
          <span className="chooser-copy">
            SQL, modeling, pipelines, Spark, Airflow, Kafka, and data quality — 16 questions.
          </span>
          <span className="chooser-url">{ASSESSMENT_PATHS.de}</span>
        </a>
      </div>

      {loadError ? <div className="error-msg">{loadError}</div> : null}

      <p className="chooser-lead" style={{ marginTop: '2rem' }}>
        Administrators:{' '}
        <a className="brand-link" href="/admin">
          Open exam dashboard
        </a>
      </p>
    </div>
  );
}
