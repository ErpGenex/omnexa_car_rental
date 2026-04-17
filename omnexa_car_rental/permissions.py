# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe

from omnexa_core.omnexa_core.branch_access import enforce_branch_access, get_allowed_branches
from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults


def enforce_branch_access_for_doc(doc, method=None):
	enforce_branch_access(doc)


def populate_company_branch_from_user_context(doc, method=None):
	apply_company_branch_defaults(doc)


def _get_query_for_table(table: str, user=None):
	user = user or frappe.session.user
	allowed = get_allowed_branches(user)
	if allowed is None:
		return ""
	if not allowed:
		return "1=0"
	quoted = ", ".join([frappe.db.escape(v) for v in allowed])
	return f"(`tab{table}`.branch in ({quoted}) or `tab{table}`.branch is null or `tab{table}`.branch = '')"


def vehicle_query_conditions(user=None):
	return _get_query_for_table("Vehicle", user)


def rental_booking_query_conditions(user=None):
	return _get_query_for_table("Rental Booking", user)


def rental_contract_query_conditions(user=None):
	return _get_query_for_table("Rental Contract", user)


def rental_driver_query_conditions(user=None):
	return _get_query_for_table("Rental Driver", user)


def supplier_fleet_contract_query_conditions(user=None):
	return _get_query_for_table("Supplier Fleet Contract", user)


def vehicle_maintenance_record_query_conditions(user=None):
	return _get_query_for_table("Vehicle Maintenance Record", user)


def vehicle_fuel_log_query_conditions(user=None):
	return _get_query_for_table("Vehicle Fuel Log", user)


def vehicle_damage_report_query_conditions(user=None):
	return _get_query_for_table("Vehicle Damage Report", user)


def vehicle_insurance_policy_query_conditions(user=None):
	return _get_query_for_table("Vehicle Insurance Policy", user)


def toll_transaction_query_conditions(user=None):
	return _get_query_for_table("Toll Transaction", user)


def toll_allocation_rule_query_conditions(user=None):
	return _get_query_for_table("Toll Allocation Rule", user)


def toll_invoice_line_query_conditions(user=None):
	return _get_query_for_table("Toll Invoice Line", user)


def toll_provider_query_conditions(user=None):
	"""Toll Provider is global config (no branch)."""
	return ""

