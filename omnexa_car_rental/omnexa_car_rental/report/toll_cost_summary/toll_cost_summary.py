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
		filters.company = frappe.defaults.get_user_default("Company")
	if not filters.get("company"):
		frappe.throw(_("Company is required (set filter or user default)."), title=_("Filters"))

	conditions = ["tt.company = %(company)s", "tt.status != 'Duplicate Ignored'"]
	values: dict = {"company": filters.company
	}

	if filters.get("branch"):
		conditions.append("tt.branch = %(branch)s")
		values["branch"] = filters.branch

	if filters.get("from_date"):
		conditions.append("DATE(tt.crossing_datetime) >= %(from_date)s")
		values["from_date"] = filters.from_date
	if filters.get("to_date"):
		conditions.append("DATE(tt.crossing_datetime) <= %(to_date)s")
		values["to_date"] = filters.to_date

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		values["allowed_branches"] = tuple(allowed)
		conditions.append("tt.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		select
			tt.vehicle,
			tt.customer,
			tt.branch,
			tt.provider,
			count(tt.name) as toll_count,
			coalesce(sum(coalesce(tt.amount_company_currency, tt.amount)), 0) as total_amount
		from `tabToll Transaction` tt
		where {' AND '.join(conditions)}
		group by tt.vehicle, tt.customer, tt.branch, tt.provider
		order by total_amount desc, tt.vehicle asc
		""",
		values,
		as_dict=True,
	)
	for row in data:
		row.total_amount = flt(row.total_amount, 2)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 160
	},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160
	},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120
	},
		{"label": _("Toll Provider"), "fieldname": "provider", "fieldtype": "Link", "options": "Toll Provider", "width": 140
	},
		{"label": _("Crossings"), "fieldname": "toll_count", "fieldtype": "Int", "width": 100
	},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 140
	},
	]
