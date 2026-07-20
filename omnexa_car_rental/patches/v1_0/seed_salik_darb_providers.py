# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe

from omnexa_car_rental.omnexa_car_rental.toll.darb_client import default_darb_config
from omnexa_car_rental.omnexa_car_rental.toll.salik_client import default_salik_config


def execute():
	for cfg in (default_salik_config(), default_darb_config()):
		code = cfg["provider_code"]
		if frappe.db.exists("Toll Provider", {"provider_code": code}):
			# Ensure polling + sandbox defaults on existing rows
			name = frappe.db.get_value("Toll Provider", {"provider_code": code}, "name")
			doc = frappe.get_doc("Toll Provider", name)
			updated = False
			for key in (
				"endpoint_url",
				"api_transactions_path",
				"default_currency",
				"default_country",
				"integration_type",
				"poll_interval_minutes",
				"auth_header_name",
			):
				if not doc.get(key) and cfg.get(key):
					doc.set(key, cfg[key])
					updated = True
			if doc.integration_type != "API Polling":
				doc.integration_type = "API Polling"
				updated = True
			if not doc.sandbox_mode:
				try:
					has_token = bool(doc.get_password("auth_token", raise_exception=False))
				except Exception:
					has_token = False
				if not has_token:
					doc.sandbox_mode = 1
					updated = True
			if updated:
				doc.save(ignore_permissions=True)
			continue
		doc = frappe.get_doc({"doctype": "Toll Provider", **cfg})
		doc.insert(ignore_permissions=True)
	frappe.db.commit()
