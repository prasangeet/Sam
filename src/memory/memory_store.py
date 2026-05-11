import sqlite3
import json
from typing import Dict, List, Optional

DB_PATH = "memory.db"


class MemoryStore:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    # -----------------------------------
    # 🧱 TABLE SETUP
    # -----------------------------------
    def _create_tables(self):
        # 👤 Profile (long-term identity)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        # 💬 Event-based history
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            action_type TEXT,
            action_params TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 🧠 Flexible memory (future use)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    # -----------------------------------
    # 👤 PROFILE METHODS
    # -----------------------------------
    def set_profile(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO profile (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()

    def get_profile_value(self, key: str) -> Optional[str]:
        cursor = self.conn.execute(
            "SELECT value FROM profile WHERE key=?",
            (key,)
        )
        row = cursor.fetchone()
        return row["value"] if row else None

    def update_profile(self, updates: Dict):
        if not updates:
            return

        # 🔒 whitelist (critical)
        allowed_keys = ["name", "date_of_birth"]

        for k, v in updates.items():
            if k in allowed_keys and v:
                self.set_profile(k, v)

    def get_profile(self) -> Dict:
        return {
            "name": self.get_profile_value("name"),
            "date_of_birth": self.get_profile_value("date_of_birth"),
        }

    # -----------------------------------
    # 💬 HISTORY (EVENT-BASED)
    # -----------------------------------
    def add_event(
        self,
        role: str,
        content: str,
        action_type: Optional[str] = None,
        action_params: Optional[Dict] = None
    ):
        self.conn.execute(
            """
            INSERT INTO history (role, content, action_type, action_params)
            VALUES (?, ?, ?, ?)
            """,
            (
                role,
                content,
                action_type,
                json.dumps(action_params) if action_params else None
            )
        )
        self.conn.commit()

    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        cursor = self.conn.execute(
            """
            SELECT role, content, action_type, action_params
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        events = []
        for row in reversed(rows):
            events.append({
                "role": row["role"],
                "content": row["content"],
                "action_type": row["action_type"],
                "action_params": json.loads(row["action_params"])
                if row["action_params"] else None
            })

        return events

    def clear_history(self):
        self.conn.execute("DELETE FROM history")
        self.conn.commit()

    # -----------------------------------
    # 🧠 LONG-TERM MEMORY (OPTIONAL)
    # -----------------------------------
    def add_memory(self, content: str):
        self.conn.execute(
            "INSERT INTO memory (content) VALUES (?)",
            (content,)
        )
        self.conn.commit()

    def get_memories(self, limit: int = 5) -> List[str]:
        cursor = self.conn.execute(
            """
            SELECT content FROM memory
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [row["content"] for row in cursor.fetchall()]

    # -----------------------------------
    # 🧠 CONTEXT BUILDER (FOR LLM)
    # -----------------------------------
    def build_context(self, event_limit: int = 6):
        """
        Build structured context for LLM.
        Keeps it SMALL and RELEVANT.
        """

        return {
            "profile": self.get_profile(),
            "history": self.get_recent_events(event_limit),
            "memories": self.get_memories(3)
        }
