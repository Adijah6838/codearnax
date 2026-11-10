import asyncio
import json
import sqlite3
import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.db.init import connect


Handler = Callable[[dict[str, Any]], Awaitable[None]]


class JobQueue:
    def __init__(self) -> None:
        self._q: asyncio.Queue[int] = asyncio.Queue()
        self._handlers: dict[str, Handler] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    def register(self, job_type: str, handler: Handler) -> None:
        self._handlers[job_type] = handler

    def enqueue(self, submission_id: int) -> None:
        self._q.put_nowait(submission_id)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _worker(self) -> None:
        while self._running:
            submission_id = await self._q.get()
            try:
                await self._process(submission_id)
            except Exception as exc:
                self._log(submission_id, "error", f"worker error: {exc!r}")
            finally:
                self._q.task_done()

    def _log(self, submission_id: int, level: str, msg: str) -> None:
        conn = connect()
        try:
            conn.execute(
                "INSERT INTO execution_logs (submission_id, level, message) VALUES (?,?,?)",
                (submission_id, level, msg),
            )
        finally:
            conn.close()

    async def _process(self, submission_id: int) -> None:
        conn = connect()
        try:
            row = conn.execute(
                "SELECT id, user_id, challenge_id, language, source_code, status "
                "FROM submissions WHERE id = ?",
                (submission_id,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return
        if row[5] != "Queued":
            return

        conn = connect()
        try:
            conn.execute(
                "UPDATE submissions SET status = 'Running' WHERE id = ?",
                (submission_id,),
            )
        finally:
            conn.close()

        self._log(submission_id, "info", f"job started: {submission_id}")
        t0 = time.perf_counter()

        try:
            # STUB — real Docker execution arrives in Step 7
            await asyncio.sleep(0.5)
            conn = connect()
            try:
                conn.execute(
                    "UPDATE submissions SET status = 'Accepted' WHERE id = ?",
                    (submission_id,),
                )
            finally:
                conn.close()
        except Exception:
            conn = connect()
            try:
                conn.execute(
                    "UPDATE submissions SET status = 'InternalError' WHERE id = ?",
                    (submission_id,),
                )
            finally:
                conn.close()
            raise
        finally:
            duration = (time.perf_counter() - t0) * 1000
            self._log(submission_id, "info",
                      f"job finished in {duration:.0f} ms")


queue = JobQueue()


def _log_to_json(conn: sqlite3.Connection, sid: int, level: str, msg: str) -> None:
    conn.execute(
        "INSERT INTO execution_logs (submission_id, level, message) VALUES (?,?,?)",
        (sid, level, msg),
    )