import { useEffect, useState } from 'react';
import { ApiError } from '../api.js';
import { inlineFieldError, MESSAGES } from '../validation.js';

const EDITABLE_INVITE_FIELDS = new Set(['name', 'email', 'phone']);

function requiredMessage(field) {
  if (field === 'name') return MESSAGES.nameRequired;
  if (field === 'email') return MESSAGES.emailRequired;
  if (field === 'phone') return MESSAGES.phoneRequired;
  return 'This field is required';
}

export default function CandidateForm({
  values,
  errors,
  onChange,
  disabled,
  examLocked = false,
  inviteMode = false,
  onSaveInviteField,
}) {
  const [fieldModes, setFieldModes] = useState({});
  const [baselines, setBaselines] = useState({});
  const [savingField, setSavingField] = useState(null);
  const [localErrors, setLocalErrors] = useState({});

  useEffect(() => {
    if (!inviteMode) {
      setFieldModes({});
      setBaselines({});
      setSavingField(null);
      setLocalErrors({});
    }
  }, [inviteMode]);

  useEffect(() => {
    if (examLocked) {
      setFieldModes({});
      setBaselines({});
      setSavingField(null);
      setLocalErrors({});
    }
  }, [examLocked]);

  const fields = [
    { name: 'name', label: 'Your name:', autoComplete: 'name' },
    { name: 'email', label: 'Your email:', autoComplete: 'email' },
    { name: 'phone', label: 'Your phone number:', autoComplete: 'tel' },
    {
      name: 'recruiter_email',
      label: "Recruiter's Email:",
      autoComplete: 'email',
      lockedInInvite: true,
    },
  ];

  function modeFor(fieldName) {
    return fieldModes[fieldName] === 'editing' ? 'editing' : 'idle';
  }

  function displayError(fieldName) {
    return localErrors[fieldName] || errors[fieldName] || '';
  }

  function startEdit(fieldName) {
    if (!inviteMode || examLocked || savingField) {
      return;
    }
    const current = values[fieldName] || '';
    setBaselines((prev) => ({ ...prev, [fieldName]: current }));
    setFieldModes((prev) => ({ ...prev, [fieldName]: 'editing' }));
    setLocalErrors((prev) => ({ ...prev, [fieldName]: '' }));
  }

  function cancelEdit(fieldName) {
    const baseline = baselines[fieldName] ?? values[fieldName] ?? '';
    onChange(fieldName, baseline);
    setFieldModes((prev) => {
      const next = { ...prev };
      delete next[fieldName];
      return next;
    });
    setBaselines((prev) => {
      const next = { ...prev };
      delete next[fieldName];
      return next;
    });
    setLocalErrors((prev) => ({ ...prev, [fieldName]: '' }));
  }

  async function submitEdit(fieldName) {
    if (!inviteMode || examLocked || savingField || typeof onSaveInviteField !== 'function') {
      return;
    }
    const value = values[fieldName] || '';
    const trimmed = value.trim();
    const baseline = (baselines[fieldName] ?? '').trim();
    if (trimmed === baseline) {
      return;
    }
    if (!trimmed) {
      setLocalErrors((prev) => ({ ...prev, [fieldName]: requiredMessage(fieldName) }));
      return;
    }
    const clientError = inlineFieldError(fieldName, trimmed);
    if (clientError) {
      setLocalErrors((prev) => ({ ...prev, [fieldName]: clientError }));
      return;
    }

    setSavingField(fieldName);
    setLocalErrors((prev) => ({ ...prev, [fieldName]: '' }));
    try {
      await onSaveInviteField(fieldName, trimmed);
      setFieldModes((prev) => {
        const next = { ...prev };
        delete next[fieldName];
        return next;
      });
      setBaselines((prev) => {
        const next = { ...prev };
        delete next[fieldName];
        return next;
      });
    } catch (err) {
      let message = 'Unable to save. Please try again.';
      if (err instanceof ApiError) {
        if (err.fields && err.fields[fieldName]) {
          message = String(err.fields[fieldName]);
        } else if (err.message) {
          message = err.message;
        }
      }
      setLocalErrors((prev) => ({ ...prev, [fieldName]: message }));
    } finally {
      setSavingField(null);
    }
  }

  function handleKeyDown(fieldName, event) {
    if (!inviteMode || modeFor(fieldName) !== 'editing') {
      return;
    }
    if (event.key === 'Escape') {
      event.preventDefault();
      cancelEdit(fieldName);
    }
  }

  return (
    <section className="candidate-section">
      <h2>Candidate Information</h2>
      {inviteMode ? (
        <p className="invite-locked-note">
          Details were provided by your recruiter. Press Update next to a field to correct
          your name, email, or phone, then Submit to save.
        </p>
      ) : null}
      <div className={`candidate-info${inviteMode ? ' is-invite-mode' : ''}`}>
        {fields.map((field) => {
          const error = displayError(field.name);
          const isEditing = inviteMode && modeFor(field.name) === 'editing';
          const alwaysLocked = inviteMode && field.lockedInInvite;
          const inviteIdleLocked =
            inviteMode && EDITABLE_INVITE_FIELDS.has(field.name) && !isEditing;
          const fieldLocked =
            alwaysLocked || inviteIdleLocked || (inviteMode && examLocked) || disabled;
          const fieldDisabled = inviteMode
            ? fieldLocked || !isEditing || disabled
            : disabled;
          const showAction =
            inviteMode && EDITABLE_INVITE_FIELDS.has(field.name);
          const baseline = baselines[field.name] ?? values[field.name] ?? '';
          const current = values[field.name] || '';
          const isDirty = current.trim() !== String(baseline).trim();
          const isSaving = savingField === field.name;
          const actionDisabled =
            disabled ||
            examLocked ||
            Boolean(savingField) ||
            (isEditing && (!isDirty || !current.trim()));

          return (
            <div
              key={field.name}
              className={`field${error ? ' invalid-input' : ''}${
                fieldLocked || alwaysLocked ? ' is-field-locked' : ''
              }${showAction ? ' has-field-action' : ''}`}
            >
              <label htmlFor={field.name}>{field.label}</label>
              <div className={showAction ? 'field-row' : undefined}>
                <input
                  id={field.name}
                  name={field.name}
                  type="text"
                  autoComplete={field.autoComplete}
                  value={current}
                  onChange={(event) => {
                    onChange(field.name, event.target.value);
                    if (localErrors[field.name]) {
                      setLocalErrors((prev) => ({ ...prev, [field.name]: '' }));
                    }
                  }}
                  onKeyDown={(event) => handleKeyDown(field.name, event)}
                  disabled={fieldDisabled}
                  readOnly={fieldLocked && !isEditing}
                  aria-readonly={(fieldLocked && !isEditing) || undefined}
                />
                {showAction ? (
                  <button
                    type="button"
                    className={`btn-field-action${
                      isEditing ? ' btn-field-action--submit' : ' btn-field-action--update'
                    }`}
                    disabled={actionDisabled}
                    onClick={() =>
                      isEditing ? submitEdit(field.name) : startEdit(field.name)
                    }
                  >
                    {isSaving ? 'Saving…' : isEditing ? 'Submit' : 'Update'}
                  </button>
                ) : null}
              </div>
              {error ? <div className="field-error">{error}</div> : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
