const API = "http://localhost:8000";

async function j(res) {
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

export const api = {
  ask: (question, chat_id, signal) =>
    fetch(`${API}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, chat_id }),
      signal,
    }).then(j),

  listChats: () => fetch(`${API}/chats`).then(j),
  getChat: (id) => fetch(`${API}/chats/${id}`).then(j),
  deleteChat: (id) => fetch(`${API}/chats/${id}`, { method: "DELETE" }).then(j),

  listDocs: () => fetch(`${API}/documents`).then(j),
  getDoc: (name) => fetch(`${API}/documents/${encodeURIComponent(name)}`).then(j),
  deleteDoc: (name) =>
    fetch(`${API}/documents/${encodeURIComponent(name)}`, { method: "DELETE" }).then(j),
  uploadDoc: (file) => {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${API}/documents`, { method: "POST", body: fd }).then(j);
  },
};
