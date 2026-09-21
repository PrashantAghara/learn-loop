import MessageBubble from "./MessageBubble";
import MessageImage from "./MessageImage";
import MessageAudio from "./MessageAudio";
import ReactionBar from "../reaction/ReactionBar";
import QuizCard from "../quiz/QuizCard";
import { API_BASE } from "../../api/client";

export default function Message({ message }) {
  const {
    role,
    content,
    response,
    image_path,
    audio_files,
    intent,
    topic,
    quiz_id,
    questions,
  } = message;
  const text = content || response;

  return (
    <div>
      <MessageBubble role={role}>{text}</MessageBubble>
      {role === "assistant" && image_path && (
        <MessageImage src={`${API_BASE}${image_path}`} />
      )}
      {role === "assistant" && audio_files?.length > 0 && (
        <MessageAudio files={audio_files} />
      )}
      {role === "assistant" && intent === "explain" && topic && (
        <ReactionBar topic={topic} />
      )}
      {role === "assistant" && quiz_id && questions?.length > 0 && (
        <QuizCard quizId={quiz_id} questions={questions} />
      )}
      {role === "assistant" && quiz_id && !questions?.length && (
        <p className="text-xs text-[var(--text-muted)] mt-2">
          Quiz no longer available for retaking.
        </p>
      )}
    </div>
  );
}
