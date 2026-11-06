import { useEffect, useRef } from "react";
import { Send } from "../icons";

function Thinking() {
  return (
    <div className="flex items-center gap-3">
      <span className="label normal-case">retrieving</span>
      <span className="relative block h-px w-24 overflow-hidden bg-line-bright">
        <span className="scanner absolute inset-y-0 left-0 w-6 bg-ink" />
      </span>
    </div>
  );
}

function Line({ role, text }) {
  const isUser = role === "user";
  return (
    <div className="flex gap-3">
      <span className={`label mt-1 w-12 shrink-0 ${isUser ? "text-ink-dim" : "text-ink"}`}>
        {isUser ? "USER" : "NODE"}
      </span>
      <div
        className={`min-w-0 flex-1 whitespace-pre-wrap text-[14px] leading-relaxed ${
          isUser ? "text-ink-dim" : "text-ink"
        }`}
      >
        {text}
      </div>
    </div>
  );
}

export default function Chat({ messages, loading, input, setInput, onSend, model }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const empty = messages.length === 0;

  return (
    <main className="flex min-w-0 flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-line px-6 py-3">
        <div className="flex items-center gap-3">
          <span className="relative flex h-1.5 w-1.5">
            <span className="live-dot absolute inline-flex h-1.5 w-1.5 bg-ink" />
          </span>
          <span className="label">online · local · {model}</span>
        </div>
        <span className="label">no data leaves this machine</span>
      </header>

      <div ref={scrollRef} className="dotfield flex-1 overflow-y-auto px-6 py-6">
        {empty && !loading ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="label mb-4">enclosure ready</div>
            <p className="max-w-sm text-[14px] leading-relaxed text-ink-dim">
              Query the corpus held inside this node. Nothing you ask or upload
              leaves the machine.
            </p>
            <p className="mt-3 font-mono text-[12px] text-ink-faint">
              e.g. "max discharge pressure of the pump?"
            </p>
          </div>
        ) : (
          <div className="mx-auto max-w-2xl space-y-6">
            {messages.map((m, i) => (
              <Line key={i} role={m.role} text={m.text} />
            ))}
            {loading && (
              <div className="flex gap-3">
                <span className="label mt-1 w-12 shrink-0 text-ink">NODE</span>
                <Thinking />
              </div>
            )}
          </div>
        )}
      </div>

      <div className="border-t border-line px-6 py-4">
        <div className="mx-auto flex max-w-2xl items-center gap-3 border border-line bg-panel px-4 py-1 transition focus-within:border-line-bright">
          <span className="font-mono text-[13px] text-ink-faint">{">"}</span>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSend()}
            placeholder="query the corpus"
            className="flex-1 bg-transparent py-3 text-[14px] text-ink outline-none focus:outline-none focus-visible:outline-none"
          />
          <button
            onClick={onSend}
            disabled={loading || !input.trim()}
            className="flex items-center gap-2 text-ink transition hover:text-ink disabled:cursor-not-allowed disabled:text-ink-faint"
            aria-label="Send query"
          >
            <span className="label normal-case">send</span>
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </main>
  );
}
