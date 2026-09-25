import MessageBubble from "./MessageBubble";
import MessageImage from "./MessageImage";
import ReactionBar from "../reaction/ReactionBar";
import QuizCard from "../quiz/QuizCard";
import { API_BASE } from "../../api/client";

export default function Message({ message }) {
  const {
    role,
    content,
    response,
    image_path,
    intent,
    topic,
    quiz_id,
    questions,
  } = message;
  const text = content || response;

  return (
    <div>
      <MessageBubble role={role}>{text}</MessageBubble>
      {role === "assistant" && image_path && <MessageImage src={image_path} />}
      {role === "assistant" && intent === "explain" && topic && (
        <ReactionBar topic={topic} />
      )}
      {role === "assistant" && quiz_id && (
        <QuizCard quizId={quiz_id} questions={questions} />
      )}
    </div>
  );
}
