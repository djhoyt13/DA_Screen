function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function simpleMarkdownToHtml(content) {
  const escaped = escapeHtml(content);
  return escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

function CodeBlock({ language, content }) {
  return (
    <pre className="code-block">
      {language ? <span className="code-lang">{language}</span> : null}
      <code>{content}</code>
    </pre>
  );
}

function MarkdownBlock({ content }) {
  return (
    <div
      className="markdown-block"
      dangerouslySetInnerHTML={{ __html: simpleMarkdownToHtml(content) }}
    />
  );
}

function TableBlock({ columns = [], rows = [] }) {
  const headers = columns.length
    ? columns
    : rows[0] && !Array.isArray(rows[0])
      ? Object.keys(rows[0])
      : [];

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        {headers.length ? (
          <thead>
            <tr>
              {headers.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
        ) : null}
        <tbody>
          {rows.map((row, rowIndex) => {
            const cells = Array.isArray(row)
              ? row
              : headers.map((col) => row[col]);
            return (
              <tr key={rowIndex}>
                {cells.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell == null ? '' : String(cell)}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function renderBlock(block, index) {
  if (!block || !block.type) {
    return null;
  }
  if (block.type === 'code') {
    return (
      <CodeBlock
        key={`block-${index}`}
        language={block.language}
        content={block.content || ''}
      />
    );
  }
  if (block.type === 'markdown') {
    return <MarkdownBlock key={`block-${index}`} content={block.content || ''} />;
  }
  if (block.type === 'table') {
    return (
      <TableBlock
        key={`block-${index}`}
        columns={block.columns || []}
        rows={block.rows || []}
      />
    );
  }
  if (block.content) {
    return <MarkdownBlock key={`block-${index}`} content={block.content} />;
  }
  return null;
}

function QuestionInput({ question, value, onChange, disabled }) {
  const prompt = question.prompt || (question.input === 'radio' ? '' : 'Answer:');

  if (question.input === 'radio') {
    const options = question.options || [];
    return (
      <div className="question">
        {prompt ? (
          <p className="answer-prompt">
            <strong>{prompt}</strong>
          </p>
        ) : null}
        <div className="radio-group" role="radiogroup" aria-label={question.key}>
          {options.map((option, index) => {
            const id = `${question.key}-option-${index}`;
            return (
              <label key={option} className="radio-option" htmlFor={id}>
                <input
                  id={id}
                  type="radio"
                  name={question.key}
                  value={option}
                  checked={value === option}
                  onChange={() => onChange(question.key, option)}
                  disabled={disabled}
                />
                <span className="radio-circle" />
                <span className="radio-text">{option}</span>
              </label>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="question">
      {prompt ? (
        <p className="answer-prompt">
          <strong>{prompt}</strong>
        </p>
      ) : null}
      <input
        type="text"
        className="answer-input"
        aria-label={prompt || question.key}
        value={value || ''}
        onChange={(event) => onChange(question.key, event.target.value)}
        disabled={disabled}
      />
    </div>
  );
}

function CategoryContent({ category, answers, onAnswer, disabled }) {
  const blocks = category.blocks || [];
  const questions = category.questions || [];

  if (questions.length <= 1) {
    return (
      <>
        {blocks.map((block, index) => renderBlock(block, index))}
        {questions.map((question) => (
          <QuestionInput
            key={question.key}
            question={question}
            value={answers[question.key]}
            onChange={onAnswer}
            disabled={disabled}
          />
        ))}
      </>
    );
  }

  const extra = Math.max(0, blocks.length - questions.length);
  const leading = blocks.slice(0, extra);
  const paired = blocks.slice(extra);

  return (
    <>
      {leading.map((block, index) => renderBlock(block, index))}
      {questions.map((question, index) => (
        <div key={question.key} className="question-cluster">
          {paired[index] ? renderBlock(paired[index], extra + index) : null}
          <QuestionInput
            question={question}
            value={answers[question.key]}
            onChange={onAnswer}
            disabled={disabled}
          />
        </div>
      ))}
    </>
  );
}

export default function QuestionSection({ section, answers, onAnswer, disabled }) {
  return (
    <section className="quiz-section">
      <h2>{section.name}</h2>
      {(section.categories || []).map((category) => (
        <div key={category.name} className="quiz-category">
          {category.name && category.name !== 'General' ? <h3>{category.name}</h3> : null}
          <CategoryContent
            category={category}
            answers={answers}
            onAnswer={onAnswer}
            disabled={disabled}
          />
        </div>
      ))}
    </section>
  );
}
