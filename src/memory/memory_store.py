import sqlite3
import json

from typing import Dict
from typing import List
from typing import Optional

from src.observability.bus import (
    event_bus
)


DB_PATH = "memory.db"


class MemoryStore:

    def __init__(
        self,
        db_path: str = DB_PATH
    ):

        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self._create_tables()

        event_bus.emit(
            "memory_initialized",
            {
                "db_path": db_path
            }
        )

    # -----------------------------------
    # TABLE SETUP
    # -----------------------------------
    def _create_tables(self):

        # Profile table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        # History table
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

        # Memory table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

        event_bus.emit(
            "memory_tables_created",
            {}
        )

    # -----------------------------------
    # PROFILE METHODS
    # -----------------------------------
    def set_profile(
        self,
        key: str,
        value: str
    ):

        self.conn.execute(
            """
            INSERT OR REPLACE INTO
            profile (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )

        self.conn.commit()

        event_bus.emit(
            "profile_value_set",
            {
                "key": key
            }
        )

    def get_profile_value(
        self,
        key: str
    ) -> Optional[str]:

        cursor = self.conn.execute(
            """
            SELECT value
            FROM profile
            WHERE key=?
            """,
            (key,)
        )

        row = cursor.fetchone()

        return row["value"] if row else None

    def update_profile(
        self,
        updates: Dict
    ):

        if not updates:
            return

        allowed_keys = [
            "name",
            "date_of_birth"
        ]

        updated_keys = []

        for k, v in updates.items():

            if k in allowed_keys and v:

                self.set_profile(k, v)

                updated_keys.append(k)

        if updated_keys:

            event_bus.emit(
                "profile_updated",
                {
                    "keys": updated_keys
                }
            )

    def get_profile(self) -> Dict:

        profile = {
            "name": self.get_profile_value(
                "name"
            ),
            "date_of_birth": self.get_profile_value(
                "date_of_birth"
            ),
        }

        event_bus.emit(
            "profile_loaded",
            {
                "has_name": bool(
                    profile["name"]
                )
            }
        )

        return profile

    # -----------------------------------
    # HISTORY METHODS
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
            INSERT INTO history
            (
                role,
                content,
                action_type,
                action_params
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                role,
                content,
                action_type,
                json.dumps(action_params)
                if action_params else None
            )
        )

        self.conn.commit()

        event_bus.emit(
            "history_event_added",
            {
                "role": role,
                "action_type": action_type
            }
        )

    def get_recent_events(
        self,
        limit: int = 10
    ) -> List[Dict]:

        cursor = self.conn.execute(
            """
            SELECT
                role,
                content,
                action_type,
                action_params
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
                "action_params":
                    json.loads(
                        row["action_params"]
                    )
                    if row["action_params"]
                    else None
            })

        event_bus.emit(
            "history_loaded",
            {
                "count": len(events)
            }
        )

        return events

    def clear_history(self):

        self.conn.execute(
            "DELETE FROM history"
        )

        self.conn.commit()

        event_bus.emit(
            "history_cleared",
            {}
        )

    # -----------------------------------
    # LONG TERM MEMORY
    # -----------------------------------
    def add_memory(
        self,
        content: str
    ):

        self.conn.execute(
            """
            INSERT INTO memory
            (content)
            VALUES (?)
            """,
            (content,)
        )

        self.conn.commit()

        event_bus.emit(
            "memory_added",
            {
                "content": content
            }
        )

    def get_memories(
        self,
        limit: int = 5
    ) -> List[str]:

        cursor = self.conn.execute(
            """
            SELECT content
            FROM memory
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        memories = [
            row["content"]
            for row in cursor.fetchall()
        ]

        event_bus.emit(
            "memories_loaded",
            {
                "count": len(memories)
            }
        )

        return memories

    # -----------------------------------
    # CONTEXT BUILDER
    # -----------------------------------
    def build_context(
        self,
        event_limit: int = 6
    ):

        context = {
            "profile": self.get_profile(),
            "history": self.get_recent_events(
                event_limit
            ),
            "memories": self.get_memories(3)
        }

        event_bus.emit(
            "context_constructed",
            {
                "history_count": len(
                    context["history"]
                ),
                "memory_count": len(
                    context["memories"]
                )
            }
        )

        return context
