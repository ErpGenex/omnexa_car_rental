import frappe
from frappe import _
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

	rows = frappe.db.sql(
		f"""
		SELECT vehicle, branch, COUNT(name) AS contracts_count
		FROM `tabRental Contract`
		WHERE {' AND '.join(conditions)}
		GROUP BY vehicle, branch
		ORDER BY contracts_count DESC, vehicle ASC
		""",
		filters,
		as_dict=True,
	)
	total_contracts = sum(flt(r.contracts_count) for r in rows) or 1
	data = []
	for row in rows:
		data.append(
			{
				"vehicle": row.vehicle,
				"branch": row.branch,
				"contracts_count": flt(row.contracts_count),
				"utilization_percent": flt((flt(row.contracts_count) / total_contracts) * 100.0, 2),
			}
		)
	return _columns(), data


def _columns():
	return [
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 180},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Contracts"), "fieldname": "contracts_count", "fieldtype": "Int", "width": 110},
		{"label": _("Utilization %"), "fieldname": "utilization_percent", "fieldtype": "Percent", "width": 120},
	]

