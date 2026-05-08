from __future__ import annotations

import aiosqlite
from pathlib import Path
from typing import Literal

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "qubit.db"


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DB_PATH
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._init_schema()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected")
        return self._conn

    async def _init_schema(self) -> None:
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT NOT NULL,
                is_banned INTEGER NOT NULL DEFAULT 0,
                referred_by INTEGER,
                requests_used_today INTEGER NOT NULL DEFAULT 0,
                last_usage_date TEXT,
                referral_bonus INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS referrals (
                inviter_id INTEGER NOT NULL,
                invitee_id INTEGER NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                PRIMARY KEY (inviter_id, invitee_id)
            );
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_orders (
                label TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                requests INTEGER NOT NULL,
                amount_rub REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                paid_at TEXT,
                yoomoney_operation_id TEXT
            );
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS yoomoney_processed_ops (
                operation_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        await self.conn.commit()

    async def upsert_user(
        self,
        user_id: int,
        username: str | None,
        full_name: str,
        joined_at_iso: str,
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO users (user_id, username, full_name, joined_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name;
            """,
            (user_id, username, full_name, joined_at_iso),
        )
        await self.conn.commit()

    async def get_user_row(self, user_id: int) -> aiosqlite.Row | None:
        cur = await self.conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        )
        return await cur.fetchone()

    async def set_banned(self, user_id: int, banned: bool) -> None:
        await self.conn.execute(
            "UPDATE users SET is_banned = ? WHERE user_id = ?",
            (1 if banned else 0, user_id),
        )
        await self.conn.commit()

    async def add_referral_if_new(
        self,
        inviter_id: int,
        invitee_id: int,
        created_at_iso: str,
    ) -> bool:
        if inviter_id == invitee_id:
            return False
        dup = await self.conn.execute(
            "SELECT 1 FROM referrals WHERE invitee_id = ? LIMIT 1",
            (invitee_id,),
        )
        if await dup.fetchone():
            return False
        invite_row = await self.get_user_row(inviter_id)
        if invite_row is None:
            return False
        await self.conn.execute("BEGIN IMMEDIATE")
        try:
            await self.conn.execute(
                """
                INSERT INTO referrals (inviter_id, invitee_id, created_at)
                VALUES (?, ?, ?);
                """,
                (inviter_id, invitee_id, created_at_iso),
            )
            await self.conn.execute(
                """
                UPDATE users
                SET referral_bonus = referral_bonus + 1
                WHERE user_id = ?;
                """,
                (inviter_id,),
            )
            await self.conn.execute(
                """
                UPDATE users
                SET referred_by = COALESCE(referred_by, ?)
                WHERE user_id = ?;
                """,
                (inviter_id, invitee_id),
            )
            await self.conn.commit()
        except Exception:
            await self.conn.rollback()
            return False
        return True

    async def count_referrals(self, inviter_id: int) -> int:
        cur = await self.conn.execute(
            "SELECT COUNT(*) AS c FROM referrals WHERE inviter_id = ?",
            (inviter_id,),
        )
        row = await cur.fetchone()
        return int(row["c"]) if row else 0

    async def reset_daily_counter_if_needed(
        self,
        user_id: int,
        today: str,
    ) -> tuple[int, int]:
        """Возвращает (requests_used_today после сброса, referral_bonus)."""
        row = await self.get_user_row(user_id)
        if row is None:
            return 0, 0
        last = row["last_usage_date"]
        used = row["requests_used_today"]
        bonus = row["referral_bonus"]
        if last != today:
            await self.conn.execute(
                """
                UPDATE users
                SET requests_used_today = 0,
                    last_usage_date = ?
                WHERE user_id = ?;
                """,
                (today, user_id),
            )
            await self.conn.commit()
            return 0, bonus
        return used, bonus

    async def increment_usage(self, user_id: int, today: str) -> None:
        await self.conn.execute(
            """
            UPDATE users
            SET requests_used_today = requests_used_today + 1,
                last_usage_date = ?
            WHERE user_id = ?;
            """,
            (today, user_id),
        )
        await self.conn.commit()

    async def add_bonus_requests(self, user_id: int, amount: int) -> None:
        await self.conn.execute(
            """
            UPDATE users SET referral_bonus = referral_bonus + ? WHERE user_id = ?;
            """,
            (amount, user_id),
        )
        await self.conn.commit()

    async def set_bonus_requests(self, user_id: int, amount: int) -> None:
        await self.conn.execute(
            "UPDATE users SET referral_bonus = ? WHERE user_id = ?;",
            (amount, user_id),
        )
        await self.conn.commit()

    async def total_users(self) -> int:
        cur = await self.conn.execute("SELECT COUNT(*) AS c FROM users;")
        row = await cur.fetchone()
        return int(row["c"]) if row else 0

    async def total_requests_today_sum(self) -> int:
        cur = await self.conn.execute(
            "SELECT SUM(requests_used_today) AS s FROM users;"
        )
        row = await cur.fetchone()
        return int(row["s"] or 0)

    async def create_payment_order(
        self,
        label: str,
        user_id: int,
        requests: int,
        amount_rub: float,
        created_at_iso: str,
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO payment_orders (label, user_id, requests, amount_rub, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?);
            """,
            (label, user_id, requests, amount_rub, created_at_iso),
        )
        await self.conn.commit()

    async def get_payment_order(self, label: str) -> aiosqlite.Row | None:
        cur = await self.conn.execute(
            "SELECT * FROM payment_orders WHERE label = ?;",
            (label,),
        )
        return await cur.fetchone()

    async def try_fulfill_yoomoney_payment(
        self,
        *,
        label: str,
        operation_id: str,
        amount_received: float,
        paid_at_iso: str,
        amount_tolerance: float = 0.009,
    ) -> str:
        """
        Идempotent: повтор того же operation_id → 'duplicate_op'.
        Всё выполняется под одним BEGIN IMMEDIATE, чтобы исключить гонки.
        """
        await self.conn.execute("BEGIN IMMEDIATE")
        try:
            dup = await self.conn.execute(
                "SELECT 1 FROM yoomoney_processed_ops WHERE operation_id = ?;",
                (operation_id,),
            )
            if await dup.fetchone():
                await self.conn.rollback()
                return "duplicate_op"

            order_cur = await self.conn.execute(
                "SELECT * FROM payment_orders WHERE label = ?;",
                (label,),
            )
            order_row = await order_cur.fetchone()
            if order_row is None:
                await self.conn.rollback()
                return "unknown_label"

            if str(order_row["status"]) != "pending":
                await self.conn.rollback()
                return "not_pending"

            expected = float(order_row["amount_rub"])
            if abs(expected - amount_received) > amount_tolerance:
                await self.conn.rollback()
                return "amount_mismatch"

            user_id = int(order_row["user_id"])
            requests = int(order_row["requests"])

            await self.conn.execute(
                """
                INSERT INTO yoomoney_processed_ops (operation_id, label, created_at)
                VALUES (?, ?, ?);
                """,
                (operation_id, label, paid_at_iso),
            )
            await self.conn.execute(
                """
                UPDATE payment_orders
                SET status = 'paid',
                    paid_at = ?,
                    yoomoney_operation_id = ?
                WHERE label = ? AND status = 'pending';
                """,
                (paid_at_iso, operation_id, label),
            )
            await self.conn.execute(
                """
                UPDATE users SET referral_bonus = referral_bonus + ? WHERE user_id = ?;
                """,
                (requests, user_id),
            )
            await self.conn.commit()
            return "credited"
        except Exception:
            await self.conn.rollback()
            return "error"

    async def add_chat_message(
        self,
        user_id: int,
        role: Literal["user", "assistant"],
        content: str,
        created_at_iso: str,
    ) -> None:
        await self.conn.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, created_at)
            VALUES (?, ?, ?, ?);
            """,
            (user_id, role, content, created_at_iso),
        )
        await self.conn.commit()

    async def get_recent_chat_messages(
        self,
        user_id: int,
        limit: int = 12,
    ) -> list[aiosqlite.Row]:
        cur = await self.conn.execute(
            """
            SELECT role, content, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?;
            """,
            (user_id, limit),
        )
        rows = await cur.fetchall()
        return list(reversed(rows))

    async def clear_chat_messages(self, user_id: int) -> int:
        cur = await self.conn.execute(
            "DELETE FROM chat_messages WHERE user_id = ?;",
            (user_id,),
        )
        await self.conn.commit()
        return int(cur.rowcount or 0)

    async def get_setting(self, key: str, default: str = "") -> str:
        cur = await self.conn.execute(
            "SELECT value FROM bot_settings WHERE key = ?;",
            (key,),
        )
        row = await cur.fetchone()
        if not row:
            return default
        return str(row["value"])

    async def set_setting(self, key: str, value: str) -> None:
        await self.conn.execute(
            """
            INSERT INTO bot_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value;
            """,
            (key, value),
        )
        await self.conn.commit()

    async def get_admin_business_autoreply_enabled(self) -> bool:
        v = await self.get_setting("admin_business_autoreply_enabled", "0")
        return v == "1"

    async def set_admin_business_autoreply_enabled(self, enabled: bool) -> None:
        await self.set_setting("admin_business_autoreply_enabled", "1" if enabled else "0")
