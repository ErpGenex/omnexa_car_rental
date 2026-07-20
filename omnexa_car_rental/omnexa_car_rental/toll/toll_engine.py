# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

import frappe
from frappe.utils import add_days, add_to_date, flt, get_datetime, get_first_day, get_last_day, getdate, today

from omnexa_car_rental.omnexa_car_rental.toll.toll_util import normalize_plate


def find_duplicate_event(
	vehicle: str | None,
	toll_gate_code: str | None,
	toll_gate_name: str | None,
	crossing_dt,
	provider: str,
	window_seconds: int,
	exclude_name: str | None = None,
) -> str | None:
	"""Return name of existing Toll Transaction if duplicate within time window."""
	if not vehicle or not crossing_dt:
		return None
	gate = toll_gate_code or toll_gate_name or ""
	if not gate:
		return None
	start = get_datetime(crossing_dt) - timedelta(seconds=window_seconds)
	end = get_datetime(crossing_dt) + timedelta(seconds=window_seconds)
	filters = [
		["vehicle", "=", vehicle],
		["provider", "=", provider],
		["crossing_datetime", ">=", start],
		["crossing_datetime", "<=", end],
		["status", "!=", "Duplicate Ignored"],
	]
	if toll_gate_code:
		filters.append(["toll_gate_code", "=", toll_gate_code])
	elif toll_gate_name:
		filters.append(["toll_gate_name", "=", toll_gate_name])
	rows = frappe.get_all(
		"Toll Transaction",
		filters=filters,
		pluck="name",
		limit=5,
	)
	for row in rows:
		if exclude_name and row == exclude_name:
			continue
		return row
	return None


def resolve_vehicle(plate_number: str | None, tag_id: str | None) -> tuple[str | None, str]:
	"""Returns (vehicle_name, match_source)."""
	if tag_id:
		tag = tag_id.strip()
		v = frappe.db.get_value("Vehicle", {"toll_tag_id": tag
	}, "name")
		if v:
			return v, "tag"
	if plate_number:
		norm = normalize_plate(plate_number)
		for row in frappe.get_all("Vehicle", fields=["name", "plate_number"], limit_page_length=5000):
			if normalize_plate(row.plate_number) == norm:
				return row.name, "plate"
	return None, ""


def _contract_end_with_grace(contract_name: str, event_dt) -> Any:
	doc = frappe.get_cached_doc("Rental Contract", contract_name)
	grace = int(doc.grace_period_minutes or 0)
	end = get_datetime(doc.contract_end)
	if grace:
		end = add_to_date(end, minutes=grace, as_datetime=True)
	return end


def find_active_contract(vehicle: str, event_dt, use_last_known_renter: bool = False) -> tuple[str | None, str]:
	"""Returns (contract_name, reason)."""
	event = get_datetime(event_dt)
	rows = frappe.get_all(
		"Rental Contract",
		filters={
			"vehicle": vehicle,
			"docstatus": 1,
			"status": "Active Rental"
	},
		fields=["name", "contract_start", "contract_end", "grace_period_minutes"],
		order_by="contract_start desc",
	)
	for row in rows:
		start = get_datetime(row.contract_start)
		end = _contract_end_with_grace(row.name, event)
		if start <= event <= end:
			return row.name, "active_window"

	if use_last_known_renter:
		past = frappe.get_all(
			"Rental Contract",
			filters={"vehicle": vehicle, "docstatus": 1
	},
			fields=["name", "contract_start", "contract_end"],
			order_by="contract_end desc",
			limit=1,
		)
		if past:
			return past[0].name, "last_known_renter"
	return None, ""


def _customer_from_contract(contract_name: str) -> tuple[str | None, str | None]:
	contract = frappe.get_cached_doc("Rental Contract", contract_name)
	cprofile = contract.customer_profile
	customer = None
	if cprofile:
		customer = frappe.db.get_value("Customer Profile", cprofile, "linked_customer")
	return cprofile, customer


def _rule_matches(rule: dict, contract, vehicle_doc, txn: dict) -> bool:
	if rule.get("branch") and txn.get("branch") and rule["branch"] != txn["branch"]:
		return False
	if rule.get("match_rental_mode") and rule["match_rental_mode"] != "Any":
		if contract.rental_mode != rule["match_rental_mode"]:
			return False
	if rule.get("match_vehicle_category") and rule["match_vehicle_category"] != "Any":
		if vehicle_doc.category != rule["match_vehicle_category"]:
			return False
	if rule.get("match_customer_type") and rule["match_customer_type"] != "Any":
		ct = frappe.db.get_value("Customer Profile", contract.customer_profile, "customer_type")
		if ct != rule["match_customer_type"]:
			return False
	if rule.get("match_customer_group"):
		linked = frappe.db.get_value("Customer Profile", contract.customer_profile, "linked_customer")
		if not linked:
			return False
		cg = frappe.db.get_value("Customer", linked, "customer_group")
		if cg != rule["match_customer_group"]:
			return False
	if rule.get("match_project"):
		if not txn.get("project") or txn["project"] != rule["match_project"]:
			return False
	return True


