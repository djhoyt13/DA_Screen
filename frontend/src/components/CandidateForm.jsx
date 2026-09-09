export default function CandidateForm({
  values,
  errors,
  onChange,
  disabled,
  inviteLocked = false,
}) {
  const fields = [
    { name: 'name', label: 'Enter your name:', autoComplete: 'name' },
    { name: 'email', label: 'Enter your email:', autoComplete: 'email' },
    { name: 'phone', label: 'Enter your phone number:', autoComplete: 'tel' },
    { name: 'recruiter_email', label: "Recruiter's Email:", autoComplete: 'email' },
  ];

  return (
    <section className="candidate-section">
      <h2>Candidate Information</h2>
      {inviteLocked ? (
        <p className="invite-locked-note">
          Your details were provided by your recruiter and do not need to be edited.
        </p>
      ) : null}
      <div className={`candidate-info${inviteLocked ? ' is-invite-locked' : ''}`}>
        {fields.map((field) => {
          const error = errors[field.name];
          const fieldDisabled = disabled || inviteLocked;
          return (
            <div
              key={field.name}
              className={`field${error ? ' invalid-input' : ''}`}
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
                readOnly={inviteLocked}
                aria-readonly={inviteLocked || undefined}
              />
              {error ? <div className="field-error">{error}</div> : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
