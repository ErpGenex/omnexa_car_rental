# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["rc.company = %(company)s", "rc.docstatus = 1"]
	if filters.get("branch"):
		conditions.append("rc.branch = %(branch)s")
	if filters.get("status"):
		conditions.append("rc.status = %(status)s")
	if filters.get("from_date"):
		conditions.append("DATE(rc.contract_start) >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("DATE(rc.contract_end) <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("rc.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			rc.branch,
			rc.status,
			rc.rental_mode,
			COUNT(*) AS contract_count,
			COALESCE(SUM(rc.total_amount), 0) AS total_amount,
			COALESCE(SUM(rc.deposit_amount), 0) AS deposit_amount
		FROM `tabRental Contract` rc
		WHERE {' AND '.join(conditions)}
		GROUP BY rc.branch, rc.status, rc.rental_mode
		ORDER BY rc.branch, rc.status
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["total_amount"] = flt(row.total_amount)
		row["deposit_amount"] = flt(row.deposit_amount)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Rental Mode"), "fieldname": "rental_mode", "fieldtype": "Data", "width": 120},
		{"label": _("Contracts"), "fieldname": "contract_count", "fieldtype": "Int", "width": 90},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Deposits"), "fieldname": "deposit_amount", "fieldtype": "Currency", "width": 120},
	]
