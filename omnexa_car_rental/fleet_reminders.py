# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""Daily fleet reminders: expiring insurance and driver licenses (ToDo for Fleet Managers)."""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today


def _fleet_manager_users() -> list[str]:
	rows = frappe.db.sql(
		"""
		select distinct hr.parent
		from `tabHas Role` hr
		inner join `tabUser` u on u.name = hr.parent and u.enabled = 1
		where hr.role = 'Fleet Manager' and hr.parenttype = 'User'
		""",
		pluck=True,
	)
	return list(rows) if rows else ["Administrator"]


def _open_todo_exists(reference_doctype: str, reference_name: str) -> bool:
	return bool(
		frappe.db.exists(
			"ToDo",
			{
				"reference_type": reference_doctype,
				"reference_name": reference_name,
				"status": "Open",
			},
		)
	)


def remind_insurance_expiry():
	"""Create one open ToDo per policy expiring within 30 days (Active only)."""
	td, lim = getdate(today()), getdate(add_days(today(), 30))
	assignee = _fleet_manager_users()[0]
	for row in frappe.get_all(
		"Vehicle Insurance Policy",
		filters={"status": "Active", "end_date": ["between", [td, lim]]},
		fields=["name", "vehicle", "end_date", "policy_number"],
	):
		if _open_todo_exists("Vehicle Insurance Policy", row.name):
			continue
		frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": _(
					"Vehicle insurance expiring on {0}: policy {1} — vehicle {2}"
				).format(row.end_date, row.policy_number or row.name, row.vehicle),
				"reference_type": "Vehicle Insurance Policy",
				"reference_name": row.name,
				"allocated_to": assignee,
				"priority": "Medium",
			}
		).insert(ignore_permissions=True)


def remind_driver_license_expiry():
	"""Drivers with Active status and license expiring within 30 days."""
	td, lim = getdate(today()), getdate(add_days(today(), 30))
	assignee = _fleet_manager_users()[0]
	for row in frappe.get_all(
		"Rental Driver",
		filters={
			"status": "Active",
			"license_expiry_date": ["between", [td, lim]],
		},
		fields=["name", "driver_name", "license_expiry_date", "license_number"],
	):
		if _open_todo_exists("Rental Driver", row.name):
			continue
		frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": _(
					"Driver license expiring on {0}: {1} ({2})"
				).format(row.license_expiry_date, row.driver_name, row.license_number or ""),
				"reference_type": "Rental Driver",
				"reference_name": row.name,
				"allocated_to": assignee,
				"priority": "Medium",
			}
		).insert(ignore_permissions=True)


def run_daily():
	remind_insurance_expiry()
	remind_driver_license_expiry()
	frappe.db.commit()
