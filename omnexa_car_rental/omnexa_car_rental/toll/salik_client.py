# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""RTA Salik fleet toll API client (polling + connection test)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import frappe
from frappe.utils import get_datetime, now_datetime

from omnexa_car_rental.omnexa_car_rental.toll.toll_api_base import (
	TollAPIError,
	cint_sandbox,
	cursor_from_payload,
	extract_transaction_list,
	http_get_json,
)

DEFAULT_TX_PATH = "/v1/toll-transactions"
DEFAULT_BASE = "https://api.salik.ae/fleet"


class SalikClient:
	def __init__(self, provider):
		self.provider = provider

	def fetch_since(self, cursor: str | None = None) -> tuple[list[dict], str | None]:
		if cint_sandbox(self.provider):
			return self._sandbox_transactions(cursor)
		path = getattr(self.provider, "api_transactions_path", None) or DEFAULT_TX_PATH
		params: dict[str, Any] = {"limit": 200
	}
		if cursor:
			if cursor.isdigit() or "T" in cursor:
				params["since"] = cursor
			else:
				params["cursor"] = cursor
		payload = http_get_json(self.provider, path, params)
		rows = extract_transaction_list(payload)
		next_cursor = cursor_from_payload(payload, fallback=_cursor_from_rows(rows, cursor))
		return rows, next_cursor

	def test_connection(self) -> dict:
		if cint_sandbox(self.provider):
			return {"ok": True, "mode": "sandbox", "provider": "SALIK", "message": "Sandbox ready"
	}
		path = getattr(self.provider, "api_transactions_path", None) or DEFAULT_TX_PATH
		payload = http_get_json(self.provider, path, {"limit": 1
	})
		count = len(extract_transaction_list(payload))
		return {"ok": True, "mode": "live", "provider": "SALIK", "sample_count": count
	}

	def _sandbox_transactions(self, cursor: str | None) -> tuple[list[dict], str | None]:
		"""Deterministic demo feed when sandbox_mode is enabled."""
		base = get_datetime(now_datetime()) - timedelta(minutes=30)
		tag_base = cursor or "0"
		offset = int(tag_base) if str(tag_base).isdigit() else 0
		if offset >= 3:
			return [], str(offset)
		idx = offset + 1
		rows = [
			{
				"transactionId": f"SALIK-SBX-{idx:04d}",
				"transactionDateTime": (base + timedelta(minutes=idx * 5)).isoformat(),
				"tollAmount": 4.0,
				"currencyCode": "AED",
				"plateNumber": f"DXB-{1000 + idx}",
				"salikTagId": f"TAG-SALIK-{idx:03d}",
				"gateName": "Al Barsha",
				"gateCode": f"SAL-G{idx}",
				"countryCode": "AE"
	}
		]
		return rows, str(idx)


def _cursor_from_rows(rows: list[dict], prev: str | None) -> str | None:
	if not rows:
		return prev
	last = rows[-1]
	for key in ("transactionId", "transaction_id", "id"):
		if last.get(key):
			return str(last[key])
	dt = last.get("transactionDateTime") or last.get("crossing_datetime")
	return str(dt) if dt else prev


def default_salik_config() -> dict:
	return {
		"provider_code": "SALIK",
		"provider_name": "RTA Salik",
		"integration_type": "API Polling",
		"endpoint_url": DEFAULT_BASE,
		"api_transactions_path": DEFAULT_TX_PATH,
		"default_currency": "AED",
		"default_country": "AE",
		"poll_interval_minutes": 15,
		"auth_header_name": "Authorization",
		"sandbox_mode": 1,
		"is_active": 1,
		"notes": "Salik fleet API. Set auth_token or oauth_token_url+client_id for live RTA access."
	}
