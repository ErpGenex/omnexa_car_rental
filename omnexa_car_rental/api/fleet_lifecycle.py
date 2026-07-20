# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Vehicle acquisition, disposal, leasing templates, warranty, downtime SLA."""

from __future__ import annotations

import frappe
from frappe.utils import flt, today


@frappe.whitelist()
def record_vehicle_acquisition(vehicle: str, purchase_amount: float, supplier: str | None = None) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Vehicle Acquisition",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"acquisition_date": today(),
			"purchase_amount": flt(purchase_amount),
			"supplier": supplier,
			"status": "Completed"
	}
	)
	doc.insert()
	return {"acquisition": doc.name
	}


@frappe.whitelist()
def record_vehicle_disposal(vehicle: str, method: str = "Sale", proceeds: float = 0) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Vehicle Disposal",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"disposal_date": today(),
			"disposal_method": method,
			"proceeds": flt(proceeds),
			"status": "Completed"
	}
	)
	doc.insert()
	v.status = "Disposed"
	v.save()
	return {"disposal": doc.name
	}


@frappe.whitelist()
def get_leasing_template(template_code: str) -> dict:
	return frappe.get_doc("Rental Leasing Template", template_code).as_dict()


@frappe.whitelist()
def submit_warranty_claim(vehicle: str, claim_amount: float, work_order: str | None = None) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Warranty Claim",
			"vehicle": vehicle,
			"work_order": work_order,
			"company": v.company,
			"branch": v.branch,
			"claim_amount": flt(claim_amount),
			"status": "Open"
	}
	)
	doc.insert()
	return {"claim": doc.name
	}


@frappe.whitelist()
def track_downtime_sla(vehicle: str, target_hours: int = 24) -> dict:
	from frappe.utils import add_to_date, now_datetime

	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Downtime SLA",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"incident_start": now_datetime(),
			"target_restore": add_to_date(now_datetime(), hours=target_hours),
			"status": "Open"
	}
	)
	doc.insert()
	return {"sla": doc.name
	}
