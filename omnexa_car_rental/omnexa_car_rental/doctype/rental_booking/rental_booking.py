# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime

from omnexa_car_rental.omnexa_car_rental.rental_availability import (
	overlapping_confirmed_bookings,
	overlapping_submitted_contracts,
)


class RentalBooking(Document):
	def validate(self):
		if get_datetime(self.end_datetime) <= get_datetime(self.start_datetime):
			frappe.throw(_("End Date-Time must be after Start Date-Time."), title=_("Booking"))

		self._validate_vehicle_org_match()
		self._validate_lifecycle_controls()
		if self.booking_status == "Confirmed":
			self._validate_no_overlap()

	def _validate_vehicle_org_match(self):
		v = frappe.db.get_value("Vehicle", self.vehicle, ["company", "branch"], as_dict=True)
		if not v:
			frappe.throw(_("Vehicle not found."), title=_("Vehicle"))
		if v.company != self.company:
			frappe.throw(_("Vehicle belongs to another company."), title=_("Vehicle"))
		if v.branch != self.branch:
			frappe.throw(_("Vehicle belongs to another branch."), title=_("Vehicle"))

	def _validate_no_overlap(self):
		excl_book = self.name if not self.is_new() else None
		other_books = overlapping_confirmed_bookings(
			self.vehicle, self.start_datetime, self.end_datetime, exclude_booking=excl_book
		)
		if other_books:
			frappe.throw(
				_("Overlapping confirmed booking(s): {0}").format(", ".join(other_books[:3])),
				title=_("Availability"),
			)
		contracts = overlapping_submitted_contracts(
			self.vehicle, self.start_datetime, self.end_datetime, exclude_contract=None
		)
		if contracts:
			frappe.throw(
				_("Period overlaps active rental contract(s): {0}").format(", ".join(contracts[:3])),
				title=_("Availability"),
			)

	def _validate_lifecycle_controls(self):
		if self.booking_status in {"Confirmed", "Converted"}:
			if not self.customer_profile:
				frappe.throw(_("Customer Profile is mandatory for confirmed bookings."), title=_("Booking"))
			if not self.vehicle:
				frappe.throw(_("Vehicle is mandatory for confirmed bookings."), title=_("Booking"))
			if flt(self.estimated_amount) <= 0:
				frappe.throw(_("Estimated Amount must be greater than zero for confirmed bookings."), title=_("Pricing"))
