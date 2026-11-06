import { useRef, useState } from "react";
import { Upload, Doc, Trash } from "../icons";

export default function DocsPanel({ docs, onUpload, onDelete, onView }) {
  const fileRef = useRef(null);
  const [busy, setBusy] = useState(false);

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      await onUpload(file);
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <aside className="flex w-72 shrink-0 flex-col border-l border-line bg-panel">
      <div className="flex items-center justify-between border-b border-line px-4 py-4">
        <span className="label">Corpus</span>
        <span className="label">{String(docs.length).padStart(2, "0")} files</span>
      </div>

      <button
        onClick={() => fileRef.current?.click()}
        disabled={busy}
        className="group flex items-center gap-2 border-b border-line px-4 py-3 text-left text-[13px] text-ink transition hover:bg-white/[0.03] disabled:text-ink-faint"
      >
        <Upload className="h-4 w-4 text-ink-dim transition group-hover:text-ink" />
        {busy ? "Ingesting…" : "Upload document"}
      </button>
      <input ref={fileRef} type="file" accept=".txt,.md" onChange={handleFile} className="hidden" />

      <div className="flex-1 overflow-y-auto">
        {docs.length === 0 && (
          <div className="px-4 py-3 text-[12px] text-ink-faint">Corpus empty.</div>
        )}
        {docs.map((name) => (
          <div
            key={name}
            className="group flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-ink-dim transition hover:bg-white/[0.02] hover:text-ink"
          >
            <Doc className="h-4 w-4 shrink-0 text-ink-faint" />
            <button
              onClick={() => onView(name)}
              className="min-w-0 flex-1 truncate text-left"
              title={name}
            >
              {name}
            </button>
            <button
              onClick={() => onDelete(name)}
              className="shrink-0 text-ink-faint opacity-0 transition hover:text-ink group-hover:opacity-100"
              aria-label="Delete document"
            >
              <Trash className="h-3.5 w-3.5" width={14} height={14} />
            </button>
          </div>
        ))}
      </div>

      <div className="border-t border-line px-4 py-3">
        <div className="label normal-case tracking-[0.1em]">.txt / .md · indexed on query</div>
      </div>
    </aside>
  );
}
