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

	conditions = ["fl.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("fl.branch = %(branch)s")
	if filters.get("allocation_mode"):
		conditions.append("fl.allocation_mode = %(allocation_mode)s")
	if filters.get("from_date"):
		conditions.append("fl.posting_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("fl.posting_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("fl.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			fl.branch,
			fl.allocation_mode,
			DATE_FORMAT(fl.posting_date, '%%Y-%%m') AS period,
			COUNT(*) AS log_count,
			COALESCE(SUM(fl.fuel_liters), 0) AS fuel_liters,
			COALESCE(SUM(fl.fuel_cost), 0) AS fuel_cost,
			COALESCE(SUM(fl.km_driven), 0) AS km_driven
		FROM `tabVehicle Fuel Log` fl
		WHERE {' AND '.join(conditions)}
		GROUP BY fl.branch, fl.allocation_mode, DATE_FORMAT(fl.posting_date, '%%Y-%%m')
		ORDER BY period DESC, fl.branch
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["fuel_liters"] = flt(row.fuel_liters)
		row["fuel_cost"] = flt(row.fuel_cost)
		row["km_driven"] = flt(row.km_driven)
		lit = row["fuel_liters"]
		km = row["km_driven"]
		row["cost_per_km"] = flt(row["fuel_cost"] / km, 4) if km else None
		row["liters_per_100km"] = flt((lit / km) * 100.0, 2) if km else None

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Allocation"), "fieldname": "allocation_mode", "fieldtype": "Data", "width": 150},
		{"label": _("Period (YYYY-MM)"), "fieldname": "period", "fieldtype": "Data", "width": 120},
		{"label": _("Logs"), "fieldname": "log_count", "fieldtype": "Int", "width": 70},
		{"label": _("Fuel Liters"), "fieldname": "fuel_liters", "fieldtype": "Float", "width": 110},
		{"label": _("Fuel Cost"), "fieldname": "fuel_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("KM Driven"), "fieldname": "km_driven", "fieldtype": "Float", "width": 100},
		{"label": _("Cost / KM"), "fieldname": "cost_per_km", "fieldtype": "Float", "width": 100},
		{"label": _("L / 100 KM"), "fieldname": "liters_per_100km", "fieldtype": "Float", "width": 100},
	]
