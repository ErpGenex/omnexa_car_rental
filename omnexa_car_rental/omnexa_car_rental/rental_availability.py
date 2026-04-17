# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""Shared overlap checks for vehicles across bookings and rental contracts."""

from __future__ import annotations

import frappe
from frappe.utils import get_datetime


def intervals_overlap(start_a, end_a, start_b, end_b) -> bool:
	a0, a1 = get_datetime(start_a), get_datetime(end_a)
	b0, b1 = get_datetime(start_b), get_datetime(end_b)
	return a0 < b1 and b0 < a1


def overlapping_submitted_contracts(
	vehicle: str,
	start_dt,
	end_dt,
	*,
	exclude_contract: str | None = None,
) -> list[str]:
	"""Return names of submitted contracts in Active Rental that overlap the window."""
	if not vehicle:
		return []
	rows = frappe.get_all(
		"Rental Contract",
		filters={"vehicle": vehicle, "docstatus": 1, "status": "Active Rental"},
		fields=["name", "contract_start", "contract_end"],
	)
	out = []
	for row in rows:
		if exclude_contract and row.name == exclude_contract:
			continue
		if intervals_overlap(start_dt, end_dt, row.contract_start, row.contract_end):
			out.append(row.name)
	return out


def overlapping_confirmed_bookings(
	vehicle: str,
	start_dt,
	end_dt,
	*,
	exclude_booking: str | None = None,
) -> list[str]:
	if not vehicle:
		return []
	rows = frappe.get_all(
		"Rental Booking",
		filters={"vehicle": vehicle, "booking_status": "Confirmed"},
		fields=["name", "start_datetime", "end_datetime"],
	)
	out = []
	for row in rows:
		if exclude_booking and row.name == exclude_booking:
			continue
		if intervals_overlap(start_dt, end_dt, row.start_datetime, row.end_datetime):
			out.append(row.name)
	return out


def vehicle_has_other_active_rental(vehicle: str, exclude_contract: str | None = None) -> bool:
	"""Another submitted contract still in Active Rental for this vehicle."""
	filters: dict = {"vehicle": vehicle, "docstatus": 1, "status": "Active Rental"}
	rows = frappe.get_all("Rental Contract", filters=filters, pluck="name", limit=20)
	for name in rows:
		if exclude_contract and name == exclude_contract:
			continue
		return True
	return False
