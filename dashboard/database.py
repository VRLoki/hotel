"""
Hotel Intel — SQLite Database Layer.

Handles DB init, migrations, and helper functions.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "hotel_intel.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            location TEXT,
            logo_url TEXT,
            timezone TEXT DEFAULT 'UTC',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'staff' CHECK(role IN ('admin','manager','staff')),
            property_id INTEGER REFERENCES properties(id),
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES properties(id),
            guest_id TEXT NOT NULL,
            data JSON NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(property_id, guest_id)
        );

        CREATE TABLE IF NOT EXISTS recaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES properties(id),
            date TEXT NOT NULL,
            data JSON NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(property_id, date)
        );

        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL UNIQUE REFERENCES properties(id),
            data JSON NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS oauth_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES properties(id),
            provider TEXT NOT NULL CHECK(provider IN ('google','microsoft')),
            client_id TEXT NOT NULL,
            client_secret TEXT NOT NULL,
            tenant_id TEXT,
            allowed_domain TEXT,
            enabled INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(property_id, provider)
        );

        CREATE TABLE IF NOT EXISTS app_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES properties(id),
            app_id TEXT NOT NULL,
            config JSON NOT NULL DEFAULT '{}',
            enabled INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'disconnected' CHECK(status IN ('disconnected','connected','error')),
            last_sync TEXT,
            last_error TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(property_id, app_id)
        );

        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES properties(id),
            module_key TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            status TEXT DEFAULT 'disconnected',
            endpoint TEXT DEFAULT '',
            description TEXT DEFAULT '',
            config JSON DEFAULT '{}',
            UNIQUE(property_id, module_key)
        );
    """)
    # Migration: add oauth_provider to users if missing
    cursor = conn.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'oauth_provider' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN oauth_provider TEXT")
        conn.commit()

    conn.commit()
    conn.close()


# ── Helper Functions ─────────────────────────

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    return [dict(r) for r in rows]


def get_property(conn, property_id):
    return row_to_dict(conn.execute("SELECT * FROM properties WHERE id=?", (property_id,)).fetchone())


def get_all_properties(conn):
    return rows_to_list(conn.execute("SELECT * FROM properties ORDER BY id").fetchall())


def get_user_by_email(conn, email):
    return row_to_dict(conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone())


def get_user_by_id(conn, user_id):
    return row_to_dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())


def get_profiles(conn, property_id):
    rows = conn.execute("SELECT data FROM profiles WHERE property_id=? ORDER BY guest_id", (property_id,)).fetchall()
    return [json.loads(r["data"]) for r in rows]


def get_profile(conn, property_id, guest_id):
    row = conn.execute("SELECT data FROM profiles WHERE property_id=? AND guest_id=?", (property_id, guest_id)).fetchone()
    return json.loads(row["data"]) if row else None


def get_recap(conn, property_id, date):
    row = conn.execute("SELECT data FROM recaps WHERE property_id=? AND date=?", (property_id, date)).fetchone()
    return json.loads(row["data"]) if row else None


def get_recap_dates(conn, property_id):
    rows = conn.execute("SELECT date FROM recaps WHERE property_id=? ORDER BY date", (property_id,)).fetchall()
    return [r["date"] for r in rows]


def get_settings(conn, property_id):
    row = conn.execute("SELECT data FROM settings WHERE property_id=?", (property_id,)).fetchone()
    return json.loads(row["data"]) if row else None


def get_modules(conn, property_id):
    rows = conn.execute("SELECT * FROM modules WHERE property_id=? ORDER BY module_key", (property_id,)).fetchall()
    result = {}
    for r in rows:
        result[r["module_key"]] = {
            "enabled": bool(r["enabled"]),
            "status": r["status"],
            "endpoint": r["endpoint"],
            "description": r["description"],
            "config": json.loads(r["config"]) if r["config"] else {},
        }
    return result


def get_oauth_configs(conn, property_id):
    rows = conn.execute("SELECT * FROM oauth_configs WHERE property_id=? ORDER BY provider", (property_id,)).fetchall()
    return rows_to_list(rows)


def get_oauth_config(conn, property_id, provider):
    return row_to_dict(conn.execute(
        "SELECT * FROM oauth_configs WHERE property_id=? AND provider=?",
        (property_id, provider)
    ).fetchone())


def upsert_oauth_config(conn, property_id, provider, client_id, client_secret, tenant_id, allowed_domain, enabled):
    conn.execute("""
        INSERT INTO oauth_configs (property_id, provider, client_id, client_secret, tenant_id, allowed_domain, enabled, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(property_id, provider) DO UPDATE SET
            client_id=excluded.client_id,
            client_secret=excluded.client_secret,
            tenant_id=excluded.tenant_id,
            allowed_domain=excluded.allowed_domain,
            enabled=excluded.enabled,
            updated_at=datetime('now')
    """, (property_id, provider, client_id, client_secret, tenant_id, allowed_domain, int(enabled)))
    conn.commit()


def get_enabled_oauth_providers(conn):
    """Return set of provider names that are enabled on at least one property."""
    rows = conn.execute("SELECT DISTINCT provider FROM oauth_configs WHERE enabled=1").fetchall()
    return {r["provider"] for r in rows}


def get_all_enabled_oauth_configs(conn, provider):
    """Return all enabled configs for a given provider across all properties."""
    rows = conn.execute(
        "SELECT * FROM oauth_configs WHERE provider=? AND enabled=1",
        (provider,)
    ).fetchall()
    return rows_to_list(rows)


# ── App Config Functions ──────────────────────

def get_app_configs(conn, property_id):
    rows = conn.execute(
        "SELECT * FROM app_configs WHERE property_id=? ORDER BY app_id",
        (property_id,)
    ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["config"] = json.loads(d["config"]) if d["config"] else {}
        d["enabled"] = bool(d["enabled"])
        result.append(d)
    return result


def get_app_config(conn, property_id, app_id):
    row = conn.execute(
        "SELECT * FROM app_configs WHERE property_id=? AND app_id=?",
        (property_id, app_id)
    ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["config"] = json.loads(d["config"]) if d["config"] else {}
    d["enabled"] = bool(d["enabled"])
    return d


def upsert_app_config(conn, property_id, app_id, config, enabled, status="disconnected"):
    conn.execute("""
        INSERT INTO app_configs (property_id, app_id, config, enabled, status, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(property_id, app_id) DO UPDATE SET
            config=excluded.config,
            enabled=excluded.enabled,
            status=excluded.status,
            updated_at=datetime('now')
    """, (property_id, app_id, json.dumps(config), int(enabled), status))
    conn.commit()


def delete_app_config(conn, property_id, app_id):
    conn.execute("DELETE FROM app_configs WHERE property_id=? AND app_id=?", (property_id, app_id))
    conn.commit()


def update_app_config_status(conn, property_id, app_id, status, last_sync=None, last_error=None):
    updates = ["status=?", "updated_at=datetime('now')"]
    params = [status]
    if last_sync is not None:
        updates.append("last_sync=?")
        params.append(last_sync)
    if last_error is not None:
        updates.append("last_error=?")
        params.append(last_error)
    params.extend([property_id, app_id])
    conn.execute(f"UPDATE app_configs SET {', '.join(updates)} WHERE property_id=? AND app_id=?", params)
    conn.commit()


# Run init on import
init_db()
