import { useEffect, useState } from "react";
import client from "../../api/client";

export default function QuizCard({ quizId, questions: initialQuestions }) {
  const [questions, setQuestions] = useState(initialQuestions || []);
  const [answers, setAnswers] = useState(() =>
    Array((initialQuestions || []).length).fill("")
  );
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(!initialQuestions);

  useEffect(() => {
    if (initialQuestions) return;
    (async () => {
      const { data } = await client.get(`/assess/${quizId}`);
      if (data.submitted) {
        setResult(data);
      } else {
        setQuestions(data.questions);
        setAnswers(Array(data.questions.length).fill(""));
      }
      setLoading(false);
    })();
  }, [quizId, initialQuestions]);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const { data } = await client.post(`/assess/${quizId}/submit`, {
        answers,
      });
      setResult(data);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading)
    return (
      <p className="text-xs text-[var(--text-muted)] mt-2">Loading quiz…</p>
    );

  if (result) {
    return (
      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-4 space-y-3 mt-2">
        <p className="font-semibold text-[var(--text)]">
          Score: {result.correct}/{result.total}
        </p>
        {result.results.map((r, i) => (
          <div key={i} className="text-sm border-t border-[var(--border)] pt-2">
            <p className="font-medium text-[var(--text)]">{r.question}</p>
            <p className={r.correct ? "text-green-500" : "text-red-400"}>
              {r.feedback}
            </p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-4 space-y-4 mt-2">
      {questions.map((q, i) => (
        <div key={i}>
          <p className="font-medium text-[var(--text)] mb-1">{q.question}</p>
          <input
            className="w-full border border-[var(--border)] bg-[var(--bg)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
            placeholder="Your answer"
            value={answers[i]}
            onChange={(e) => {
              const next = [...answers];
              next[i] = e.target.value;
              setAnswers(next);
            }}
          />
        </div>
      ))}
      <button
        onClick={handleSubmit}
        disabled={submitting}
        className="px-4 py-2 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg text-sm disabled:opacity-50"
      >
        {submitting ? "Grading…" : "Submit answers"}
      </button>
    </div>
  );
}
