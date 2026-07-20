# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Preventive and predictive maintenance."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, today


@frappe.whitelist()
def schedule_preventive_maintenance(vehicle: str, service_type: str, interval_km: int = 5000) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Preventive Schedule",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"service_type": service_type,
			"interval_km": interval_km,
			"next_due_date": add_days(today(), 30),
			"status": "Active"
	}
	)
	doc.insert()
	return {"schedule": doc.name
	}


@frappe.whitelist()
def create_predictive_alert(vehicle: str, alert_type: str, severity: str = "Medium") -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Predictive Alert",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"alert_type": alert_type,
			"severity": severity,
			"predicted_on": frappe.utils.now_datetime(),
			"status": "Open"
	}
	)
	doc.insert()
	return {"alert": doc.name
	}
