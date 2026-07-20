# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""ITC Abu Dhabi DARB toll API client (polling + connection test)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from frappe.utils import get_datetime, now_datetime

from omnexa_car_rental.omnexa_car_rental.toll.toll_api_base import (
	cint_sandbox,
	cursor_from_payload,
	extract_transaction_list,
	http_get_json,
)

DEFAULT_TX_PATH = "/api/v1/passages"
DEFAULT_BASE = "https://api.darb.ae/fleet"


class DarbClient:
	def __init__(self, provider):
		self.provider = provider

	def fetch_since(self, cursor: str | None = None) -> tuple[list[dict], str | None]:
		if cint_sandbox(self.provider):
			return self._sandbox_transactions(cursor)
		path = getattr(self.provider, "api_transactions_path", None) or DEFAULT_TX_PATH
		params: dict[str, Any] = {"page_size": 200
	}
		if cursor:
			params["since"] = cursor
		payload = http_get_json(self.provider, path, params)
		rows = extract_transaction_list(payload)
		next_cursor = cursor_from_payload(payload, fallback=_cursor_from_rows(rows, cursor))
		return rows, next_cursor

	def test_connection(self) -> dict:
		if cint_sandbox(self.provider):
			return {"ok": True, "mode": "sandbox", "provider": "DARB", "message": "Sandbox ready"
	}
		path = getattr(self.provider, "api_transactions_path", None) or DEFAULT_TX_PATH
		payload = http_get_json(self.provider, path, {"page_size": 1
	})
		count = len(extract_transaction_list(payload))
		return {"ok": True, "mode": "live", "provider": "DARB", "sample_count": count
	}

	def _sandbox_transactions(self, cursor: str | None) -> tuple[list[dict], str | None]:
		base = get_datetime(now_datetime()) - timedelta(minutes=45)
		offset = int(cursor) if cursor and str(cursor).isdigit() else 0
		if offset >= 3:
			return [], str(offset)
		idx = offset + 1
		rows = [
			{
				"trans_id": f"DARB-SBX-{idx:04d
	}",
				"passage_time": (base + timedelta(minutes=idx * 7)).isoformat(),
				"toll_fee": 4.0,
				"currency": "AED",
				"licensePlate": f"AUH-{2000 + idx
	}",
				"obu_id": f"TAG-DARB-{idx:03d
	}",
				"checkpoint": "Sheikh Zayed Bridge",
				"checkpoint_code": f"DARB-G{idx}"
	}
		]
		return rows, str(idx)


def _cursor_from_rows(rows: list[dict], prev: str | None) -> str | None:
	if not rows:
		return prev
	last = rows[-1]
	for key in ("trans_id", "transaction_id", "id"):
		if last.get(key):
			return str(last[key])
	dt = last.get("passage_time") or last.get("crossing_datetime")
	return str(dt) if dt else prev


def default_darb_config() -> dict:
	return {
		"provider_code": "DARB",
		"provider_name": "ITC DARB",
		"integration_type": "API Polling",
		"endpoint_url": DEFAULT_BASE,
		"api_transactions_path": DEFAULT_TX_PATH,
		"default_currency": "AED",
		"default_country": "AE",
		"poll_interval_minutes": 15,
		"auth_header_name": "Authorization",
		"sandbox_mode": 1,
		"is_active": 1,
		"notes": "DARB fleet API. Set auth_token or oauth_token_url+client_id for live ITC access."
	}
