import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";

interface Notebook {
  id: number;
  name: string;
  created_at: string;
}

interface Note {
  id: number;
  notebook_id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

function App() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [activeNotebook, setActiveNotebook] = useState<number | null>(null);
  const [activeNote, setActiveNote] = useState<Note | null>(null);
  const [editingContent, setEditingContent] = useState("");
  const [newNotebookName, setNewNotebookName] = useState("");
  const [showNewNotebook, setShowNewNotebook] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotebooks();
  }, []);

  useEffect(() => {
    if (activeNotebook !== null) {
      loadNotes(activeNotebook);
    }
  }, [activeNotebook]);

  useEffect(() => {
    if (activeNote) {
      setEditingContent(activeNote.content);
    }
  }, [activeNote]);

  async function loadNotebooks() {
    try {
      const result = await invoke<Notebook[]>("get_notebooks");
      setNotebooks(result);
      if (result.length > 0 && activeNotebook === null) {
        setActiveNotebook(result[0].id);
      }
    } catch (e) {
      console.error("Failed to load notebooks:", e);
    } finally {
      setLoading(false);
    }
  }

  async function loadNotes(notebookId: number) {
    try {
      const result = await invoke<Note[]>("get_notes", { notebookId });
      setNotes(result);
    } catch (e) {
      console.error("Failed to load notes:", e);
    }
  }

  async function createNotebook() {
    if (!newNotebookName.trim()) return;
    try {
      await invoke("create_notebook", { name: newNotebookName });
      setNewNotebookName("");
      setShowNewNotebook(false);
      await loadNotebooks();
    } catch (e) {
      console.error("Failed to create notebook:", e);
    }
  }

  async function createNote() {
    if (activeNotebook === null) return;
    try {
      const note = await invoke<Note>("create_note", {
        notebookId: activeNotebook,
        title: "新笔记",
        content: "",
      });
      setNotes([...notes, note]);
      setActiveNote(note);
    } catch (e) {
      console.error("Failed to create note:", e);
    }
  }

  async function saveNote() {
    if (activeNote === null) return;
    try {
      await invoke("update_note", {
        id: activeNote.id,
        title: activeNote.title,
        content: editingContent,
      });
      setActiveNote({ ...activeNote, content: editingContent });
      setNotes(notes.map((n) => (n.id === activeNote.id ? { ...n, content: editingContent } : n)));
    } catch (e) {
      console.error("Failed to save note:", e);
    }
  }

  async function deleteNote(id: number) {
    try {
      await invoke("delete_note", { id });
      setNotes(notes.filter((n) => n.id !== id));
      if (activeNote?.id === id) setActiveNote(null);
    } catch (e) {
      console.error("Failed to delete note:", e);
    }
  }

  async function openFile() {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog");
      const { readFile } = await import("@tauri-apps/plugin-fs");
      const selected = await open({ multiple: false });
      if (selected) {
        const content = await readFile(selected as string);
        const text = new TextDecoder().decode(content);
        if (activeNotebook !== null) {
          const note = await invoke<Note>("create_note", {
            notebookId: activeNotebook,
            title: (selected as string).split("/").pop() || "导入文件",
            content: text,
          });
          setNotes([...notes, note]);
          setActiveNote(note);
        }
      }
    } catch (e) {
      console.error("Failed to open file:", e);
    }
  }

  async function backupData() {
    try {
      await invoke("backup_data");
      alert("备份成功！");
    } catch (e) {
      console.error("Failed to backup:", e);
      alert("备份失败: " + e);
    }
  }

  if (loading) {
    return <div className="app" style={{ justifyContent: "center", alignItems: "center" }}>加载中...</div>;
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">📚 雪子知识库</div>
        <div className="sidebar-content">
          <div className="section-title">笔记本</div>
          {notebooks.map((nb) => (
            <div
              key={nb.id}
              className={`notebook-item ${activeNotebook === nb.id ? "active" : ""}`}
              onClick={() => setActiveNotebook(nb.id)}
            >
              📓 {nb.name}
            </div>
          ))}

          {showNewNotebook ? (
            <div style={{ padding: "8px" }}>
              <input
                autoFocus
                value={newNotebookName}
                onChange={(e) => setNewNotebookName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && createNotebook()}
                placeholder="笔记本名称..."
                style={{
                  width: "100%",
                  padding: "6px",
                  borderRadius: "4px",
                  border: "1px solid var(--border)",
                  background: "var(--bg)",
                  color: "var(--text)",
                  marginBottom: "4px",
                }}
              />
              <div style={{ display: "flex", gap: "4px" }}>
                <button className="btn" onClick={createNotebook}>创建</button>
                <button className="btn" onClick={() => setShowNewNotebook(false)}>取消</button>
              </div>
            </div>
          ) : (
            <div className="add-btn" onClick={() => setShowNewNotebook(true)}>➕ 新建笔记本</div>
          )}

          {activeNotebook !== null && (
            <>
              <div className="section-title" style={{ marginTop: "12px" }}>笔记</div>
              {notes.map((note) => (
                <div
                  key={note.id}
                  className={`note-item ${activeNote?.id === note.id ? "active" : ""}`}
                  onClick={() => setActiveNote(note)}
                >
                  📝 {note.title || "无标题"}
                </div>
              ))}
              <div className="add-btn" onClick={createNote}>➕ 新建笔记</div>
            </>
          )}
        </div>
      </div>

      {/* Main area */}
      <div className="main">
        <div className="toolbar">
          <button className="btn" onClick={openFile}>📂 导入文件</button>
          <button className="btn" onClick={backupData}>💾 备份数据</button>
          {activeNote && (
            <button className="btn" onClick={saveNote} style={{ marginLeft: "auto" }}>
              保存
            </button>
          )}
          {activeNote && (
            <button className="btn" onClick={() => deleteNote(activeNote.id)} style={{ color: "#ff6b6b" }}>
              🗑️ 删除
            </button>
          )}
        </div>

        <div className="editor">
          {activeNote ? (
            <textarea
              className="editor-input"
              value={editingContent}
              onChange={(e) => setEditingContent(e.target.value)}
              placeholder="开始写笔记..."
            />
          ) : (
            <div style={{ opacity: 0.5, textAlign: "center", marginTop: "40px" }}>
              选择或创建笔记开始
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
