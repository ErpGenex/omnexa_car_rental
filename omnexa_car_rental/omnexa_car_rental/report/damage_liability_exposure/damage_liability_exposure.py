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

	conditions = ["dr.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("dr.branch = %(branch)s")
	if filters.get("liability_type"):
		conditions.append("dr.liability_type = %(liability_type)s")
	if filters.get("status"):
		conditions.append("dr.status = %(status)s")
	if filters.get("from_date"):
		conditions.append("dr.report_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("dr.report_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("dr.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			dr.branch,
			dr.liability_type,
			dr.status,
			COUNT(*) AS report_count,
			COALESCE(SUM(dr.estimated_damage_cost), 0) AS estimated_damage_cost,
			SUM(CASE WHEN dr.insurance_claim_required = 1 THEN 1 ELSE 0 END) AS insurance_claims
		FROM `tabVehicle Damage Report` dr
		WHERE {' AND '.join(conditions)}
		GROUP BY dr.branch, dr.liability_type, dr.status
		ORDER BY dr.branch, dr.liability_type, dr.status
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["estimated_damage_cost"] = flt(row.estimated_damage_cost)

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Liability"), "fieldname": "liability_type", "fieldtype": "Data", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Reports"), "fieldname": "report_count", "fieldtype": "Int", "width": 90},
		{"label": _("Estimated Cost"), "fieldname": "estimated_damage_cost", "fieldtype": "Currency", "width": 140},
		{"label": _("Insurance Claims"), "fieldname": "insurance_claims", "fieldtype": "Int", "width": 130},
	]