def apply_allocation_rules(txn_doc: frappe.model.document.Document) -> dict | None:
	if not txn_doc.contract or not txn_doc.vehicle:
		return None
	contract = frappe.get_cached_doc("Rental Contract", txn_doc.contract)
	vehicle_doc = frappe.get_cached_doc("Vehicle", txn_doc.vehicle)
	txn = {"branch": txn_doc.branch, "project": txn_doc.project
	}
	rules = frappe.get_all(
		"Toll Allocation Rule",
		filters={"is_active": 1, "company": txn_doc.company
	},
		fields="*",
		order_by="priority asc",
	)
	for rule in rules:
		if not _rule_matches(rule, contract, vehicle_doc, txn):
			continue
		return rule
	return None


def run_matching(txn_name: str, allow_last_known_renter: bool = True) -> dict[str, Any]:
	doc = frappe.get_doc("Toll Transaction", txn_name)
	if doc.status == "Duplicate Ignored":
		return {"ok": True, "skipped": True, "reason": "duplicate_ignored"
	}

	# Vehicle
	if not doc.vehicle:
		vname, src = resolve_vehicle(doc.plate_number, doc.tag_id)
		if vname:
			doc.vehicle = vname
			doc.match_source = src
			doc.status = "Vehicle Matched"
		else:
			doc.status = "Unmatched"
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			return {"ok": True, "status": doc.status
	}

	# Contract
	if not doc.contract:
		cname, reason = find_active_contract(doc.vehicle, doc.crossing_datetime, allow_last_known_renter)
		if cname:
			doc.contract = cname
			doc.status = "Contract Matched"
			cprof, cust = _customer_from_contract(cname)
			doc.customer_profile = cprof
			doc.customer = cust
			# org from contract
			rc = frappe.get_cached_doc("Rental Contract", cname)
			doc.company = rc.company
			doc.branch = rc.branch
		else:
			doc.status = "Unmatched"
			doc.save(ignore_permissions=True)
			frappe.db.commit()
			return {"ok": True, "status": doc.status
	}

	# Rules
	rule = apply_allocation_rules(doc)
	if rule:
		doc.payer_assigned = rule.get("payer")
		doc.billing_method_applied = rule.get("billing_method")
		doc.allocation_rule = rule.get("name")
		doc.status = "Rule Applied"
	else:
		doc.status = "Contract Matched"

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "status": doc.status, "rule": rule.get("name") if rule else None
	}


def toll_txn_has_financial_link(txn_name: str) -> bool:
	return bool(frappe.db.exists("Toll Invoice Line", {"toll_transaction": txn_name
	}))


def create_recharge_sales_invoice(txn_name: str) -> dict[str, Any]:
	"""Create draft Sales Invoice + Toll Invoice Line when billing rules allow."""
	if not frappe.db.exists("DocType", "Sales Invoice"):
		return {"ok": False, "error": "Sales Invoice not available"
	}

	doc = frappe.get_doc("Toll Transaction", txn_name)
	if toll_txn_has_financial_link(txn_name):
		return {"ok": True, "skipped": True, "reason": "already_linked"
	}
	if doc.status in ("Billed", "Paid"):
		return {"ok": True, "skipped": True
	}

	if doc.payer_assigned not in (None, "", "Customer"):
		return {"ok": True, "skipped": True, "reason": "payer_not_customer"
	}

	rule_name = doc.allocation_rule
	if not rule_name:
		return {"ok": False, "error": "No allocation rule"
	}

	rule = frappe.get_doc("Toll Allocation Rule", rule_name)
	if rule.billing_method == "Internal Cost Only":
		return {"ok": True, "skipped": True, "reason": "internal_cost"
	}

	if rule.billing_method == "Monthly Consolidated":
		doc.add_comment("Comment", "Pending monthly consolidation per allocation rule.")
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		return {"ok": True, "skipped": True, "reason": "monthly_consolidated"
	}

	if not doc.customer:
		return {"ok": False, "error": "No customer for recharge"
	}

	item_code = rule.invoice_item or frappe.db.get_value(
		"Toll Provider", doc.provider, "default_sales_item"
	)
	if not item_code:
		return {"ok": False, "error": "No invoice item configured on rule or provider"
	}

	rate = flt(doc.amount_company_currency) or flt(doc.amount)
	posting_date = getdate(doc.crossing_datetime)

	si = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": doc.customer,
			"company": doc.company,
			"posting_date": posting_date,
			"due_date": posting_date,
			"items": [
				{
					"item_code": item_code,
					"qty": 1,
					"rate": rate,
					"description": f"Toll {doc.toll_gate_name or doc.toll_gate_code or ''} ({doc.provider})".strip()
	}
			]}
	)
	if rule.cost_center:
		for row in si.items:
			row.cost_center = rule.cost_center
	si.insert(ignore_permissions=True)

	tax_amount = 0.0
	tinv = frappe.get_doc(
		{
			"doctype": "Toll Invoice Line",
			"toll_transaction": doc.name,
			"sales_invoice": si.name,
			"company": doc.company,
			"branch": doc.branch,
			"amount": rate,
			"tax_amount": tax_amount,
			"cost_center": rule.cost_center,
			"revenue_account": rule.revenue_account,
			"description": si.items[0].description
	}
	)
	tinv.insert(ignore_permissions=True)

	doc.status = "Billed"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "sales_invoice": si.name, "toll_invoice_line": tinv.name
	}


