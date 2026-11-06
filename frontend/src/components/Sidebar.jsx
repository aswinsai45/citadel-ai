import { Plus, Trash, Mark } from "../icons";

function stamp(ts) {
  if (!ts) return "--:--";
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
}

export default function Sidebar({ chats, activeId, onNew, onSelect, onDelete }) {
  return (
    <aside className="flex w-60 shrink-0 flex-col bg-panel">
      <div className="flex items-center gap-2.5 border-b border-line px-4 py-4">
        <Mark className="h-5 w-5 text-ink" width={20} height={20} />
        <div className="leading-none">
          <div className="text-[13px] font-semibold tracking-tight text-ink">CITADEL</div>
          <div className="label mt-1">sovereign node</div>
        </div>
      </div>

      <button
        onClick={onNew}
        className="group flex items-center gap-2 border-b border-line px-4 py-3 text-left text-[13px] text-ink transition hover:bg-white/[0.03]"
      >
        <Plus className="h-4 w-4 text-ink-dim transition group-hover:text-ink" />
        New session
      </button>

      <div className="flex items-center justify-between px-4 py-3">
        <span className="label">Session log</span>
        <span className="label">{String(chats.length).padStart(2, "0")}</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {chats.length === 0 && (
          <div className="px-4 py-2 text-[12px] text-ink-faint">No sessions recorded.</div>
        )}
        {chats.map((c) => {
          const active = c.id === activeId;
          return (
            <div
              key={c.id}
              onClick={() => onSelect(c.id)}
              className={`group relative flex cursor-pointer items-center gap-3 px-4 py-2.5 text-[13px] transition ${
                active ? "bg-white/[0.05] text-ink" : "text-ink-dim hover:bg-white/[0.02] hover:text-ink"
              }`}
            >
              <span
                className={`h-3 w-px shrink-0 ${active ? "bg-ink" : "bg-line-bright"}`}
                aria-hidden
              />
              <div className="min-w-0 flex-1">
                <div className="truncate">{c.title || "untitled"}</div>
                <div className="label mt-0.5 normal-case tracking-[0.1em]">{stamp(c.updated)}</div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(c.id);
                }}
                className="shrink-0 text-ink-faint opacity-0 transition hover:text-ink group-hover:opacity-100"
                aria-label="Delete session"
              >
                <Trash className="h-3.5 w-3.5" width={14} height={14} />
              </button>
            </div>
          );
        })}
      </div>

      <div className="border-t border-line px-4 py-3">
        <div className="label">air-gapped · no egress</div>
      </div>
    </aside>
  );
}
