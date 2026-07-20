# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Accidents, insurance claims, cost recovery, insurer API."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def submit_insurance_claim(damage_report: str, claim_amount: float) -> dict:
	damage = frappe.get_doc("Vehicle Damage Report", damage_report)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Insurance Claim",
			"damage_report": damage_report,
			"insurance_policy": frappe.db.get_value("Vehicle Insurance Policy", {"vehicle": damage.vehicle, "status": "Active"}, "name"),
			"company": damage.company,
			"branch": damage.branch,
			"claim_amount": flt(claim_amount),
			"status": "Submitted",
		}
	)
	doc.insert()
	return {"claim": doc.name}


@frappe.whitelist()
def bill_cost_recovery(damage_report: str, customer_profile: str, amount: float) -> dict:
	from omnexa_car_rental.api.integrations import create_payment_preauth

	return {
		"damage_report": damage_report,
		"customer_profile": customer_profile,
		"recovery_amount": flt(amount),
		"invoice_status": "Pending",
		"preauth": create_payment_preauth(customer_profile, amount),
	}


@frappe.whitelist()
def submit_insurer_api_claim(claim: str) -> dict:
	doc = frappe.get_doc("Rental Insurance Claim", claim)
	return {"claim": doc.name, "external_ref": frappe.generate_hash(length=10), "status": "Submitted to Insurer"}


def run_policy_renewal_reminders() -> None:
	"""Daily job — policies expiring within 30 days."""
	from frappe.utils import add_days

	threshold = add_days(frappe.utils.today(), 30)
	for pol in frappe.get_all(
		"Vehicle Insurance Policy",
		filters={"expiry_date": ["<=", threshold], "status": "Active"},
		fields=["name", "vehicle", "expiry_date"],
	):
		frappe.logger("car_rental").info(f"Policy renewal reminder: {pol.name} vehicle={pol.vehicle}")
