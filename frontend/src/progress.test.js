import { describe, expect, it } from 'vitest';
import { collectQuestionKeys, getTotalQuestions } from './progress.js';
import { countAnswered } from './validation.js';

const sampleQuiz = {
  title: 'Data Scientist Technical Review',
  total_questions: 3,
  sections: [
    {
      name: 'Python Basics',
      categories: [
        {
          name: 'Unpacking',
          blocks: [{ type: 'code', language: 'python', content: 'print(1)' }],
          questions: [{ key: 'answer_Unpacking', prompt: 'Terminal Output:', input: 'text' }],
        },
        {
          name: 'Loops',
          questions: [{ key: 'answer_Loops', prompt: 'Terminal Output:', input: 'text' }],
        },
      ],
    },
    {
      name: 'Data Visualization',
      categories: [
        {
          name: 'Data Visualization',
          questions: [
            {
              key: 'answer_DataViz_q2',
              input: 'radio',
              options: ["'Bar Chart'", "'Histogram'"],
            },
          ],
        },
      ],
    },
  ],
};

describe('collectQuestionKeys', () => {
  it('reads keys from the API payload instead of a hardcoded list', () => {
    expect(collectQuestionKeys(sampleQuiz)).toEqual([
      'answer_Unpacking',
      'answer_Loops',
      'answer_DataViz_q2',
    ]);
  });

  it('returns an empty list when the quiz has not loaded', () => {
    expect(collectQuestionKeys(null)).toEqual([]);
    expect(collectQuestionKeys({})).toEqual([]);
  });
});

describe('getTotalQuestions', () => {
  it('prefers total_questions from the API', () => {
    expect(getTotalQuestions(sampleQuiz, ['a', 'b'])).toBe(3);
  });

  it('falls back to collected keys when the API omits a total', () => {
    expect(getTotalQuestions({ sections: [] }, ['a', 'b'])).toBe(2);
  });
});

describe('progress from filled answers', () => {
  const keys = collectQuestionKeys(sampleQuiz);

  it('updates as the user answers', () => {
    expect(countAnswered({}, keys)).toBe(0);
    expect(countAnswered({ answer_Unpacking: 'filled' }, keys)).toBe(1);
    expect(
      countAnswered(
        {
          answer_Unpacking: 'filled',
          answer_Loops: 'filled',
          answer_DataViz_q2: 'option-a',
        },
        keys
      )
    ).toBe(3);
  });
});
