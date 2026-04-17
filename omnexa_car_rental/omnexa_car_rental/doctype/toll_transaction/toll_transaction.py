# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TollTransaction(Document):
	def validate(self):
		self._validate_unique_external()
		self._sync_company_currency_amount()

	def _validate_unique_external(self):
		tn = frappe.db.get_value(
			"Toll Transaction",
			{"transaction_id": self.transaction_id, "provider": self.provider},
			"name",
		)
		if tn and tn != self.name:
			frappe.throw(
				_("Toll Transaction already exists for this provider and external ID."),
				title=_("Duplicate"),
			)

	def _sync_company_currency_amount(self):
		if self.amount is None:
			return
		rate = flt(self.exchange_rate) or 1.0
		self.amount_company_currency = flt(self.amount) * rate

	def before_insert(self):
		if not self.currency:
			prov = frappe.db.get_value(
				"Toll Provider",
				self.provider,
				["default_currency", "default_country"],
				as_dict=True,
			)
			if prov:
				self.currency = self.currency or prov.default_currency
				self.country = self.country or prov.default_country
