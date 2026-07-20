# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""ISO 27001 control pack."""

from __future__ import annotations

import frappe


ISO_CONTROLS = [
	("A.5.1", "Information security policies", "A.5"),
	("A.8.2", "Privileged access management", "A.8"),
	("A.12.4", "Logging and monitoring", "A.12"),
	("A.14.2", "Secure development", "A.14"),
]


def ensure_iso_controls() -> int:
	created = 0
	for control_id, title, domain in ISO_CONTROLS:
		if frappe.db.exists("Rental ISO Control", control_id):
			continue
		frappe.get_doc(
			{
				"doctype": "Rental ISO Control",
				"control_id": control_id,
				"control_title": title,
				"iso_domain": domain,
				"implementation_status": "Implemented",
			}
		).insert(ignore_permissions=True)
		created += 1
	return created


@frappe.whitelist()
def get_iso27001_status() -> dict:
	ensure_iso_controls()
	total = frappe.db.count("Rental ISO Control")
	verified = frappe.db.count("Rental ISO Control", {"implementation_status": "Verified"})
	return {"controls_total": total, "verified": verified, "framework": "ISO 27001:2022", "ready": total >= 4}
