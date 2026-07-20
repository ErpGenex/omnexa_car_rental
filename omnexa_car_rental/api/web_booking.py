# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Public / guest APIs for online car rental booking."""

from __future__ import annotations

from datetime import datetime

import frappe
from frappe import _
from frappe.utils import flt, get_datetime

from omnexa_car_rental.omnexa_car_rental.rental_availability import vehicle_has_overlap


def _rate_for_plan(plan: dict, rental_type: str) -> float:
	mapping = {
		"Hourly": plan.get("hourly_rate"),
		"Daily": plan.get("daily_rate"),
		"Weekly": plan.get("weekly_rate"),
		"Monthly": plan.get("monthly_rate"),
		"Long-term lease": plan.get("monthly_rate")
	}
	return flt(mapping.get(rental_type) or plan.get("daily_rate"))


@frappe.whitelist(allow_guest=True)
def quote_rental_rate(
	company: str,
	branch: str,
	vehicle_group: str | None = None,
	rental_type: str = "Daily",
) -> dict:
	"""Return best active rate plan amount for a branch/group."""
	if not (company and branch):
		frappe.throw(_("Company and branch are required"))
	filters = {"company": company, "branch": branch, "is_active": 1
	}
	if vehicle_group:
		filters["vehicle_group"] = vehicle_group
	plan = frappe.db.get_value("Rental Rate Plan", filters, ["name", "hourly_rate", "daily_rate", "weekly_rate", "monthly_rate", "currency"], as_dict=True)
	if not plan and vehicle_group:
		plan = frappe.db.get_value(
			"Rental Rate Plan",
			{"company": company, "branch": branch, "is_active": 1
	},
			["name", "hourly_rate", "daily_rate", "weekly_rate", "monthly_rate", "currency"],
			as_dict=True,
		)
	if not plan:
		return {"amount": 0, "currency": frappe.db.get_value("Company", company, "default_currency"), "plan": None
	}
	return {
		"amount": _rate_for_plan(plan, rental_type),
		"currency": plan.currency or frappe.db.get_value("Company", company, "default_currency"),
		"plan": plan.name
	}


@frappe.whitelist(allow_guest=True)
def get_available_vehicles(
	company: str,
	branch: str,
	start_datetime: str,
	end_datetime: str,
	category: str | None = None,
) -> list[dict]:
	if not (company and branch and start_datetime and end_datetime):
		frappe.throw(_("Company, branch, start and end are required"))
	start = get_datetime(start_datetime)
	end = get_datetime(end_datetime)
	if end <= start:
		frappe.throw(_("End must be after start"))
	filters = {"company": company, "branch": branch, "status": ["in", ["Available", "Rented"]]}
	if category:
		filters["category"] = category
	rows = frappe.get_all(
		"Vehicle",
		filters=filters,
		fields=["name", "plate_number", "model", "category", "year", "status"],
		order_by="plate_number asc",
		limit=200,
	)
	out = []
	for row in rows:
		if vehicle_has_overlap(row.name, start, end):
			continue
		out.append(row)
	return out


@frappe.whitelist(allow_guest=True)
def book_rental_online(payload: str | dict) -> dict:
	"""Create inquiry/confirmed booking from website or guest channel."""
	data = frappe.parse_json(payload) if isinstance(payload, str) else frappe._dict(payload or {})
	required = ("company", "branch", "customer_profile", "vehicle", "start_datetime", "end_datetime", "rental_type")
	for key in required:
		if not data.get(key):
			frappe.throw(_("{0} is required").format(key.replace("_", " ").title()))

	start = get_datetime(data.start_datetime)
	end = get_datetime(data.end_datetime)
	if vehicle_has_overlap(data.vehicle, start, end):
		frappe.throw(_("Vehicle is not available for the selected period."), title=_("Availability"))

	quote = quote_rental_rate(data.company, data.branch, data.get("vehicle_group"), data.rental_type)
	amount = flt(data.estimated_amount) or flt(quote.get("amount"))

	doc = frappe.get_doc(
		{
			"doctype": "Rental Booking",
			"company": data.company,
			"branch": data.branch,
			"customer_profile": data.customer_profile,
			"vehicle": data.vehicle,
			"rental_type": data.rental_type,
			"rental_mode": data.get("rental_mode") or "Self Drive",
			"start_datetime": start,
			"end_datetime": end,
			"booking_status": data.get("booking_status") or "Confirmed",
			"estimated_amount": amount,
			"currency": data.get("currency") or quote.get("currency"),
			"booking_reference": data.get("booking_reference") or f"WEB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
	}
	)
	doc.flags.ignore_permissions = True
	doc.insert(ignore_permissions=True)
	return {"booking": doc.name, "estimated_amount": amount, "message": _("Booking created successfully.")
	}
