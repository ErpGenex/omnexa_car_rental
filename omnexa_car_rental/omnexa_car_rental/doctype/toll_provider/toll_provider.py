# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TollProvider(Document):
	def validate(self):
		if self.provider_code:
			self.provider_code = self.provider_code.strip().upper()
		if self.deduplication_window_seconds is not None and self.deduplication_window_seconds < 0:
			frappe.throw(_("Dedup window cannot be negative."))
