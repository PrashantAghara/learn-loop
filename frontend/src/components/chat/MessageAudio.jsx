import { API_BASE } from "../../api/client";

export default function MessageAudio({ files }) {
  return (
    <div className="mt-2 space-y-1">
      {files.map((url, i) => (
        <audio key={i} controls src={`${API_BASE}${url}`} className="w-full" />
      ))}
    </div>
  );
}
