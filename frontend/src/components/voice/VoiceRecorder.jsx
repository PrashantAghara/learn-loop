import { useRef, useState } from "react";
import client from "../../api/client";

export default function VoiceRecorder({ onResult }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", blob, "recording.webm");
      const { data } = await client.post("/voice/message", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onResult(data);
    };
    recorder.start();
    mediaRecorderRef.current = recorder;
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  return (
    <button
      onClick={recording ? stopRecording : startRecording}
      className={`px-4 py-2 rounded-lg text-sm ${
        recording ? "bg-red-600 text-white" : "bg-slate-200 text-slate-700"
      }`}
    >
      {recording ? "⏹ Stop" : "🎤 Voice"}
    </button>
  );
}
