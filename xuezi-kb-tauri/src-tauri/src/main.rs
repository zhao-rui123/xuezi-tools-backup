#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use rusqlite::{Connection, Result as SqlResult};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;
use directories::ProjectDirs;
use std::fs;
use chrono::Local;

pub struct AppState {
    pub db: Mutex<Connection>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Notebook {
    pub id: i64,
    pub name: String,
    pub created_at: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Note {
    pub id: i64,
    pub notebook_id: i64,
    pub title: String,
    pub content: String,
    pub created_at: String,
    pub updated_at: String,
}

fn get_db_path() -> String {
    if let Some(proj_dirs) = ProjectDirs::from("com", "xuezi", "xuezi-kb") {
        let data_dir = proj_dirs.data_dir();
        fs::create_dir_all(data_dir).ok();
        data_dir.join("xuezi-kb.db").to_string_lossy().to_string()
    } else {
        "xuezi-kb.db".to_string()
    }
}

fn init_db(conn: &Connection) -> SqlResult<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )",
        [],
    )?;
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notebook_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT '无标题',
            content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
        )",
        [],
    )?;
    conn.execute("PRAGMA foreign_keys = ON", [])?;
    Ok(())
}

#[tauri::command]
fn get_notebooks(state: State<AppState>) -> Result<Vec<Notebook>, String> {
    let conn = state.db.lock().map_err(|e| e.to_string())?;
    let mut stmt = conn
        .prepare("SELECT id, name, created_at FROM notebooks ORDER BY created_at DESC")
        .map_err(|e| e.to_string())?;
    let notebooks = stmt
        .query_map([], |row| {
            Ok(Notebook {
                id: row.get(0)?,
                name: row.get(1)?,
                created_at: row.get(2)?,
            })
        })
        .map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| e.to_string())?;
    Ok(notebooks)
}

#[tauri::command]
fn create_notebook(name: String, state: State<AppState>) -> Result<Notebook, String> {
    let conn = state.db.lock().map_err(|e| e.to_string())?;
    conn.execute("INSERT INTO notebooks (name) VALUES (?1)", [&name])
        .map_err(|e| e.to_string())?;
    let id = conn.last_insert_rowid();
    let mut stmt = conn
        .prepare("SELECT id, name, created_at FROM notebooks WHERE id = ?1")
        .map_err(|e| e.to_string())?;
    let notebook = stmt
        .query_row([id], |row| {
            Ok(Notebook {
                id: row.get(0)?,
                name: row.get(1)?,
                created_at: row.get(2)?,
            })
        })
        .map_err(|e| e.to_string())?;
    Ok(notebook)
}

#[tauri::command]
fn get_notes(notebook_id: i64, state: State<AppState>) -> Result<Vec<Note>, String> {
    let conn = state.db.lock().map_err(|e| e.to_string())?;
    let mut stmt = conn
        .prepare("SELECT id, notebook_id, title, content, created_at, updated_at FROM notes WHERE notebook_id = ?1 ORDER BY updated_at DESC")
        .map_err(|e| e.to_string())?;
    let notes = stmt
        .query_map([notebook_id], |row| {
            Ok(Note {
                id: row.get(0)?,
                notebook_id: row.get(1)?,
                title: row.get(2)?,
                content: row.get(3)?,
                created_at: row.get(4)?,
                updated_at: row.get(5)?,
            })
        })
        .map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| e.to_string())?;
    Ok(notes)
}

#[tauri::command]
fn create_note(notebook_id: i64, title: String, content: String, state: State<AppState>) -> Result<Note, String> {
    let conn = state.db.lock().map_err(|e| e.to_string())?;
    conn.execute(
        "INSERT INTO notes (notebook_id, title, content) VALUES (?1, ?2, ?3)",
        rusqlite::params![notebook_id, title, content],
    ).map_err(|e| e.to_string())?;
    let id = conn.last_insert_rowid();
    let mut stmt = conn
        .prepare("SELECT id, notebook_id, title, content, created_at, updated_at FROM notes WHERE id = ?1")
        .map_err(|e| e.to_string())?;
    let note = stmt
        .query_row([id], |row| {
            Ok(Note {
                id: row.get(0)?,
                notebook_id: row.get(1)?,
                title: row.get(2)?,
                content: row.get(3)?,
                created_at: row.get(4)?,
                updated_at: row.get(5)?,
            })
        })
        .map_err(|e| e.to_string())?;
    Ok(note)
}

#[tauri::command]
fn update_note(id: i64, title: String, content: String, state: State<AppState>) -> Result<(), String> {
    let conn = state.db.lock().map_err(|e| e.to_string())?;
    conn.execute(
        "UPDATE notes SET title = ?1, content = ?2, updated_at = datetime('now', 'localtime') WHERE id = ?3",
        rusqlite::params![title, content, id],
    ).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn delete_note(id: i64, state: State<AppState>) -> Result<(), String> {
    let conn = state.db.lock().map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM notes WHERE id = ?1", [id]).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn backup_data(state: State<AppState>) -> Result<String, String> {
    let _conn = state.db.lock().map_err(|e| e.to_string())?;
    
    let backup_dir = if let Some(proj_dirs) = ProjectDirs::from("com", "xuezi", "xuezi-kb") {
        let backup_base = proj_dirs.data_dir().parent().unwrap().join(" backups");
        fs::create_dir_all(&backup_base).ok();
        backup_base
    } else {
        std::env::current_dir().unwrap().join("backups")
    };
    
    let timestamp = Local::now().format("%Y%m%d_%H%M%S").to_string();
    let backup_path = backup_dir.join(format!("xuezi-kb-backup-{}.db", timestamp));
    
    fs::copy(get_db_path(), &backup_path).map_err(|e| e.to_string())?;
    
    Ok(backup_path.to_string_lossy().to_string())
}

fn main() {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path).expect("Failed to open database");
    init_db(&conn).expect("Failed to initialize database");

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            Some(vec!["--autostart"]),
        ))
        .plugin(tauri_plugin_notification::init())
        .manage(AppState {
            db: Mutex::new(conn),
        })
        .invoke_handler(tauri::generate_handler![
            get_notebooks,
            create_notebook,
            get_notes,
            create_note,
            update_note,
            delete_note,
            backup_data,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
