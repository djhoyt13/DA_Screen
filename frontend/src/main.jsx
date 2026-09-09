import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import AssessmentChooser from './components/AssessmentChooser.jsx';
import {
  navigateToAssessment,
  pathForAssessment,
  readAssessmentFromUrl,
} from './routing.js';
import './styles.css';

function Root() {
  const [assessmentId, setAssessmentId] = useState(() => readAssessmentFromUrl());

  useEffect(() => {
    // Canonicalize legacy ?assessment= query links to path URLs.
    const current = readAssessmentFromUrl();
    if (current) {
      const canonical = pathForAssessment(current);
      if (window.location.pathname.replace(/\/+$/, '') !== canonical) {
        navigateToAssessment(current, { replace: true });
      }
    }

    function onPopState() {
      setAssessmentId(readAssessmentFromUrl());
    }
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  function selectAssessment(id) {
    navigateToAssessment(id);
    setAssessmentId(id);
  }

  function clearAssessment() {
    navigateToAssessment(null);
    setAssessmentId(null);
  }

  if (!assessmentId) {
    return <AssessmentChooser onSelect={selectAssessment} />;
  }

  return (
    <App
      assessmentId={assessmentId}
      onChangeAssessment={clearAssessment}
    />
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
