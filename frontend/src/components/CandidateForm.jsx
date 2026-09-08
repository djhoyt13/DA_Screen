export default function CandidateForm({ values, errors, onChange, disabled }) {
  const fields = [
    { name: 'name', label: 'Enter your name:', autoComplete: 'name' },
    { name: 'email', label: 'Enter your email:', autoComplete: 'email' },
    { name: 'phone', label: 'Enter your phone number:', autoComplete: 'tel' },
    { name: 'recruiter_email', label: "Recruiter's Email:", autoComplete: 'email' },
  ];

  return (
    <section className="candidate-section">
      <h2>Candidate Information</h2>
      <div className="candidate-info">
        {fields.map((field) => {
          const error = errors[field.name];
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
                disabled={disabled}
              />
              {error ? <div className="field-error">{error}</div> : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
