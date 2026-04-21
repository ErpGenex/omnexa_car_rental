# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime

from omnexa_car_rental.omnexa_car_rental.rental_availability import (
	overlapping_confirmed_bookings,
	overlapping_submitted_contracts,
	vehicle_has_other_active_rental,
)


class RentalContract(Document):
	def validate(self):
		if get_datetime(self.contract_end) <= get_datetime(self.contract_start):
			frappe.throw(_("Contract End must be after Contract Start."), title=_("Contract"))

		self._sync_from_booking()
		self._validate_vehicle_org_match()
		self._validate_no_double_booking()
		self._validate_contract_controls()

	def before_submit(self):
		if self.status == "Draft":
			self.status = "Active Rental"
		st = frappe.db.get_value("Vehicle", self.vehicle, "status")
		if st in ("Maintenance", "Out of Service"):
			frappe.throw(
				_("Vehicle is {0}. Cannot start rental.").format(_(st)),
				title=_("Vehicle"),
			)

	def on_submit(self):
		frappe.db.set_value("Vehicle", self.vehicle, "status", "Rented")
		if self.booking:
			frappe.db.set_value("Rental Booking", self.booking, "booking_status", "Converted")
			frappe.db.set_value("Rental Booking", self.booking, "rental_contract", self.name)

	def on_cancel(self):
		if not vehicle_has_other_active_rental(self.vehicle, exclude_contract=self.name):
			frappe.db.set_value("Vehicle", self.vehicle, "status", "Available")

	def on_update_after_submit(self):
		if self.has_value_changed("status") and self.status in ("Returned", "Closed", "Cancelled"):
			if not vehicle_has_other_active_rental(self.vehicle, exclude_contract=self.name):
				frappe.db.set_value("Vehicle", self.vehicle, "status", "Available")

	def _sync_from_booking(self):
		if not self.booking:
			return
		b = frappe.get_cached_doc("Rental Booking", self.booking)
		if not self.customer_profile:
			self.customer_profile = b.customer_profile
		if not self.vehicle:
			self.vehicle = b.vehicle
		if not self.company:
			self.company = b.company
		if not self.branch:
			self.branch = b.branch
		if not self.rental_mode:
			self.rental_mode = b.rental_mode
		if not self.contract_start:
			self.contract_start = b.start_datetime
		if not self.contract_end:
			self.contract_end = b.end_datetime
		if not (self.total_amount or 0) and (b.estimated_amount or 0):
			self.total_amount = b.estimated_amount

	def _validate_vehicle_org_match(self):
		v = frappe.db.get_value("Vehicle", self.vehicle, ["company", "branch"], as_dict=True)
		if not v:
			frappe.throw(_("Vehicle not found."), title=_("Vehicle"))
		if v.company != self.company:
			frappe.throw(_("Vehicle belongs to another company."), title=_("Vehicle"))
		if v.branch != self.branch:
			frappe.throw(_("Vehicle belongs to another branch."), title=_("Vehicle"))

	def _validate_no_double_booking(self):
		excl_contract = None if self.is_new() else self.name
		overlap = overlapping_submitted_contracts(
			self.vehicle,
			self.contract_start,
			self.contract_end,
			exclude_contract=excl_contract,
		)
		if overlap:
			frappe.throw(
				_("Vehicle has an overlapping active contract: {0}").format(", ".join(overlap[:3])),
				title=_("Availability"),
			)

		excl_booking = self.booking or None
		book_ov = overlapping_confirmed_bookings(
			self.vehicle,
			self.contract_start,
			self.contract_end,
			exclude_booking=excl_booking,
		)
		if book_ov:
			frappe.throw(
				_("Vehicle has overlapping confirmed booking(s): {0}").format(", ".join(book_ov[:3])),
				title=_("Availability"),
			)

	def _validate_contract_controls(self):
		if not self.customer_profile:
			frappe.throw(_("Customer Profile is mandatory."), title=_("Contract"))
		if not self.vehicle:
			frappe.throw(_("Vehicle is mandatory."), title=_("Contract"))
		if flt(self.total_amount) <= 0:
			frappe.throw(_("Total Amount must be greater than zero."), title=_("Contract"))
