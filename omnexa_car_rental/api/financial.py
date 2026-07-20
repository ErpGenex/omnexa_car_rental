# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""IFRS 15, FX, fleet depreciation."""

from __future__ import annotations

import frappe
from frappe.utils import flt, today


@frappe.whitelist()
def recognize_revenue(rental_contract: str, amount: float, phase: str = "Performance") -> dict:
	contract = frappe.get_doc("Rental Contract", rental_contract)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Revenue Recognition",
			"rental_contract": rental_contract,
			"company": contract.company,
			"branch": contract.branch,
			"recognition_date": today(),
			"recognized_amount": flt(amount),
			"ifrs15_phase": phase,
			"status": "Posted"
	}
	)
	doc.insert()
	return {"recognition": doc.name
	}


@frappe.whitelist()
def apply_fx_rate(amount: float, from_currency: str, to_currency: str) -> dict:
	rate = flt(frappe.db.get_value("Currency Exchange", {"from_currency": from_currency, "to_currency": to_currency
	}, "exchange_rate") or 1)
	return {"from_currency": from_currency, "to_currency": to_currency, "rate": rate, "converted": flt(amount) * rate
	}


@frappe.whitelist()
def post_fleet_depreciation(vehicle: str, amount: float) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	return {
		"vehicle": vehicle,
		"company": v.company,
		"depreciation_amount": flt(amount),
		"integration": "omnexa_fixed_assets",
		"status": "Queued"
	}