def apply_fx_to_company_currency(txn_name: str) -> None:
	doc = frappe.get_doc("Toll Transaction", txn_name)
	company_currency = frappe.db.get_value("Company", doc.company, "default_currency")
	if not company_currency or doc.currency == company_currency:
		doc.exchange_rate = 1.0
		doc.save(ignore_permissions=True)
		return
	rate = None
	try:
		from erpnext.setup.utils import get_exchange_rate

		rate = get_exchange_rate(doc.currency, company_currency, getdate(doc.crossing_datetime), company=doc.company)
	except Exception:
		pass
	if rate:
		doc.exchange_rate = flt(rate)
	else:
		doc.exchange_rate = doc.exchange_rate or 1.0
	doc.save(ignore_permissions=True)


def create_toll_journal_entry(txn_name: str) -> dict[str, Any]:
	"""Book company-absorbed / internal toll: Dr expense, Cr clearing. Draft Journal Entry."""
	if not frappe.db.exists("DocType", "Journal Entry"):
		return {"ok": False, "error": "Journal Entry not available"
	}

	doc = frappe.get_doc("Toll Transaction", txn_name)
	if doc.status == "Duplicate Ignored":
		return {"ok": True, "skipped": True, "reason": "duplicate_ignored"
	}
	if toll_txn_has_financial_link(txn_name):
		return {"ok": True, "skipped": True, "reason": "already_linked"
	}
	if not doc.allocation_rule:
		return {"ok": False, "error": "No allocation rule"
	}

	rule = frappe.get_doc("Toll Allocation Rule", doc.allocation_rule)
	expense_acc = rule.toll_expense_account
	credit_acc = rule.company_clearing_account
	if not expense_acc or not credit_acc:
		return {"ok": False, "error": "Configure Toll Expense and Company Clearing accounts on the rule"
	}

	internal = rule.billing_method == "Internal Cost Only"
	company_payer = doc.payer_assigned in ("Company", "Insurance", "Vendor", "Project")
	if not internal and not company_payer:
		return {"ok": False, "error": "Journal entry applies to internal cost or company/insurance/vendor/project payers"
	}

	amt = flt(doc.amount_company_currency) or flt(doc.amount)
	if amt <= 0:
		return {"ok": False, "error": "Invalid amount"
	}

	posting_date = getdate(doc.crossing_datetime)
	remark = f"Toll {doc.name} | {doc.transaction_id} | {doc.provider}"

	debit_row = {
		"account": expense_acc,
		"debit_in_account_currency": amt,
		"credit_in_account_currency": 0,
		"cost_center": rule.cost_center
	}
	if doc.project:
		debit_row["project"] = doc.project

	accounts = [
		debit_row,
		{
			"account": credit_acc,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": amt
	},
	]

	je = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": doc.company,
			"posting_date": posting_date,
			"user_remark": remark,
			"accounts": accounts
	}
	)
	je.insert(ignore_permissions=True)

	tinv = frappe.get_doc(
		{
			"doctype": "Toll Invoice Line",
			"toll_transaction": doc.name,
			"journal_entry": je.name,
			"company": doc.company,
			"branch": doc.branch,
			"amount": amt,
			"tax_amount": 0,
			"cost_center": rule.cost_center,
			"revenue_account": expense_acc,
			"description": remark
	}
	)
	tinv.insert(ignore_permissions=True)

	doc.status = "Billed"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True, "journal_entry": je.name, "toll_invoice_line": tinv.name
	}


