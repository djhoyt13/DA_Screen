export function collectQuestionKeys(quiz) {
  const keys = [];
  if (!quiz?.sections) {
    return keys;
  }
  for (const section of quiz.sections) {
    for (const category of section.categories || []) {
      for (const question of category.questions || []) {
        if (question?.key) {
          keys.push(question.key);
        }
      }
    }
  }
  return keys;
}

export function getTotalQuestions(quiz, keys) {
  if (Number.isFinite(quiz?.total_questions) && quiz.total_questions > 0) {
    return quiz.total_questions;
  }
  return keys?.length || 0;
}
