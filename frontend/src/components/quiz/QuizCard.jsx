import { useState } from "react";
import client from "../../api/client";

export default function QuizCard({ quizId, questions }) {
  const [answers, setAnswers] = useState(Array(questions.length).fill(""));
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

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

  if (result) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3">
        <p className="font-semibold text-slate-800">
          Score: {result.correct}/{result.total}
        </p>
        {result.results.map((r, i) => (
          <div key={i} className="text-sm border-t pt-2">
            <p className="font-medium">{r.question}</p>
            <p className={r.correct ? "text-green-600" : "text-red-600"}>
              {r.feedback}
            </p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-4">
      {questions.map((q, i) => (
        <div key={i}>
          <p className="font-medium text-slate-800 mb-1">{q.question}</p>
          <input
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
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
        className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm disabled:opacity-50"
      >
        {submitting ? "Grading…" : "Submit answers"}
      </button>
    </div>
  );
}
