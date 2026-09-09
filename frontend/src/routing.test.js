import { describe, expect, it } from 'vitest';
import {
  ASSESSMENT_PATHS,
  pathForAssessment,
  readAssessmentFromUrl,
} from './routing.js';

describe('assessment routing', () => {
  it('maps assessment ids to shareable paths', () => {
    expect(pathForAssessment('ds')).toBe('/data-scientist');
    expect(pathForAssessment('de')).toBe('/data-engineer');
    expect(ASSESSMENT_PATHS.ds).toBe('/data-scientist');
  });

  it('reads assessment ids from path aliases', () => {
    expect(readAssessmentFromUrl({ pathname: '/data-scientist', search: '' })).toBe('ds');
    expect(readAssessmentFromUrl({ pathname: '/ds/', search: '' })).toBe('ds');
    expect(readAssessmentFromUrl({ pathname: '/data-engineer', search: '' })).toBe('de');
    expect(readAssessmentFromUrl({ pathname: '/de', search: '' })).toBe('de');
    expect(readAssessmentFromUrl({ pathname: '/', search: '' })).toBe(null);
  });

  it('supports legacy query links', () => {
    expect(readAssessmentFromUrl({ pathname: '/', search: '?assessment=de' })).toBe('de');
    expect(readAssessmentFromUrl({ pathname: '/', search: '?assessment=ds' })).toBe('ds');
  });
});
