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


@frappe.whitelist()
def toll_run_matching(toll_transaction: str, allow_last_known_renter: int = 1):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import run_matching

	return run_matching(toll_transaction, allow_last_known_renter=bool(cint(allow_last_known_renter)))


@frappe.whitelist()
def toll_create_customer_invoice(toll_transaction: str):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import create_recharge_sales_invoice

	return create_recharge_sales_invoice(toll_transaction)


@frappe.whitelist()
def toll_apply_fx(toll_transaction: str):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import apply_fx_to_company_currency

	apply_fx_to_company_currency(toll_transaction)
	return {"ok": True}


@frappe.whitelist()
def toll_ingest_batch_file(file_name: str, provider_code: str):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_ingestion import ingest_batch_file

	return ingest_batch_file(file_name, provider_code)


@frappe.whitelist()
def toll_create_journal_entry(toll_transaction: str):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import create_toll_journal_entry

	return create_toll_journal_entry(toll_transaction)


@frappe.whitelist()
def toll_run_monthly_consolidation(year: int, month: int, company: str | None = None, dry_run: int = 0):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import run_monthly_consolidated_billing

	return run_monthly_consolidated_billing(
		int(year), int(month), company=company or None, dry_run=bool(cint(dry_run))
	)


@frappe.whitelist()
def toll_run_previous_month_consolidation(company: str | None = None):
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import run_previous_month_consolidation

	return run_previous_month_consolidation(company=company or None)


@frappe.whitelist()
def create_rental_contract_from_booking(booking: str):
	"""Create a draft Rental Contract from a confirmed (or inquiry) booking."""
	b = frappe.get_doc("Rental Booking", booking)
	if b.booking_status == "Cancelled":
		frappe.throw(frappe._("Cancelled booking cannot be converted."), title=frappe._("Booking"))
	if b.rental_contract:
		return b.rental_contract

	c = frappe.get_doc(
		{
			"doctype": "Rental Contract",
			"booking": b.name,
			"customer_profile": b.customer_profile,
			"vehicle": b.vehicle,
			"company": b.company,
			"branch": b.branch,
			"rental_mode": b.rental_mode,
			"contract_start": b.start_datetime,
			"contract_end": b.end_datetime,
			"status": "Draft",
		}
	)
	c.insert()
	return c.name


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("car_rental", scenario=scenario, params=params)
