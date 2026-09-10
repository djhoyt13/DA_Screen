export default function CandidateForm({
  values,
  errors,
  onChange,
  disabled,
  inviteMode = false,
}) {
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

  return (
    <section className="candidate-section">
      <h2>Candidate Information</h2>
      {inviteMode ? (
        <p className="invite-locked-note">
          Details were provided by your recruiter and may be corrected if needed.
        </p>
      ) : null}
      <div className={`candidate-info${inviteMode ? ' is-invite-mode' : ''}`}>
        {fields.map((field) => {
          const error = errors[field.name];
          const fieldLocked = inviteMode && field.lockedInInvite;
          const fieldDisabled = disabled || fieldLocked;
          return (
            <div
              key={field.name}
              className={`field${error ? ' invalid-input' : ''}${
                fieldLocked ? ' is-field-locked' : ''
              }`}
            >
              <label htmlFor={field.name}>{field.label}</label>
              <input
                id={field.name}
                name={field.name}
                type="text"
                autoComplete={field.autoComplete}
                value={values[field.name] || ''}
                onChange={(event) => onChange(field.name, event.target.value)}
                disabled={fieldDisabled}
                readOnly={fieldLocked}
                aria-readonly={fieldLocked || undefined}
              />
              {error ? <div className="field-error">{error}</div> : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
