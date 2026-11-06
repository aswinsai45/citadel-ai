import { useEffect, useState } from "react";
import { api } from "./api";
import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";
import DocsPanel from "./components/DocsPanel";
import { Close } from "./icons";

const MODEL = "llama3.2:3b";

function DocViewer({ doc, onClose }) {
  if (!doc) return null;
  const lines = doc.content.split("\n").length;
  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-8"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex max-h-[80vh] w-full max-w-2xl flex-col border border-line-bright bg-panel"
      >
        <div className="flex items-center justify-between border-b border-line px-5 py-3">
          <div className="flex items-center gap-3">
            <span className="label">document</span>
            <span className="font-mono text-[13px] text-ink">{doc.name}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="label normal-case">{lines} lines</span>
            <button onClick={onClose} className="text-ink-dim hover:text-ink" aria-label="Close">
              <Close className="h-4 w-4" />
            </button>
          </div>
        </div>
        <pre className="flex-1 overflow-auto whitespace-pre-wrap px-5 py-4 font-mono text-[12px] leading-relaxed text-ink-dim">
          {doc.content}
        </pre>
      </div>
    </div>
  );
}

export default function App() {
  const [chats, setChats] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [docs, setDocs] = useState([]);
  const [viewing, setViewing] = useState(null);

  async function refreshChats() {
    const { chats } = await api.listChats();
    setChats(chats);
  }
  async function refreshDocs() {
    const { documents } = await api.listDocs();
    setDocs(documents);
  }

  useEffect(() => {
    refreshChats().catch(() => {});
    refreshDocs().catch(() => {});
  }, []);

  async function selectChat(id) {
    setActiveId(id);
    const chat = await api.getChat(id);
    setMessages(chat.messages);
  }

  function newChat() {
    setActiveId(null);
    setMessages([]);
    setInput("");
  }

  async function deleteChat(id) {
    await api.deleteChat(id);
    if (id === activeId) newChat();
    refreshChats();
  }

  async function send() {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);

    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 120000);
    try {
      const data = await api.ask(q, activeId, ctrl.signal);
      setMessages((m) => [...m, { role: "assistant", text: data.answer ?? "No answer." }]);
      if (!activeId) setActiveId(data.chat_id);
      refreshChats();
    } catch (e) {
      const text =
        e.name === "AbortError"
          ? "Timed out on the local model. Try a shorter, more specific query."
          : "Cannot reach the node. Is the backend running on :8000?";
      setMessages((m) => [...m, { role: "assistant", text }]);
    } finally {
      clearTimeout(timer);
      setLoading(false);
    }
  }

  async function uploadDoc(file) {
    await api.uploadDoc(file);
    refreshDocs();
  }
  async function deleteDoc(name) {
    await api.deleteDoc(name);
    refreshDocs();
  }
  async function viewDoc(name) {
    setViewing(await api.getDoc(name));
  }

  return (
    <div className="crosshairs flex h-full overflow-hidden">
      <Sidebar
        chats={chats}
        activeId={activeId}
        onNew={newChat}
        onSelect={selectChat}
        onDelete={deleteChat}
      />
      <div className="w-px bg-line" />
      <Chat
        messages={messages}
        loading={loading}
        input={input}
        setInput={setInput}
        onSend={send}
        model={MODEL}
      />
      <DocsPanel docs={docs} onUpload={uploadDoc} onDelete={deleteDoc} onView={viewDoc} />

      <DocViewer doc={viewing} onClose={() => setViewing(null)} />
    </div>
  );
}
