#!/usr/bin/env python3
"""Check publishable files; print rule IDs and locations, never matched values.

This complements Gitleaks. It cannot establish that all private information is
absent. Git files include untracked additions but exclude ignored runtime data.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP_DIRS = {".git", ".venv", "node_modules", ".dart_tool", "build", "__pycache__", ".pytest_cache", ".ruff_cache"}
PRIVATE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".sqlite", ".sqlite3", ".db", ".dump"}
PATTERNS = {
    "personal-path": re.compile(r"/(?:Users|home)/[^/\s]+/"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "cloud-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bAIza[\w-]{35}\b"),
    "server-token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|gsk_[A-Za-z0-9]{30,}|sk-(?:proj-)?[\w-]{30,})\b"),
}


def candidate_files(root: Path) -> list[Path]:
    """Use Git's ignored-file boundary when root is itself a checkout."""
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
            timeout=10,
        )
        return [root / value.decode() for value in result.stdout.split(b"\0") if value]
    return [path for path in root.rglob("*") if not set(path.relative_to(root).parts) & SKIP_DIRS]


def scan_tree(root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(set(candidate_files(root))):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in PRIVATE_SUFFIXES or (path.name.startswith(".env") and path.name != ".env.example"):
            findings.append(f"{relative}: forbidden-file")
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
            for rule, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{relative}:{number}: {rule}")
            if path.suffix == ".md":
                for link in re.finditer(r"\[[^\]]*\]\(([^\s)]+)\)", line):
                    target = link.group(1)
                    if target.startswith("#") or urlsplit(target).scheme:
                        continue
                    local = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                    if not local.is_relative_to(root) or not local.exists():
                        findings.append(f"{relative}:{number}: broken-link")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    findings = scan_tree(args.root.resolve())
    for finding in findings:
        print(finding)
    print(f"Publication checks: {len(findings)} finding(s)")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
