# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["rb.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("rb.branch = %(branch)s")
	if filters.get("booking_status"):
		conditions.append("rb.booking_status = %(booking_status)s")
	if filters.get("from_date"):
		conditions.append("DATE(rb.start_datetime) >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("DATE(rb.end_datetime) <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("rb.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			rb.branch,
			rb.booking_status,
			rb.rental_type,
			rb.rental_mode,
			COUNT(*) AS booking_count,
			COALESCE(SUM(rb.estimated_amount), 0) AS estimated_amount
		FROM `tabRental Booking` rb
		WHERE {' AND '.join(conditions)}
		GROUP BY rb.branch, rb.booking_status, rb.rental_type, rb.rental_mode
		ORDER BY rb.branch, rb.booking_status, rb.rental_type
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["estimated_amount"] = flt(row.estimated_amount)

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Booking Status"), "fieldname": "booking_status", "fieldtype": "Data", "width": 120},
		{"label": _("Rental Type"), "fieldname": "rental_type", "fieldtype": "Data", "width": 130},
		{"label": _("Rental Mode"), "fieldname": "rental_mode", "fieldtype": "Data", "width": 120},
		{"label": _("Bookings"), "fieldname": "booking_count", "fieldtype": "Int", "width": 90},
		{"label": _("Estimated Amount"), "fieldname": "estimated_amount", "fieldtype": "Currency", "width": 140},
	]
