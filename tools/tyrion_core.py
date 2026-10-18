#!/usr/bin/env python3
"""Tyrion Production Core (`tyrion_core.py`) — Atomic I/O, Input Sanitization, Safe Numeric Parsing,
Path Traversal Guards, Secret Redaction, and Exponential Backoff HTTP Client (0 external dependencies).
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MAX_FILE_BYTES: int = 25 * 1024 * 1024  # 25 MB hard ceiling for CSV/JSON imports
MAX_RPC_LINE_BYTES: int = 1 * 1024 * 1024  # 1 MB hard ceiling for STDIO JSON-RPC lines

SECRET_REDACT_RE = re.compile(
    r"(EAA[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}|\b\d{8,10}:AA[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,})"
)
SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")
CONTROL_AND_TAG_RE = re.compile(r"[\x00-\x1f\x7f<>\"'`\\]")


def redact_secrets(text: str) -> str:
    """Har qanday xato xabari yoki log ichidan API tokenlarni to'liq yashiradi."""
    if not text:
        return ""
    return SECRET_REDACT_RE.sub("[REDACTED_SECRET]", str(text))


def safe_float(
    value: Any,
    default: float = 0.0,
    min_val: float | None = None,
    max_val: float | None = None,
    field_name: str = "value",
) -> float:
    """NaN, Infinity, manfiy yoki buzilgan satrlardan himoyalangan float parser."""
    if value is None or isinstance(value, bool):
        res = default
    elif isinstance(value, (int, float)):
        res = float(value)
    else:
        cleaned = str(value).replace("$", "").replace(",", "").replace("%", "").replace(" ", "").strip()
        try:
            res = float(cleaned) if cleaned else default
        except ValueError:
            res = default

    if not math.isfinite(res):
        res = default
    if min_val is not None and res < min_val:
        raise ValueError(f"'{field_name}' kamida {min_val} bo'lishi shart (berildi: {res})")
    if max_val is not None and res > max_val:
        raise ValueError(f"'{field_name}' ko'pi bilan {max_val} bo'lishi shart (berildi: {res})")
    return res


def safe_int(
    value: Any,
    default: int = 0,
    min_val: int | None = None,
    max_val: int | None = None,
    field_name: str = "value",
) -> int:
    """NaN, Infinity va diapazondan tashqari qiymatlardan himoyalangan int parser."""
    fval = safe_float(value, default=float(default), field_name=field_name)
    res = int(round(fval))
    if min_val is not None and res < min_val:
        raise ValueError(f"'{field_name}' kamida {min_val} bo'lishi shart (berildi: {res})")
    if max_val is not None and res > max_val:
        raise ValueError(f"'{field_name}' ko'pi bilan {max_val} bo'lishi shart (berildi: {res})")
    return res


def safe_slug(value: str, fallback: str = "unnamed-project", max_len: int = 48) -> str:
    """Path traversal (`../`) va bo'sh slug'lardan 100% himoyalangan identifikator."""
    raw = SAFE_SLUG_RE.sub("-", str(value or "").lower()).strip("-")[:max_len].strip("-")
    return raw if raw else fallback


def sanitize_url(url: str) -> str:
    """XSS (`javascript:`, `data:`) va CRLF injection'dan himoyalangan URL tekshiruvi."""
    cleaned = re.sub(r"[\r\n\t\x00-\x1f]", "", str(url or "").strip())
    parsed = urllib.parse.urlsplit(cleaned)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Xavfsiz bo'lmagan URL sxemasi: '{parsed.scheme}'. Faqat http/https ruxsat etiladi.")
    if not parsed.netloc:
        raise ValueError("URL domeni (netloc) ko'rsatilmagan.")
    return cleaned


def validate_safe_path(target: Path, allowed_root: Path | None = None) -> Path:
    """Symlink yoki `..` orqali ruxsat etilgan papkadan chiqib ketishni (Path Traversal) bloklaydi."""
    resolved = target.resolve()
    if allowed_root is not None:
        root_resolved = allowed_root.resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            raise PermissionError(f"Xavfsizlik xatosi: '{target}' ruxsat etilgan '{root_resolved}' hududidan tashqarida!")
    return resolved


def atomic_write_bytes(target: Path, data: bytes) -> None:
    """Jarayonlararo poyga (race condition) va yarim yozilgan fayllarni oldini oluvchi atomik yozish."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass
        os.replace(str(tmp_path), str(target))
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def atomic_write_text(target: Path, text: str, encoding: str = "utf-8") -> None:
    """Matnli faylni atomik tarzda (`temp -> fsync -> os.replace`) yozadi."""
    atomic_write_bytes(target, text.encode(encoding))


def atomic_write_json(target: Path, payload: Any) -> None:
    """JSON faylni NaN/Infinity'siz tekshirib, atomik tarzda yozadi."""
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    atomic_write_text(target, serialized, encoding="utf-8")


def http_get_json_with_backoff(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 8.0,
    max_retries: int = 3,
    base_delay: float = 0.6,
) -> dict[str, Any]:
    """HTTP 429 (Rate Limit) va 5xx xatolarida eksponensial backoff + jitter bilan so'rov yuboradi.
    Hech qachon URL ichida maxfiy tokenlarni oshkor qilmaydi.
    """
    clean_url = sanitize_url(url)
    req_headers = {"Accept": "application/json", "User-Agent": "Tyrion-OS/4.1"}
    if headers:
        req_headers.update(headers)

    last_err: str = "Noma'lum tarmoq xatosi"
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(clean_url, headers=req_headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(MAX_FILE_BYTES).decode("utf-8", errors="replace")
                data = json.loads(raw)
                return data if isinstance(data, dict) else {"data": data}
        except urllib.error.HTTPError as exc:
            status = exc.code
            body_preview = ""
            try:
                body_preview = redact_secrets(exc.read(2048).decode("utf-8", errors="replace"))
            except Exception:
                pass
            last_err = f"HTTP {status}: {redact_secrets(str(exc.reason))} {body_preview[:160]}".strip()
            # Retry on 429 Too Many Requests or 5xx transient errors
            if status in (429, 500, 502, 503, 504) and attempt < max_retries:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                delay = safe_float(retry_after, default=base_delay * (2 ** attempt)) + random.uniform(0.05, 0.25)
                time.sleep(min(delay, 5.0))
                continue
            break
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            last_err = redact_secrets(str(exc))
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt) + random.uniform(0.05, 0.25)
                time.sleep(min(delay, 5.0))
                continue
            break

    return {"error": last_err, "retries_attempted": max_retries}
