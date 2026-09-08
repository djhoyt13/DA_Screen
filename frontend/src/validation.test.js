import { describe, expect, it } from 'vitest';
import {
  allQuestionsAnswered,
  countAnswered,
  inlineFieldError,
  isValidEmail,
  isValidName,
  isValidPhone,
  MESSAGES,
  validateSubmission,
} from './validation.js';

describe('name validation', () => {
  it('accepts letters, spaces, hyphens, and apostrophes', () => {
    expect(isValidName("Jane Doe")).toBe(true);
    expect(isValidName("O'Neil")).toBe(true);
    expect(isValidName('Anne-Marie')).toBe(true);
  });

  it('rejects empty or numeric names', () => {
    expect(isValidName('')).toBe(false);
    expect(isValidName('Jane2')).toBe(false);
  });
});

describe('email validation', () => {
  it('accepts a standard email', () => {
    expect(isValidEmail('jane@example.com')).toBe(true);
  });

  it('rejects missing or malformed emails', () => {
    expect(isValidEmail('')).toBe(false);
    expect(isValidEmail('jane@')).toBe(false);
    expect(isValidEmail('not-an-email')).toBe(false);
  });
});

describe('phone validation', () => {
  it('strips separators and accepts 10-14 digits', () => {
    expect(isValidPhone('5551234567')).toBe(true);
    expect(isValidPhone('(555) 123-4567')).toBe(true);
    expect(isValidPhone('+1 555 123 4567')).toBe(true);
  });

  it('rejects too-short numbers', () => {
    expect(isValidPhone('5551234')).toBe(false);
    expect(isValidPhone('')).toBe(false);
  });
});

describe('inline field errors', () => {
  it('is silent when the field is empty', () => {
    expect(inlineFieldError('name', '')).toBe('');
    expect(inlineFieldError('email', '')).toBe('');
  });

  it('returns Streamlit wording for invalid values', () => {
    expect(inlineFieldError('name', 'Jane2')).toBe(MESSAGES.nameInvalid);
    expect(inlineFieldError('email', 'nope')).toBe(MESSAGES.emailInvalid);
    expect(inlineFieldError('phone', '123')).toBe(MESSAGES.phoneInvalid);
    expect(inlineFieldError('recruiter_email', 'nope')).toBe(MESSAGES.emailInvalid);
  });
});

describe('submission validation', () => {
  const keys = ['q1', 'q2'];
  const validCandidate = {
    name: 'Jane Doe',
    email: 'jane@example.com',
    phone: '5551234567',
    recruiter_email: 'recruiter@example.com',
  };

  it('lists required-field messages in Streamlit order', () => {
    const errors = validateSubmission(
      { name: '', email: '', phone: '', recruiter_email: '' },
      {},
      keys
    );
    expect(errors).toEqual([
      MESSAGES.nameRequired,
      MESSAGES.emailRequired,
      MESSAGES.phoneRequired,
      MESSAGES.recruiterRequired,
      MESSAGES.unanswered,
    ]);
  });

  it('requires every question key to be non-empty', () => {
    const errors = validateSubmission(validCandidate, { q1: 'ok' }, keys);
    expect(errors).toContain(MESSAGES.unanswered);
  });

  it('passes when candidate fields and all answers are valid', () => {
    const errors = validateSubmission(validCandidate, { q1: 'a', q2: 'b' }, keys);
    expect(errors).toEqual([]);
  });
});

describe('progress counting', () => {
  const keys = ['a', 'b', 'c'];

  it('counts only non-empty answers', () => {
    expect(countAnswered({ a: 'x', b: '  ', c: null }, keys)).toBe(1);
    expect(countAnswered({ a: '1', b: '2', c: '3' }, keys)).toBe(3);
  });

  it('treats the quiz as complete only when every key is filled', () => {
    expect(allQuestionsAnswered({ a: '1', b: '2' }, keys)).toBe(false);
    expect(allQuestionsAnswered({ a: '1', b: '2', c: '3' }, keys)).toBe(true);
    expect(allQuestionsAnswered({}, [])).toBe(false);
  });
});
