import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime


class RentalBooking(Document):
	def validate(self):
		if get_datetime(self.end_datetime) <= get_datetime(self.start_datetime):
			frappe.throw(_("End Date-Time must be after Start Date-Time."), title=_("Booking"))

