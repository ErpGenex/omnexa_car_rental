import frappe
from frappe import _
from frappe.model.document import Document


class Vehicle(Document):
	def validate(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch does not exist."), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Branch"))

	def on_trash(self):
		if frappe.db.exists("Rental Contract", {"vehicle": self.name, "docstatus": 1, "status": "Active Rental"}):
			frappe.throw(_("Cannot delete vehicle with an active rental contract."), title=_("Vehicle"))

