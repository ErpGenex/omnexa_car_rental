# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Salik / DARB connection test, manual sync, integration status."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_car_rental.omnexa_car_rental.toll.toll_polling import poll_all_active, poll_provider, test_provider_connection


@frappe.whitelist()
def test_salik_connection() -> dict:
	return test_provider_connection("SALIK")


@frappe.whitelist()
def test_darb_connection() -> dict:
	return test_provider_connection("DARB")


@frappe.whitelist()
def sync_toll_provider(provider_code: str, force: int = 1) -> dict:
	code = (provider_code or "").strip().upper()
	name = frappe.db.get_value("Toll Provider", {"provider_code": code}, "name")
	if not name:
		frappe.throw(_("Toll Provider not found: {0}").format(code))
	return poll_provider(name, force=bool(int(force)))


@frappe.whitelist()
def sync_all_toll_providers(force: int = 1) -> dict:
	results = poll_all_active(force=bool(int(force)))
	return {"ok": True, "results": results}


@frappe.whitelist()
def get_toll_integration_status() -> dict:
	providers = frappe.get_all(
		"Toll Provider",
		filters={"provider_code": ["in", ["SALIK", "DARB"]]},
		fields=[
			"name",
			"provider_code",
			"provider_name",
			"integration_type",
			"is_active",
			"sandbox_mode",
			"endpoint_url",
			"last_poll_at",
			"last_sync_token",
		],
	)
	return {
		"webhook_url": "/api/method/omnexa_car_rental.toll_webhook.ingest",
		"providers": providers,
		"scheduler": "poll_toll_providers every 15 min",
	}
