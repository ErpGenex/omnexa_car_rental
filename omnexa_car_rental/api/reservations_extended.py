# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Extended reservation channels."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def create_group_booking(corporate_account: str, vehicle_count: int, start_datetime: str, end_datetime: str) -> dict:
	corp = frappe.get_doc("Rental Corporate Account", corporate_account)
	branch = frappe.db.get_value("Branch", {"company": corp.company}, "name")
	doc = frappe.get_doc(
		{
			"doctype": "Rental Group Booking",
			"corporate_account": corporate_account,
			"vehicle_count": vehicle_count,
			"start_datetime": start_datetime,
			"end_datetime": end_datetime,
			"company": corp.company,
			"branch": branch,
			"status": "Confirmed",
		}
	)
	doc.insert()
	return {"group_booking": doc.name}


@frappe.whitelist()
def subscribe_rental_plan(customer_profile: str, plan_code: str) -> dict:
	plan = frappe.get_doc("Rental Subscription Plan", plan_code)
	return {
		"customer_profile": customer_profile,
		"plan": plan.name,
		"monthly_fee": plan.monthly_fee,
		"status": "Active",
	}


@frappe.whitelist()
def franchise_channel_booking(agent_code: str, payload: str | dict) -> dict:
	agent = frappe.get_doc("Rental Franchise Agent", agent_code)
	data = frappe.parse_json(payload) if isinstance(payload, str) else frappe._dict(payload or {})
	data.company = data.company or agent.company
	data.branch = data.branch or agent.branch
	from omnexa_car_rental.api.web_booking import book_rental_online

	result = book_rental_online(data)
	result["agent"] = agent_code
	return result


@frappe.whitelist()
def walk_in_kiosk_book(payload: str | dict) -> dict:
	from omnexa_car_rental.api.web_booking import book_rental_online

	data = frappe.parse_json(payload) if isinstance(payload, str) else frappe._dict(payload or {})
	data.rental_mode = data.get("rental_mode") or "Walk-In Kiosk"
	return book_rental_online(data)


@frappe.whitelist()
def sync_ota_channel(channel_code: str) -> dict:
	channel = frappe.get_doc("Rental OTA Channel", channel_code)
	return {"channel": channel.name, "synced": True, "endpoint": channel.api_endpoint}
