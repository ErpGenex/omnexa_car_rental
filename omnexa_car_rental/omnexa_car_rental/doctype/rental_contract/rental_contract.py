import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime


class RentalContract(Document):
	def validate(self):
		if get_datetime(self.contract_end) <= get_datetime(self.contract_start):
			frappe.throw(_("Contract End must be after Contract Start."), title=_("Contract"))

