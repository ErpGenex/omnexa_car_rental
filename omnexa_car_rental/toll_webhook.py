# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""HTTP webhook entry for toll authorities (Salik, DARB, etc.)."""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True, methods=["POST"])
def ingest():
	provider_code = frappe.form_dict.get("provider_code") or frappe.request.args.get("provider_code")
	if not provider_code:
		frappe.throw(_("provider_code is required"), exc=frappe.ValidationError)

	raw = frappe.request.get_data(as_text=True)
	sig = frappe.get_request_header("X-Omnexa-Signature") or frappe.get_request_header("X-Signature")

	from omnexa_car_rental.omnexa_car_rental.toll.toll_ingestion import ingest_payload

	return ingest_payload(provider_code, raw, signature_header=sig, auto_match=True, auto_bill=False)
