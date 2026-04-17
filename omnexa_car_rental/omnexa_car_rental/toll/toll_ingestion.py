# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe.utils import get_datetime

from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import (
	apply_fx_to_company_currency,
	create_recharge_sales_invoice,
	find_duplicate_event,
	run_matching,
)
from omnexa_car_rental.omnexa_car_rental.toll.toll_adapters import adapt_provider_payload
from omnexa_car_rental.omnexa_car_rental.toll.toll_util import verify_webhook_signature


def _provider_doc(provider_code: str) -> frappe.model.document.Document:
	name = frappe.db.get_value("Toll Provider", {"provider_code": provider_code.strip().upper()}, "name")
	if not name:
		frappe.throw(frappe._("Unknown Toll Provider: {0}").format(provider_code))
	doc = frappe.get_doc("Toll Provider", name)
	if not doc.is_active:
		frappe.throw(frappe._("Toll Provider is inactive: {0}").format(provider_code))
	return doc


def _map_payload_to_row(data: dict, provider_name: str) -> dict[str, Any]:
	"""Normalize external JSON to Toll Transaction fields."""
	tx_id = data.get("transaction_id") or data.get("id") or data.get("reference")
	if not tx_id:
		frappe.throw(frappe._("transaction_id is required in payload"))

	crossing = data.get("crossing_datetime") or data.get("timestamp") or data.get("crossing_time")
	if not crossing:
		frappe.throw(frappe._("crossing_datetime is required in payload"))

	currency = data.get("currency")
	if not currency:
		frappe.throw(frappe._("currency is required in payload"))

	amount = data.get("amount")
	if amount is None:
		amount = data.get("toll_amount")
	if amount is None:
		frappe.throw(frappe._("amount is required in payload"))

	row = {
		"transaction_id": str(tx_id).strip(),
		"provider": provider_name,
		"plate_number": data.get("plate_number") or data.get("plate") or data.get("license_plate"),
		"tag_id": data.get("tag_id") or data.get("tag") or data.get("rfid"),
		"crossing_datetime": get_datetime(crossing),
		"entry_time": get_datetime(data["entry_time"]) if data.get("entry_time") else None,
		"exit_time": get_datetime(data["exit_time"]) if data.get("exit_time") else None,
		"toll_gate_name": data.get("toll_gate_name") or data.get("gate_name") or data.get("location"),
		"toll_gate_code": data.get("toll_gate_code") or data.get("gate_code"),
		"amount": float(amount),
		"currency": currency,
		"country": data.get("country"),
		"company": data.get("company"),
		"branch": data.get("branch"),
		"project": data.get("project"),
		"raw_payload": json.dumps(data, default=str),
		"status": "Received",
	}
	return row


def ingest_payload(
	provider_code: str,
	raw_body: str,
	*,
	signature_header: str | None = None,
	auto_match: bool = True,
	auto_bill: bool = False,
) -> dict[str, Any]:
	"""Create Toll Transaction from JSON body; optionally verify HMAC."""
	prov = _provider_doc(provider_code)
	if prov.webhook_secret and signature_header:
		sec = prov.get_password("webhook_secret")
		if not verify_webhook_signature(raw_body, sec, signature_header):
			frappe.throw(frappe._("Invalid webhook signature"), exc=frappe.ValidationError)

	try:
		data = json.loads(raw_body or "{}")
	except json.JSONDecodeError:
		frappe.throw(frappe._("Invalid JSON body"))

	if isinstance(data, list):
		results = []
		for row in data:
			results.append(ingest_dict(prov, row, auto_match=auto_match, auto_bill=auto_bill))
		return {"ok": True, "batch": True, "results": results}

	return ingest_dict(prov, data, auto_match=auto_match, auto_bill=auto_bill)


def ingest_dict(
	prov: frappe.model.document.Document,
	data: dict,
	*,
	auto_match: bool = True,
	auto_bill: bool = False,
) -> dict[str, Any]:
	data = adapt_provider_payload(prov.provider_code, dict(data))
	row = _map_payload_to_row(data, prov.name)
	if not row.get("country") and prov.default_country:
		row["country"] = prov.default_country
	if not row.get("currency") and prov.default_currency:
		row["currency"] = prov.default_currency

	vname = None
	if row.get("plate_number") or row.get("tag_id"):
		from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import resolve_vehicle

		vname, _ = resolve_vehicle(row.get("plate_number"), row.get("tag_id"))
	if vname:
		row["vehicle"] = vname
		comp_br = frappe.db.get_value("Vehicle", vname, ["company", "branch"], as_dict=True)
		if comp_br:
			row["company"] = row.get("company") or comp_br.company
			row["branch"] = row.get("branch") or comp_br.branch

	if not row.get("company") or not row.get("branch"):
		frappe.throw(
			frappe._(
				"company and branch are required when vehicle cannot be resolved. Supply them in the payload."
			)
		)

	if frappe.db.exists(
		"Toll Transaction",
		{"transaction_id": row["transaction_id"], "provider": prov.name},
	):
		return {"ok": True, "duplicate": True, "transaction_id": row["transaction_id"]}

	doc = frappe.get_doc({"doctype": "Toll Transaction", **row})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	if vname:
		dup = find_duplicate_event(
			vname,
			doc.toll_gate_code,
			doc.toll_gate_name,
			doc.crossing_datetime,
			prov.name,
			int(prov.deduplication_window_seconds or 120),
			exclude_name=doc.name,
		)
		if dup:
			doc.status = "Duplicate Ignored"
			doc.duplicate_of = dup
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			return {"ok": True, "name": doc.name, "status": doc.status, "duplicate_of": dup}

	apply_fx_to_company_currency(doc.name)

	if auto_match:
		run_matching(doc.name)
		doc.reload()
		if auto_bill and doc.status == "Rule Applied":
			create_recharge_sales_invoice(doc.name)

	return {"ok": True, "name": doc.name, "status": doc.status}


def ingest_batch_file(file_name: str, provider_code: str) -> dict[str, Any]:
	"""Load File attachment (JSON array or NDJSON) and ingest."""
	prov = _provider_doc(provider_code)
	file_doc = frappe.get_doc("File", file_name)
	path = file_doc.get_full_path()
	with open(path, encoding="utf-8") as fh:
		text = fh.read().strip()
	if not text:
		return {"ok": False, "error": "empty file"}

	if text.startswith("["):
		rows = json.loads(text)
	else:
		rows = [json.loads(line) for line in text.splitlines() if line.strip()]

	results = []
	for data in rows:
		if not isinstance(data, dict):
			continue
		results.append(ingest_dict(prov, data, auto_match=True, auto_bill=False))
	return {"ok": True, "count": len(results), "results": results}
