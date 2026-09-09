/** Map browser path ↔ assessment id for shareable candidate links. */

export const ASSESSMENT_PATHS = {
  ds: '/data-scientist',
  de: '/data-engineer',
};

const PATH_ALIASES = {
  'data-scientist': 'ds',
  ds: 'ds',
  'data-engineer': 'de',
  de: 'de',
};

export function pathForAssessment(assessmentId) {
  return ASSESSMENT_PATHS[assessmentId] || '/';
}

export function readAssessmentFromUrl(location = window.location) {
  const path = (location.pathname || '/').replace(/\/+$/, '') || '/';
  const segment = path.split('/').filter(Boolean)[0]?.toLowerCase();
  if (segment && PATH_ALIASES[segment]) {
    return PATH_ALIASES[segment];
  }

  // Back-compat for older emailed query links: ?assessment=ds|de
  const params = new URLSearchParams(location.search);
  const queryValue = (params.get('assessment') || '').toLowerCase();
  if (PATH_ALIASES[queryValue]) {
    return PATH_ALIASES[queryValue];
  }
  return null;
}

export function navigateToAssessment(assessmentId, { replace = false } = {}) {
  const path = assessmentId ? pathForAssessment(assessmentId) : '/';
  const method = replace ? 'replaceState' : 'pushState';
  window.history[method]({}, '', path);
}
