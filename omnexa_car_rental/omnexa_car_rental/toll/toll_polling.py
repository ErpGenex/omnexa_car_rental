# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""Poll Salik/DARB and ingest toll transactions."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime

from omnexa_car_rental.omnexa_car_rental.toll.darb_client import DarbClient
from omnexa_car_rental.omnexa_car_rental.toll.salik_client import SalikClient
from omnexa_car_rental.omnexa_car_rental.toll.toll_api_base import TollAPIError, should_poll_provider
from omnexa_car_rental.omnexa_car_rental.toll.toll_ingestion import ingest_dict


def get_client(provider):
	code = (provider.provider_code or "").strip().upper()
	if code == "SALIK":
		return SalikClient(provider)
	if code == "DARB":
		return DarbClient(provider)
	raise TollAPIError(_("No API client for provider code {0}").format(code))


def poll_provider(provider_name: str, *, force: bool = False) -> dict:
	provider = frappe.get_doc("Toll Provider", provider_name)
	if not provider.is_active:
		return {"ok": False, "skipped": True, "reason": "inactive"}
	if provider.integration_type != "API Polling":
		return {"ok": False, "skipped": True, "reason": "not polling"}
	if not force and not should_poll_provider(provider):
		return {"ok": True, "skipped": True, "reason": "interval"}

	client = get_client(provider)
	cursor = provider.last_sync_token or ""
	try:
		rows, next_cursor = client.fetch_since(cursor or None)
	except TollAPIError as exc:
		frappe.log_error(title=f"Toll poll failed: {provider.provider_code}", message=str(exc))
		return {"ok": False, "error": str(exc)}

	ingested = 0
	duplicates = 0
	errors: list[str] = []
	company = frappe.defaults.get_global_default("company") or (frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company", limit=1) else None)
	branch = frappe.db.get_value("Branch", {"company": company}, "name") if company else None
	for row in rows:
		if company and not row.get("company"):
			row["company"] = company
		if branch and not row.get("branch"):
			row["branch"] = branch
		try:
			result = ingest_dict(provider, row, auto_match=True, auto_bill=False)
			if result.get("duplicate"):
				duplicates += 1
			else:
				ingested += 1
		except Exception as exc:
			errors.append(str(exc))

	provider.last_poll_at = now_datetime()
	if next_cursor:
		provider.last_sync_token = next_cursor
	provider.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"ok": True,
		"provider": provider.provider_code,
		"fetched": len(rows),
		"ingested": ingested,
		"duplicates": duplicates,
		"errors": errors[:5],
		"next_cursor": next_cursor,
	}


def poll_all_active(*, force: bool = False) -> list[dict]:
	results = []
	for name in frappe.get_all(
		"Toll Provider",
		filters={"integration_type": "API Polling", "is_active": 1},
		pluck="name",
	):
		code = frappe.db.get_value("Toll Provider", name, "provider_code")
		if (code or "").upper() not in ("SALIK", "DARB"):
			continue
		results.append(poll_provider(name, force=force))
	return results


def test_provider_connection(provider_code: str) -> dict:
	name = frappe.db.get_value("Toll Provider", {"provider_code": provider_code.strip().upper()}, "name")
	if not name:
		frappe.throw(_("Toll Provider not found: {0}").format(provider_code))
	provider = frappe.get_doc("Toll Provider", name)
	client = get_client(provider)
	return client.test_connection()
