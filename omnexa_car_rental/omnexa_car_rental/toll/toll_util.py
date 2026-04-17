# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

from __future__ import annotations

import hashlib
import hmac


def normalize_plate(plate: str | None) -> str:
	if not plate:
		return ""
	s = plate.upper().strip()
	for ch in (" ", "-", ".", "/"):
		s = s.replace(ch, "")
	return s


def verify_webhook_signature(raw_body: str, secret: str | None, signature_header: str | None) -> bool:
	if not secret:
		return False
	if not signature_header:
		return False
	sig = signature_header.strip()
	if sig.lower().startswith("sha256="):
		sig = sig[7:]
	try:
		expected = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()
	except Exception:
		return False
	return hmac.compare_digest(expected.lower(), sig.lower())
