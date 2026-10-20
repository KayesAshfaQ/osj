"""Stable source and provision identities shared by ingestion and indexing."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Mapping
from urllib.parse import urlsplit, urlunsplit


def source_identity(act: Mapping[str, object]) -> str:
    explicit = str(act.get("source_id") or act.get("id") or "").strip()
    if explicit:
        return explicit
    source_url = str(act.get("source_url") or "").strip()
    if source_url:
        url = urlsplit(source_url)
        if not url.netloc:
            raise ValueError("Invalid source URL")
        canonical = urlunsplit((url.scheme.lower(), url.netloc.lower(), url.path.rstrip("/"), url.query, ""))
        return "url:" + hashlib.sha256(canonical.encode()).hexdigest()
    title = str(act.get("act_title") or act.get("law_name_en") or "").strip().casefold()
    year = str(act.get("act_year") or "").strip()
    number = str(act.get("act_no") or "").strip().casefold()
    if not title:
        raise ValueError("Source requires an ID, URL, or Act title")
    return "act:" + hashlib.sha256(f"{title}|{year}|{number}".encode()).hexdigest()


def provision_identity(source_id: str, provision: str) -> str:
    if not source_id or not provision.strip():
        raise ValueError("Provision identity requires source and number")
    return f"{source_id}:{provision.strip().casefold()}"


def child_identity(parent_id: str, content: str, position: int) -> str:
    digest = hashlib.sha256(content.encode()).hexdigest()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{parent_id}:{digest}:{position}"))
