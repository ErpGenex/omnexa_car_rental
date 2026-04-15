import frappe
from frappe import _
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["company = %(company)s", "docstatus < 2"]
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
			maintenance_type,
			COUNT(name) AS records_count,
			COALESCE(SUM(cost_amount), 0) AS total_cost
		FROM `tabVehicle Maintenance Record`
		WHERE {' AND '.join(conditions)}
		GROUP BY vehicle, branch, maintenance_type
		ORDER BY total_cost DESC, vehicle ASC
		""",
		filters,
		as_dict=True,
	)
	return _columns(), data


def _columns():
	return [
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 180},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Maintenance Type"), "fieldname": "maintenance_type", "fieldtype": "Data", "width": 150},
		{"label": _("Records"), "fieldname": "records_count", "fieldtype": "Int", "width": 90},
		{"label": _("Total Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 140},
	]

