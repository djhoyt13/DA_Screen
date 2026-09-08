const NAME_RE = /^[A-Za-z\s'-]+$/;
const EMAIL_RE = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const PHONE_RE = /^\+?1?\d{10,14}$/;

export const MESSAGES = {
  nameRequired: 'Name is required',
  nameInvalid: 'Please enter a valid name (letters, spaces, hyphens, and apostrophes only)',
  emailRequired: 'Email is required',
  emailInvalid: 'Please enter a valid email address',
  phoneRequired: 'Phone number is required',
  phoneInvalid: 'Please enter a valid phone number (10-14 digits, can include country code)',
  recruiterRequired: "Recruiter's email is required",
  recruiterInvalid: 'Please enter a valid recruiter email address',
  unanswered: 'Please make sure you have answered all of the questions',
};

export function isValidName(name) {
  return name ? NAME_RE.test(name) : false;
}

export function isValidEmail(email) {
  return email ? EMAIL_RE.test(email) : false;
}

export function isValidPhone(phone) {
  if (!phone) {
    return false;
  }
  const stripped = phone.replace(/[\s\-()]/g, '');
  return stripped ? PHONE_RE.test(stripped) : false;
}

export function inlineFieldError(field, value) {
  if (!value) {
    return '';
  }
  if (field === 'name' && !isValidName(value)) {
    return MESSAGES.nameInvalid;
  }
  if (field === 'email' && !isValidEmail(value)) {
    return MESSAGES.emailInvalid;
  }
  if (field === 'phone' && !isValidPhone(value)) {
    return MESSAGES.phoneInvalid;
  }
  if (field === 'recruiter_email' && !isValidEmail(value)) {
    return MESSAGES.emailInvalid;
  }
  return '';
}

export function validateSubmission(candidate, answers, questionKeys) {
  const errors = [];
  const name = candidate?.name?.trim() || '';
  const email = candidate?.email?.trim() || '';
  const phone = candidate?.phone?.trim() || '';
  const recruiter = candidate?.recruiter_email?.trim() || '';

  if (!name) {
    errors.push(MESSAGES.nameRequired);
  } else if (!isValidName(name)) {
    errors.push(MESSAGES.nameInvalid);
  }

  if (!email) {
    errors.push(MESSAGES.emailRequired);
  } else if (!isValidEmail(email)) {
    errors.push(MESSAGES.emailInvalid);
  }

  if (!phone) {
    errors.push(MESSAGES.phoneRequired);
  } else if (!isValidPhone(phone)) {
    errors.push(MESSAGES.phoneInvalid);
  }

  if (!recruiter) {
    errors.push(MESSAGES.recruiterRequired);
  } else if (!isValidEmail(recruiter)) {
    errors.push(MESSAGES.recruiterInvalid);
  }

  if (!allQuestionsAnswered(answers, questionKeys)) {
    errors.push(MESSAGES.unanswered);
  }

  return errors;
}

export function allQuestionsAnswered(answers, questionKeys) {
  if (!questionKeys?.length) {
    return false;
  }
  return countAnswered(answers, questionKeys) === questionKeys.length;
}

export function countAnswered(answers, questionKeys) {
  if (!questionKeys?.length) {
    return 0;
  }
  let count = 0;
  for (const key of questionKeys) {
    const value = answers?.[key];
    if (value != null && String(value).trim() !== '') {
      count += 1;
    }
  }
  return count;
}
