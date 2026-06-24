import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["company = %(company)s", "docstatus = 1"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			vehicle,
			branch,
			COUNT(name) AS contracts_count,
			COALESCE(SUM(total_amount), 0) AS total_revenue
		FROM `tabRental Contract`
		WHERE {' AND '.join(conditions)}
		GROUP BY vehicle, branch
		ORDER BY total_revenue DESC, vehicle ASC
		""",
		filters,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 180},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Contracts"), "fieldname": "contracts_count", "fieldtype": "Int", "width": 100},
		{"label": _("Total Revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 150},
	]

