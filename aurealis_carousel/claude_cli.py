"""Subprocess wrapper around the `claude` CLI binary.

Each phase module that needs Claude calls query() or query_json() from here.
Calls are single-shot (--max-turns 1) and return parsed JSON envelopes.
This is the ONLY module in the codebase that shells out to `claude`.

Prompts are passed via stdin (not as positional argv) because the CLI's
--allowedTools flag is variadic and would otherwise greedily consume the
prompt as part of the tools list, leaving no positional input.
"""
import json
import os
import shutil
import subprocess
from typing import Optional

CLAUDE_TIMEOUT_SECONDS = 360   # large prompts (full brief + 4 playbooks) routinely take 2-4 min on Opus 4.7
DEFAULT_MODEL = "claude-opus-4-7"


class ClaudeCLIError(Exception):
    pass


def ensure_available() -> str:
    path = shutil.which("claude")
    if not path:
        raise ClaudeCLIError("'claude' binary is not on PATH. Install Claude Code first.")
    return path


def query(
    prompt: str,
    model: str = DEFAULT_MODEL,
    allowed_tools: Optional[list[str]] = None,
    max_turns: int = 1,
    timeout: int = CLAUDE_TIMEOUT_SECONDS,
) -> str:
    ensure_available()
    cmd = [
        "claude", "-p",
        "--model", model,
        "--max-turns", str(max_turns),
        "--output-format", "json",
        # Hermetic subprocess: ignore all globally-configured MCP servers (figma, notion,
        # vercel, etc.) that would otherwise leak in as available tools. Without this,
        # Claude can opportunistically call `mcp__figma__...` and burn `--max-turns` on
        # `tool_use` exits — even when --tools "" disables built-ins.
        "--strict-mcp-config",
    ]
    # Tool-availability semantics:
    #   allowed_tools is None  → all built-in tools disabled (pure text → JSON call)
    #   allowed_tools = [...]  → restrict to only those tools
    # Disabling tools is critical for phases like strategist + designer where
    # Claude can otherwise burn `--max-turns` on opportunistic tool_use calls
    # (Read, Bash, etc.) and exit with `error_max_turns` instead of returning.
    if allowed_tools is None:
        cmd += ["--tools", ""]
    elif allowed_tools:
        cmd += ["--allowedTools", ",".join(allowed_tools)]
    env = os.environ.copy()
    env["AUREALIS_PIPELINE_RUN"] = "1"
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, env=env)
    if proc.returncode != 0:
        raise ClaudeCLIError(
            f"claude exited {proc.returncode}.\n"
            f"  stderr: {proc.stderr.strip()[:500] or '(empty)'}\n"
            f"  stdout: {proc.stdout.strip()[:500] or '(empty)'}\n"
            f"  cmd: {' '.join(cmd[:8])}{'...' if len(cmd) > 8 else ''}"
        )
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ClaudeCLIError(f"non-JSON envelope from claude: {proc.stdout[:500]}") from e
    if envelope.get("is_error"):
        raise ClaudeCLIError(f"claude reported error: {envelope.get('result')}")
    return envelope.get("result", "")


def query_json(prompt: str, **kwargs) -> dict:
    raw = query(prompt, **kwargs).strip()
    if raw.startswith("```"):
        lines = [line for line in raw.split("\n") if not line.startswith("```")]
        raw = "\n".join(lines).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError as e:
                raise ClaudeCLIError(
                    f"could not parse JSON from claude response: {raw[:500]}"
                ) from e
        raise ClaudeCLIError(f"could not parse JSON from claude response: {raw[:500]}")
