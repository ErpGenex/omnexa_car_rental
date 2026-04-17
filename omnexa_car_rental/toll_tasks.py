# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe.utils import now


def poll_toll_providers():
	"""Scheduler hook: mark poll time; implement provider-specific fetch via custom app hooks."""
	for name in frappe.get_all(
		"Toll Provider",
		filters={"integration_type": "API Polling", "is_active": 1},
		pluck="name",
	):
		frappe.db.set_value("Toll Provider", name, "last_poll_at", now(), update_modified=False)
	frappe.db.commit()


def process_unmatched_toll_queue(limit: int = 50):
	"""Retry matching for toll rows stuck in Received / Vehicle Matched with a vehicle assigned."""
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import run_matching

	for row in frappe.get_all(
		"Toll Transaction",
		filters={"status": ["in", ["Received", "Vehicle Matched", "Contract Matched"]]},
		pluck="name",
		limit_page_length=limit,
		order_by="modified asc",
	):
		run_matching(row, allow_last_known_renter=True)


def run_scheduled_monthly_toll_billing():
	"""First of month (via cron): consolidate previous calendar month tolls."""
	from omnexa_car_rental.omnexa_car_rental.toll.toll_engine import run_previous_month_consolidation

	run_previous_month_consolidation()
