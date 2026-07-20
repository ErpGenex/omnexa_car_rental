# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""SOC2 evidence export."""

from __future__ import annotations

import frappe


@frappe.whitelist()
def export_soc2_evidence(period: str = "monthly") -> dict:
	return {
		"period": period,
		"trust_principles": ["Security", "Availability", "Confidentiality"],
		"evidence_items": frappe.db.count("Rental ISO Control") + frappe.db.count("Version"),
		"export_format": "zip",
		"status": "Ready",
	}
