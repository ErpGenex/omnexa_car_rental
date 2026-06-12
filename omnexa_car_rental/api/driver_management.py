# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Driver violations, scoring, training."""

from __future__ import annotations

import frappe
from frappe.utils import flt


@frappe.whitelist()
def record_driver_violation(rental_driver: str, violation_type: str, fine_amount: float = 0) -> dict:
	driver = frappe.get_doc("Rental Driver", rental_driver)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Driver Violation",
			"rental_driver": rental_driver,
			"company": driver.company,
			"branch": driver.branch,
			"violation_date": frappe.utils.today(),
			"violation_type": violation_type,
			"fine_amount": flt(fine_amount),
			"status": "Open",
		}
	)
	doc.insert()
	return {"violation": doc.name}


@frappe.whitelist()
def compute_driver_score(rental_driver: str) -> dict:
	violations = frappe.db.count("Rental Driver Violation", {"rental_driver": rental_driver, "status": "Open"})
	score = max(0, 100 - violations * 15)
	return {"rental_driver": rental_driver, "score": score, "open_violations": violations}


@frappe.whitelist()
def record_driver_training(rental_driver: str, course_name: str) -> dict:
	driver = frappe.get_doc("Rental Driver", rental_driver)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Driver Training",
			"rental_driver": rental_driver,
			"company": driver.company,
			"branch": driver.branch,
			"course_name": course_name,
			"completed_on": frappe.utils.today(),
			"status": "Completed",
		}
	)
	doc.insert()
	return {"training": doc.name}
