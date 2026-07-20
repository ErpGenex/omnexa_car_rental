# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Customer wallet, blacklist, CRM, credit limits."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_wallet_balance(customer_profile: str) -> dict:
	wallet = frappe.db.get_value(
		"Rental Customer Wallet",
		{"customer_profile": customer_profile, "status": "Active"
	},
		["name", "balance", "currency"],
		as_dict=True,
	)
	return wallet or {"balance": 0, "currency": frappe.defaults.get_global_default("currency")
	}


@frappe.whitelist()
def top_up_wallet(customer_profile: str, amount: float, company: str, branch: str) -> dict:
	wallet_name = frappe.db.get_value("Rental Customer Wallet", {"customer_profile": customer_profile, "status": "Active"
	})
	if wallet_name:
		w = frappe.get_doc("Rental Customer Wallet", wallet_name)
		w.balance = flt(w.balance) + flt(amount)
		w.save()
	else:
		w = frappe.get_doc(
			{
				"doctype": "Rental Customer Wallet",
				"customer_profile": customer_profile,
				"company": company,
				"branch": branch,
				"balance": flt(amount),
				"status": "Active"
	}
		)
		w.insert()
	return {"wallet": w.name, "balance": w.balance
	}


@frappe.whitelist()
def check_customer_risk(customer_profile: str) -> dict:
	blacklisted = frappe.db.exists("Rental Customer Blacklist", {"customer_profile": customer_profile, "status": "Active"
	})
	score = frappe.db.get_value("Rental Customer Blacklist", {"customer_profile": customer_profile, "status": "Active"
	}, "risk_score") or 10
	return {"blacklisted": bool(blacklisted), "risk_score": int(score), "allowed": not bool(blacklisted)
	}


@frappe.whitelist()
def launch_crm_campaign(campaign_name: str, segment: str, channel: str, company: str, branch: str) -> dict:
	doc = frappe.get_doc(
		{
			"doctype": "Rental CRM Campaign",
			"campaign_name": campaign_name,
			"segment": segment,
			"channel": channel,
			"company": company,
			"branch": branch,
			"status": "Scheduled"
	}
	)
	doc.insert()
	return {"campaign": doc.name
	}


@frappe.whitelist()
def enforce_credit_limit(corporate_account: str, amount: float) -> dict:
	corp = frappe.get_doc("Rental Corporate Account", corporate_account)
	limit = flt(corp.get("credit_limit") or 0)
	if limit and flt(amount) > limit:
		frappe.throw(_("Credit limit exceeded."), title=_("Credit Limit"))
	return {"allowed": True, "credit_limit": limit
	}
