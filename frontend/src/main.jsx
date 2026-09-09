import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import AdminDashboard from './components/AdminDashboard.jsx';
import AssessmentChooser from './components/AssessmentChooser.jsx';
import {
  isAdminPath,
  navigateToAssessment,
  pathForAssessment,
  readAssessmentFromUrl,
  readInviteTokenFromUrl,
} from './routing.js';
import './styles.css';

function Root() {
  const [isAdmin, setIsAdmin] = useState(() => isAdminPath());
  const [assessmentId, setAssessmentId] = useState(() =>
    isAdminPath() ? null : readAssessmentFromUrl()
  );

  useEffect(() => {
    function syncFromLocation() {
      if (isAdminPath()) {
        setIsAdmin(true);
        setAssessmentId(null);
        return;
      }
      setIsAdmin(false);
      const current = readAssessmentFromUrl();
      const invite = readInviteTokenFromUrl();
      if (current) {
        const canonical = pathForAssessment(current);
        const desired = invite ? `${canonical}?invite=${encodeURIComponent(invite)}` : canonical;
        const currentFull = `${window.location.pathname}${window.location.search}`;
        if (currentFull.replace(/\/+$/, '') !== desired && window.location.pathname.replace(/\/+$/, '') !== canonical) {
          navigateToAssessment(current, { replace: true, inviteToken: invite });
        } else if (!invite && window.location.pathname.replace(/\/+$/, '') !== canonical) {
          navigateToAssessment(current, { replace: true });
        }
      }
      setAssessmentId(current);
    }

    syncFromLocation();
    window.addEventListener('popstate', syncFromLocation);
    return () => window.removeEventListener('popstate', syncFromLocation);
  }, []);

  function selectAssessment(id) {
    navigateToAssessment(id);
    setAssessmentId(id);
  }

  function clearAssessment() {
    navigateToAssessment(null);
    setAssessmentId(null);
  }

  if (isAdmin) {
    return <AdminDashboard />;
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