def run_monthly_consolidated_billing(
	year: int,
	month: int,
	company: str | None = None,
	*,
	dry_run: bool = False,
) -> dict[str, Any]:
	"""One Sales Invoice per (customer, company, branch, allocation_rule) for the month."""
	if not frappe.db.exists("DocType", "Sales Invoice"):
		return {"ok": False, "error": "Sales Invoice not available"
	}

	start = get_first_day(date(year, month, 1))
	end = add_days(get_last_day(date(year, month, 1)), 1)

	rule_names = frappe.get_all(
		"Toll Allocation Rule",
		filters={"billing_method": "Monthly Consolidated", "is_active": 1
	},
		pluck="name",
	)
	if not rule_names:
		return {"ok": True, "message": "No active Monthly Consolidated rules", "invoices": []
	}

	values: dict[str, Any] = {"start": start, "end": end, "rules": tuple(rule_names)
	}
	conds = [
		"tt.status = 'Rule Applied'",
		"tt.payer_assigned = 'Customer'",
		"tt.customer is not null",
		"tt.customer != ''",
		"tt.allocation_rule in %(rules)s",
		"tt.crossing_datetime >= %(start)s",
		"tt.crossing_datetime < %(end)s",
		"not exists (select 1 from `tabToll Invoice Line` til where til.toll_transaction = tt.name)",
	]
	if company:
		conds.append("tt.company = %(company)s")
		values["company"] = company

	rows = frappe.db.sql(
		f"""
		select tt.name, tt.customer, tt.company, tt.branch, tt.allocation_rule,
		tt.amount_company_currency, tt.amount, tt.crossing_datetime,
			coalesce(tt.toll_gate_name,'') as toll_gate_name, tt.provider, tt.transaction_id
		from `tabToll Transaction` tt
		where {' AND '.join(conds)}
		order by tt.customer, tt.company, tt.branch, tt.allocation_rule, tt.crossing_datetime
		""",
		values,
		as_dict=True,
	)

	groups: dict[tuple, list] = defaultdict(list)
	for row in rows:
		key = (row.customer, row.company, row.branch or "", row.allocation_rule)
		groups[key].append(row)

	results = []
	for key, txrows in groups.items():
		customer, comp, branch, rule_name = key
		rule = frappe.get_doc("Toll Allocation Rule", rule_name)
		item_code = rule.invoice_item or frappe.db.get_value("Toll Provider", txrows[0].provider, "default_sales_item")
		if not item_code:
			results.append(
				{
					"ok": False,
					"customer": customer,
					"error": "No invoice item on rule or provider",
					"count": len(txrows)
	}
			)
			continue

		if dry_run:
			total = sum(flt(r.amount_company_currency) or flt(r.amount) for r in txrows)
			results.append({"ok": True, "dry_run": True, "customer": customer, "lines": len(txrows), "total": total
	})
			continue

		posting_date = get_last_day(date(year, month, 1))
		items = []
		for r in txrows:
			rate = flt(r.amount_company_currency) or flt(r.amount)
			desc = f"Toll {r.transaction_id} {r.toll_gate_name or ''} ({r.provider})".strip()
			items.append({"item_code": item_code, "qty": 1, "rate": rate, "description": desc
	})

		si = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": customer,
				"company": comp,
				"posting_date": posting_date,
				"due_date": posting_date,
				"items": items
	}
		)
		if rule.cost_center:
			for line in si.items:
				line.cost_center = rule.cost_center
		si.insert(ignore_permissions=True)

		for r in txrows:
			rate = flt(r.amount_company_currency) or flt(r.amount)
			desc = f"Toll {r.transaction_id} {r.toll_gate_name or ''} ({r.provider})".strip()
			tinv = frappe.get_doc(
				{
					"doctype": "Toll Invoice Line",
					"toll_transaction": r.name,
					"sales_invoice": si.name,
					"company": comp,
					"branch": branch or None,
					"amount": rate,
					"tax_amount": 0,
					"cost_center": rule.cost_center,
					"revenue_account": rule.revenue_account,
					"description": desc
	}
			)
			tinv.insert(ignore_permissions=True)
			tdoc = frappe.get_doc("Toll Transaction", r.name)
			tdoc.status = "Billed"
			tdoc.save(ignore_permissions=True)

		frappe.db.commit()
		results.append({"ok": True, "sales_invoice": si.name, "lines": len(txrows), "customer": customer
	})

	return {"ok": True, "year": year, "month": month, "results": results
	}


def run_previous_month_consolidation(company: str | None = None) -> dict[str, Any]:
	"""Convenience: bill the calendar month before today."""
	d = add_to_date(getdate(today()), months=-1)
	return run_monthly_consolidated_billing(d.year, d.month, company=company, dry_run=False)
