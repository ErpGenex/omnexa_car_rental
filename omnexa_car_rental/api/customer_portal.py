# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Customer self-service portal APIs."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_portal_config(company: str | None = None) -> dict:
	"""Portal home config for customer self-service."""
	return {
		"portal": "car-rental-customer-portal",
		"booking_api": "omnexa_car_rental.api.web_booking.book_rental_online",
		"quote_api": "omnexa_car_rental.api.web_booking.quote_rental_rate",
		"availability_api": "omnexa_car_rental.api.web_booking.get_available_vehicles",
		"company": company or frappe.defaults.get_global_default("company"),
		"features": ["booking", "payment", "extension", "support"]}


@frappe.whitelist(allow_guest=True)
def request_rental_extension(contract: str, new_end_datetime: str) -> dict:
	doc = frappe.get_doc("Rental Contract", contract)
	doc.contract_end = new_end_datetime
	doc.save(ignore_permissions=True)
	return {"contract": doc.name
, "message": _("Extension request recorded.")
	}
