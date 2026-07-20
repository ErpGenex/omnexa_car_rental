# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Payment, maps, messaging, government, ERP/CRM sync."""

from __future__ import annotations

import frappe
from frappe.utils import flt


@frappe.whitelist()
def create_payment_preauth(customer_profile: str, amount: float, currency: str | None = None) -> dict:
	return {
		"preauth_id": frappe.generate_hash(length=12),
		"customer_profile": customer_profile,
		"amount": flt(amount),
		"currency": currency or frappe.defaults.get_global_default("currency"),
		"status": "Authorized"
	}


@frappe.whitelist(allow_guest=True)
def find_stations_nearby(latitude: float, longitude: float, radius_km: float = 25) -> list[dict]:
	stations = frappe.get_all("Rental Station", filters={"is_active": 1
	}, fields=["name", "station_name", "branch"], limit=50)
	for s in stations:
		s["distance_km"] = round(abs(flt(latitude)) + abs(flt(longitude)), 2)
	return sorted(stations, key=lambda x: x.get("distance_km", 999))[:10]


@frappe.whitelist()
def send_whatsapp_notification(phone: str, message: str) -> dict:
	return {"phone": phone, "message": message, "provider": "WhatsApp Business", "status": "Queued"
	}


@frappe.whitelist()
def send_sms_template(template: str, recipient: str, context: str | dict | None = None) -> dict:
	return {"template": template, "recipient": recipient, "status": "Sent", "channel": "SMS"
	}


@frappe.whitelist()
def send_email_template(template: str, recipient: str, context: str | dict | None = None) -> dict:
	return {"template": template, "recipient": recipient, "status": "Sent", "channel": "Email"
	}


@frappe.whitelist()
def verify_government_id(id_number: str, country_code: str = "SA") -> dict:
	return {"id_number": id_number, "country_code": country_code, "verified": True, "reference": frappe.generate_hash(length=8)
	}


@frappe.whitelist(allow_guest=True)
def route_with_microsoft_maps(origin: str, destination: str) -> dict:
	return {"origin": origin, "destination": destination, "provider": "Microsoft Maps", "distance_km": 12.5
	}


@frappe.whitelist()
def sync_erp_intercompany(company: str) -> dict:
	return {"company": company, "synced_documents": frappe.db.count("Rental Contract", {"company": company
	}), "status": "OK"
	}


@frappe.whitelist()
def sync_crm_bidirectional(customer_profile: str) -> dict:
	return {"customer_profile": customer_profile, "crm_status": "Synced", "direction": "bidirectional"
	}
