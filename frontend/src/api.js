const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

export function getApiBase() {
  const env = import.meta.env.VITE_API_BASE_URL;
  if (env === '' || env === '/') {
    return '';
  }
  return env || DEFAULT_API_BASE;
}

export class ApiError extends Error {
  constructor(message, { status, fields } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.fields = fields || null;
  }
}

async function fetchWithTimeout(url, options = {}, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new ApiError('The request timed out. Please try again.', { status: 0 });
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

async function parseJson(response) {
  const text = await response.text();
  if (!text) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    return { error: text };
  }
}

export async function fetchQuestions(assessment = 'ds') {
  const url = `${getApiBase()}/api/questions?assessment=${encodeURIComponent(assessment)}`;
  let response;
  try {
    response = await fetchWithTimeout(url, { method: 'GET' }, 8000);
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      `Unable to load questions. Please check that the API is running at ${getApiBase() || window.location.origin}.`,
      { status: 0 }
    );
  }

  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to load questions (${response.status}).`, {
      status: response.status,
      fields: data.fields,
    });
  }
  return data;
}

export async function fetchAssessments() {
  const url = `${getApiBase()}/api/assessments`;
  const response = await fetchWithTimeout(url, { method: 'GET' }, 8000);
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to load assessments (${response.status}).`, {
      status: response.status,
    });
  }
  return data;
}

export async function submitQuiz(payload) {
  const url = `${getApiBase()}/api/submit`;
  let response;
  try {
    response = await fetchWithTimeout(
      url,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      },
      25000
    );
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      `Unable to submit. Please check that the API is running at ${getApiBase() || window.location.origin}.`,
      { status: 0 }
    );
  }

  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Submit failed (${response.status}).`, {
      status: response.status,
      fields: data.fields,
    });
  }
  return data;
}

function adminHeaders(adminKey) {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Key': adminKey,
  };
}

export async function fetchInvite(token) {
  const url = `${getApiBase()}/api/invite/${encodeURIComponent(token)}`;
  const response = await fetchWithTimeout(url, { method: 'GET' }, 8000);
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Invite not found (${response.status}).`, {
      status: response.status,
    });
  }
  return data;
}

export async function markInviteOpened(token, openedAt) {
  const url = `${getApiBase()}/api/invite/${encodeURIComponent(token)}/open`;
  const response = await fetchWithTimeout(
    url,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opened_at: openedAt }),
    },
    8000
  );
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to record open (${response.status}).`, {
      status: response.status,
    });
  }
  return data;
}

export async function markInviteAcknowledged(token, acknowledgedAt) {
  const url = `${getApiBase()}/api/invite/${encodeURIComponent(token)}/acknowledge`;
  const response = await fetchWithTimeout(
    url,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ acknowledged_at: acknowledgedAt }),
    },
    8000
  );
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to record acknowledgment (${response.status}).`, {
      status: response.status,
    });
  }
  return data;
}

export async function adminListExams(adminKey) {
  const url = `${getApiBase()}/api/admin/exams`;
  const response = await fetchWithTimeout(
    url,
    { method: 'GET', headers: adminHeaders(adminKey) },
    8000
  );
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to load exams (${response.status}).`, {
      status: response.status,
      fields: data.fields,
    });
  }
  return data;
}

export async function adminCreateExam(adminKey, payload) {
  const url = `${getApiBase()}/api/admin/exams`;
  const response = await fetchWithTimeout(
    url,
    {
      method: 'POST',
      headers: adminHeaders(adminKey),
      body: JSON.stringify(payload),
    },
    8000
  );
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to create exam (${response.status}).`, {
      status: response.status,
      fields: data.fields,
    });
  }
  return data;
}

export async function adminExamDetail(adminKey, examKey) {
  const url = `${getApiBase()}/api/admin/exams/${encodeURIComponent(examKey)}`;
  const response = await fetchWithTimeout(
    url,
    { method: 'GET', headers: adminHeaders(adminKey) },
    8000
  );
  const data = await parseJson(response);
  if (!response.ok) {
    throw new ApiError(data.error || `Failed to load exam detail (${response.status}).`, {
      status: response.status,
    });
  }
  return data;
}
