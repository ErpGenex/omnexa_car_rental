# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe.utils import now


def poll_toll_providers():
	"""Scheduler: poll RTA Salik and ITC DARB for new toll passages."""
	from omnexa_car_rental.omnexa_car_rental.toll.toll_polling import poll_all_active

	poll_all_active(force=False)


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
