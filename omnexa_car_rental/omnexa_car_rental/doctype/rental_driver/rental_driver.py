# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class RentalDriver(Document):
	def validate(self):
		if self.status == "Active" and self.license_expiry_date:
			if getdate(self.license_expiry_date) < getdate(today()):
				frappe.throw(
					_("License is expired. Renew the license or change status from Active."),
					title=_("Driver"),
				)
