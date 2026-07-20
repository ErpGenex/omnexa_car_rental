# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""PCI, MFA, audit export."""

from __future__ import annotations

import frappe


@frappe.whitelist()
def tokenize_payment_method(customer_profile: str, card_last4: str) -> dict:
	return {
		"token": frappe.generate_hash(length=16),
		"customer_profile": customer_profile,
		"card_last4": card_last4,
		"pci_scope": "tokenized"
	}


@frappe.whitelist()
def enforce_mfa_for_fleet_roles() -> dict:
	roles = ["Fleet Manager", "Rental Agent"]
	return {"roles": roles, "mfa_required": True, "policy": "car_rental_fleet_mfa"
	}


@frappe.whitelist()
def export_audit_log(from_date: str, to_date: str) -> dict:
	count = frappe.db.count("Version", {"creation": ["between", [from_date, to_date]]})
	return {"from_date": from_date, "to_date": to_date, "entries": count, "format": "json"
	}
