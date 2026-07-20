# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Mobile PWA + native app bridge APIs."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_pwa_config() -> dict:
	return {
		"manifest": "/assets/omnexa_car_rental/pwa/manifest.json",
		"service_worker": "/assets/omnexa_car_rental/pwa/sw.js",
		"api_version": "global-rental-4",
		"features": ["booking", "pickup", "return", "payments", "gps"]}


@frappe.whitelist()
def get_ios_config() -> dict:
	return {"platform": "ios", "min_version": "16.0", "bundle_id": "com.omnexa.carrental", "api_base": "/api/method/"
	}


@frappe.whitelist()
def get_android_config() -> dict:
	return {"platform": "android", "min_sdk": 26, "package": "com.omnexa.carrental", "api_base": "/api/method/"
	}


@frappe.whitelist(allow_guest=True)
def live_chat_session(customer_profile: str | None = None) -> dict:
	return {
		"session_id": frappe.generate_hash(length=12),
		"status": "connected",
		"customer_profile": customer_profile,
		"message": _("Live chat session started.")
	}


@frappe.whitelist()
def register_device_token(platform: str, device_token: str, app_version: str | None = None) -> dict:
	doc = frappe.get_doc(
		{
			"doctype": "Rental Mobile Device Token",
			"user": frappe.session.user,
			"platform": platform,
			"device_token": device_token,
			"app_version": app_version,
			"is_active": 1
	}
	)
	doc.insert(ignore_permissions=True)
	return {"token": doc.name
	}
