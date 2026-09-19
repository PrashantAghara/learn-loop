export default function MessageImage({ src }) {
  return (
    <img
      src={src}
      alt="Generated illustration"
      className="mt-2 rounded-xl max-w-sm border border-slate-200"
    />
  );
}
