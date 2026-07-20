# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""HTTP webhook entry for toll authorities (Salik, DARB, etc.)."""

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit


def _extract_signature() -> str | None:
	for header in (
		"X-Omnexa-Signature",
		"X-Signature",
		"X-Salik-Signature",
		"X-DARB-Signature",
		"X-Hub-Signature-256",
	):
		val = frappe.get_request_header(header)
		if val:
			return val
	return None


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=300, seconds=60)
def ingest():
	"""POST JSON body with ?provider_code=SALIK or ?provider_code=DARB"""
	provider_code = frappe.form_dict.get("provider_code") or frappe.request.args.get("provider_code")
	if not provider_code:
		frappe.throw(_("provider_code is required (SALIK or DARB)"), exc=frappe.ValidationError)

	raw = frappe.request.get_data(as_text=True)
	sig = _extract_signature()

	from omnexa_car_rental.omnexa_car_rental.toll.toll_ingestion import ingest_payload

	return ingest_payload(provider_code, raw, signature_header=sig, auto_match=True, auto_bill=False)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def health():
	"""Lightweight health check for Salik/DARB webhook endpoints."""
	return {"ok": True, "service": "omnexa-toll-webhook", "providers": ["SALIK", "DARB"]}
