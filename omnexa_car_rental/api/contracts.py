# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Contract e-sign, versioning, approvals."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def sign_rental_contract(rental_contract: str, signed_by: str, provider: str = "Omnexa E-Sign") -> dict:
	sig = frappe.get_doc(
		{
			"doctype": "Rental Contract Signature",
			"rental_contract": rental_contract,
			"signed_by": signed_by,
			"signed_on": now_datetime(),
			"signature_provider": provider,
			"signature_token": frappe.generate_hash(length=16),
			"status": "Signed",
			**_company_branch_from_contract(rental_contract)}
	)
	sig.insert()
	return {"signature": sig.name, "token": sig.signature_token
	}


@frappe.whitelist()
def create_contract_version(rental_contract: str, change_summary: str) -> dict:
	last = frappe.db.get_value("Rental Contract Version", {"rental_contract": rental_contract
	}, "max(version_no)") or 0
	ver = frappe.get_doc(
		{
			"doctype": "Rental Contract Version",
			"rental_contract": rental_contract,
			"version_no": int(last) + 1,
			"effective_from": frappe.utils.today(),
			"change_summary": change_summary,
			"status": "Active",
			**_company_branch_from_contract(rental_contract)}
	)
	ver.insert()
	return {"version": ver.name, "version_no": ver.version_no
	}


@frappe.whitelist()
def submit_contract_approval(rental_contract: str, approver: str, level: int = 1) -> dict:
	doc = frappe.get_doc(
		{
			"doctype": "Rental Contract Approval",
			"rental_contract": rental_contract,
			"approver": approver,
			"approval_level": level,
			"status": "Pending",
			**_company_branch_from_contract(rental_contract)}
	)
	doc.insert()
	return {"approval": doc.name
	}


def _company_branch_from_contract(contract: str) -> dict:
	row = frappe.db.get_value("Rental Contract", contract, ["company", "branch"], as_dict=True) or {}
	return {"company": row.get("company"), "branch": row.get("branch")
	}
