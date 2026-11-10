import asyncio
import time
from typing import Any

from app.api.websockets import manager
from app.db.init import connect
from app.services.executor import run_code


class JobQueue:
    def __init__(self) -> None:
        self._q: asyncio.Queue[int] = asyncio.Queue()
        self._running = False
        self._task: asyncio.Task | None = None

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
            # Fetching user_id (index 5) for leaderboard scoring
            sub = conn.execute(
                "SELECT id, challenge_id, language, source_code, status, user_id FROM submissions WHERE id = ?",
                (submission_id,),
            ).fetchone()
            
            if sub is None or sub[4] != "Queued":
                return

            conn.execute(
                "UPDATE submissions SET status = 'Running' WHERE id = ?",
                (submission_id,),
            )
            
            await manager.broadcast({
                "event": "submission_update",
                "submission_id": submission_id,
                "status": "Running"
            })
            
            tests = conn.execute(
                "SELECT id, input, expected_output FROM test_cases WHERE challenge_id = ? ORDER BY id",
                (sub[1],),
            ).fetchall()
            
            limits = conn.execute(
                "SELECT time_limit_ms FROM challenges WHERE id = ?",
                (sub[1],),
            ).fetchone()
            time_limit = limits[0] if limits else 2000
        finally:
            conn.close()

        self._log(submission_id, "info", f"job started: {submission_id} (lang={sub[2]})")
        t0 = time.perf_counter()
        overall_status = "Accepted"

        if not tests:
            self._log(submission_id, "error", "No test cases found for challenge")
            conn = connect()
            conn.execute("UPDATE submissions SET status = 'InternalError' WHERE id = ?", (submission_id,))
            conn.close()
            return

        for tc_id, tc_input, tc_expected in tests:
            result = await asyncio.to_thread(
                run_code, sub[2], sub[3], tc_input, time_limit
            )
            
            passed = False
            if result.status == "Accepted":
                if result.stdout.strip() == tc_expected.strip():
                    passed = True
                else:
                    result.status = "WrongAnswer"
            
            if result.status != "Accepted" and overall_status == "Accepted":
                overall_status = result.status

            conn = connect()
            try:
                conn.execute(
                    """INSERT INTO execution_results 
                       (submission_id, test_case_id, passed, actual_output, duration_ms, memory_kb, exit_code, stderr)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (submission_id, tc_id, int(passed), result.stdout, result.duration_ms, 0.0, result.exit_code, result.stderr)
                )
            finally:
                conn.close()

            if not passed:
                break

        ms = (time.perf_counter() - t0) * 1000
        self._log(submission_id, "info", f"job finished in {ms:.0f} ms. Status: {overall_status}")

        conn = connect()
        try:
            conn.execute(
                "UPDATE submissions SET status = ? WHERE id = ?",
                (overall_status, submission_id),
            )
            if overall_status == "Accepted":
                self._award_points(sub, conn)
        finally:
            conn.close()

        await manager.broadcast({
            "event": "submission_update",
            "submission_id": submission_id,
            "status": overall_status
        })

    def _award_points(self, sub: tuple, conn: Any) -> None:
        difficulty_scores = {
            "Beginner": 10,
            "Intermediate": 20,
            "Advanced": 30,
            "Expert": 40
        }
        
        try:
            ch = conn.execute("SELECT difficulty FROM challenges WHERE id = ?", (sub[1],)).fetchone()
            if not ch:
                self._log(sub[0], "error", "Challenge not found for leaderboard")
                return
            
            points = difficulty_scores.get(ch[0], 10)
            user_id = sub[5]
            challenge_id = sub[1]
            
            conn.execute(
                "INSERT OR IGNORE INTO leaderboard (candidate_id, challenge_id, score) VALUES (?, ?, ?)",
                (user_id, challenge_id, points)
            )
            conn.commit() # Force write to disk
            self._log(sub[0], "info", f"Awarded {points} points to user {user_id}")
        except Exception as e:
            self._log(sub[0], "error", f"Leaderboard error: {e}")


queue = JobQueue()