from __future__ import annotations

import frappe
from frappe.utils import cint, flt, get_first_day, getdate, today
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def _kpi_conditions(company: str | None = None, branch: str | None = None):
	conds = ["docstatus < 2"]
	values: dict[str, object] = {}
	if company:
		conds.append("company = %(company)s")
		values["company"] = company
	if branch:
		conds.append("branch = %(branch)s")
		values["branch"] = branch

	allowed = get_allowed_branches(company=company) if company else None
	if allowed is not None:
		if not allowed:
			conds.append("1=0")
		else:
			values["allowed_branches"] = tuple(allowed)
			conds.append("branch in %(allowed_branches)s")

	return conds, values


@frappe.whitelist()
def kpi_utilization_percent():
	company = frappe.defaults.get_user_default("Company")
	conds, values = _kpi_conditions(company=company)
	total_vehicles = frappe.db.sql(
		f"SELECT COUNT(*) FROM `tabVehicle` WHERE {' AND '.join(conds)}",
		values,
	)[0][0]
	conds.append("status = 'Rented'")
	rented_vehicles = frappe.db.sql(
		f"SELECT COUNT(*) FROM `tabVehicle` WHERE {' AND '.join(conds)}",
		values,
	)[0][0]
	percent = (flt(rented_vehicles) / flt(total_vehicles) * 100.0) if cint(total_vehicles) > 0 else 0
	return {"value": flt(percent, 2), "fieldtype": "Percent", "route": ["List", "Vehicle"]}


@frappe.whitelist()
def kpi_active_rentals():
	company = frappe.defaults.get_user_default("Company")
	conds, values = _kpi_conditions(company=company)
	conds.append("status = 'Active Rental'")
	conds.append("docstatus = 1")
	value = frappe.db.sql(
		f"SELECT COUNT(*) FROM `tabRental Contract` WHERE {' AND '.join(conds)}",
		values,
	)[0][0]
	return {"value": cint(value), "fieldtype": "Int", "route": ["List", "Rental Contract"]}


@frappe.whitelist()
def kpi_revenue_today():
	company = frappe.defaults.get_user_default("Company")
	conds, values = _kpi_conditions(company=company)
	conds.append("docstatus = 1")
	conds.append("DATE(contract_start) = %(today)s")
	values["today"] = getdate(today())
	value = frappe.db.sql(
		f"SELECT COALESCE(SUM(total_amount), 0) FROM `tabRental Contract` WHERE {' AND '.join(conds)}",
		values,
	)[0][0]
	return {"value": flt(value), "fieldtype": "Currency", "route": ["List", "Rental Contract"]}


@frappe.whitelist()
def kpi_maintenance_cost_mtd():
	company = frappe.defaults.get_user_default("Company")
	conds, values = _kpi_conditions(company=company)
	conds.append("posting_date BETWEEN %(month_start)s AND %(today)s")
	values["today"] = getdate(today())
	values["month_start"] = get_first_day(values["today"])
	value = frappe.db.sql(
		f"SELECT COALESCE(SUM(cost_amount), 0) FROM `tabVehicle Maintenance Record` WHERE {' AND '.join(conds)}",
		values,
	)[0][0]
	return {"value": flt(value), "fieldtype": "Currency", "route": ["List", "Vehicle Maintenance Record"]}

