# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""Shared HTTP + OAuth helpers for Salik / DARB toll API clients."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, now_datetime


class TollAPIError(Exception):
	pass


def _base_url(provider) -> str:
	url = (provider.endpoint_url or "").strip().rstrip("/")
	if not url and not cint_sandbox(provider):
		raise TollAPIError(_("API Base URL is required for provider {0}").format(provider.provider_code))
	return url


def cint_sandbox(provider) -> bool:
	return bool(getattr(provider, "sandbox_mode", 0))


def build_auth_headers(provider) -> dict[str, str]:
	headers = {"Accept": "application/json", "Content-Type": "application/json"
	}
	if provider.auth_token:
		token = provider.get_password("auth_token")
		header_name = (provider.auth_header_name or "Authorization").strip()
		if header_name.lower() == "authorization" and token and not str(token).lower().startswith("bearer "):
			token = f"Bearer {token}"
		headers[header_name] = token
	return headers


def refresh_oauth_token_if_needed(provider) -> None:
	"""Client-credentials token refresh when oauth_token_url + client_id are set."""
	if not getattr(provider, "oauth_token_url", None) or not getattr(provider, "client_id", None):
		return
	if not getattr(provider, "client_secret", None):
		return

	import requests

	secret = provider.get_password("client_secret")
	resp = requests.post(
		provider.oauth_token_url,
		data={
			"grant_type": "client_credentials",
			"client_id": provider.client_id,
			"client_secret": secret
	},
		timeout=30,
	)
	if resp.status_code >= 400:
		raise TollAPIError(_("OAuth token request failed ({0}): {1}").format(resp.status_code, resp.text[:200]))
	data = resp.json()
	token = data.get("access_token")
	if not token:
		raise TollAPIError(_("OAuth response missing access_token"))
	provider.auth_token = token
	provider.auth_header_name = provider.auth_header_name or "Authorization"
	provider.save(ignore_permissions=True)
	frappe.db.commit()


def http_get_json(provider, path: str, params: dict | None = None) -> Any:
	refresh_oauth_token_if_needed(provider)
	import requests

	url = urljoin(_base_url(provider) + "/", path.lstrip("/"))
	resp = requests.get(url, headers=build_auth_headers(provider), params=params or {}, timeout=45)
	if resp.status_code >= 400:
		raise TollAPIError(_("GET {0} failed ({1}): {2}").format(path, resp.status_code, resp.text[:300]))
	try:
		return resp.json()
	except Exception as exc:
		raise TollAPIError(_("Invalid JSON from {0}: {1}").format(path, exc)) from exc


def should_poll_provider(provider) -> bool:
	if not provider.is_active or provider.integration_type != "API Polling":
		return False
	interval = int(provider.poll_interval_minutes or 15)
	if not provider.last_poll_at:
		return True
	next_poll = add_to_date(get_datetime(provider.last_poll_at), minutes=interval, as_datetime=True)
	return get_datetime(now_datetime()) >= get_datetime(next_poll)


def extract_transaction_list(payload: Any) -> list[dict]:
	"""Normalize common Salik/DARB list response envelopes."""
	if isinstance(payload, list):
		return [x for x in payload if isinstance(x, dict)]
	if not isinstance(payload, dict):
		return []
	for key in (
		"transactions",
		"tollTransactions",
		"data",
		"passages",
		"items",
		"results",
		"records",
	):
		val = payload.get(key)
		if isinstance(val, list):
			return [x for x in val if isinstance(x, dict)]
		if isinstance(val, dict):
			for nested in ("transactions", "passages", "items"):
				inner = val.get(nested)
				if isinstance(inner, list):
					return [x for x in inner if isinstance(x, dict)]
	return []


def cursor_from_payload(payload: Any, fallback: str | None = None) -> str | None:
	if isinstance(payload, dict):
		for key in ("next_cursor", "nextCursor", "cursor", "nextPageToken", "sync_token"):
			if payload.get(key):
				return str(payload[key])
		if payload.get("hasMore") is False and payload.get("lastId"):
			return str(payload["lastId"])
	return fallback
