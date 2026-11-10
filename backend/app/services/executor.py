import subprocess
import time
import tempfile
import shutil
import os
from pathlib import Path
from typing import Any

from app.config import settings

# Map language names to their image names and run commands
LANG_CONFIG = {
    "python": {
        "image": "codearnax-python:latest",
        "filename": "main.py",
        "cmd": ["main.py"]
    },
    "javascript": {
        "image": "codearnax-javascript:latest",
        "filename": "main.js",
        "cmd": ["main.js"]
    },
    "cpp": {
        "image": "codearnax-cpp:latest",
        "filename": "main.cpp",
        "cmd": ["bash", "-c", "g++ -O2 main.cpp -o main && ./main"]
    }
}

class ExecutionResult:
    def __init__(self, status: str, stdout: str, stderr: str, duration_ms: float, exit_code: int):
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.exit_code = exit_code

def run_code(language: str, source_code: str, stdin_data: str, time_limit_ms: int) -> ExecutionResult:
    if language not in LANG_CONFIG:
        return ExecutionResult("InternalError", "", "Unsupported language", 0, -1)

    cfg = LANG_CONFIG[language]
    
    # Create a temporary directory for this specific run
    temp_dir = tempfile.mkdtemp(prefix="codearnax_run_")
    try:
        # Write source code to file
        file_path = Path(temp_dir) / cfg["filename"]
        file_path.write_text(source_code, encoding="utf-8")

        # Prepare docker command
        # Security flags: --network none, --memory, --cpus, --read-only (with tmpfs for /tmp)
        cmd = [
            "docker", "run", "--rm", "-i",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "1.0",
            "--read-only",
            "--tmpfs", "/tmp",
            "-v", f"{temp_dir}:/work",
            "-w", "/work",
            cfg["image"]
        ] + cfg["cmd"]

        start_time = time.perf_counter()
        
        try:
            # Execute with timeout (add 1 second buffer for Docker overhead)
            process = subprocess.run(
                cmd,
                input=stdin_data,
                text=True,
                capture_output=True,
                timeout=(time_limit_ms / 1000.0) + 1.0
            )
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.returncode

            # Determine status
            if exit_code == 0:
                status = "Accepted"
            elif exit_code == 137:  # SIGKILL, usually OOM
                status = "MemoryLimitExceeded"
            elif language == "cpp" and "error:" in stderr:
                status = "CompilationError"
            else:
                status = "RuntimeError"

            return ExecutionResult(status, stdout, stderr, duration_ms, exit_code)

        except subprocess.TimeoutExpired:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return ExecutionResult("TimeLimitExceeded", "", "Execution timed out", duration_ms, -1)

    finally:
        # Clean up temp workspace
        shutil.rmtree(temp_dir, ignore_errors=True)