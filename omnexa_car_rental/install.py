# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe

SUPPORTED_FRAPPE_MAJOR = 15


def enforce_supported_frappe_version():
	"""Fail fast when running on unsupported Frappe major versions."""
	version_text = (getattr(frappe, "__version__", "") or "").strip()
	if not version_text:
		return

	major_token = version_text.split(".", 1)[0]
	try:
		major = int(major_token)
	except ValueError:
		return

	if major != SUPPORTED_FRAPPE_MAJOR:
		frappe.throw(
			f"Unsupported Frappe version '{version_text}' for omnexa_car_rental. "
			"Supported range is >=15.0,<16.0.",
			frappe.ValidationError,
		)


def ensure_fleet_roles():
	for role_name in ("Fleet Manager", "Rental Agent"):
		if frappe.db.exists("Role", role_name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 1
	}
		)
		doc.insert(ignore_permissions=True)


def after_install():
	"""Ensure fleet operations roles exist (desk users)."""
	ensure_fleet_roles()


def after_migrate():
	ensure_fleet_roles()
	try:
		from omnexa_car_rental.workspace.car_rental_workspace import sync_car_rental_workspace_menu

		sync_car_rental_workspace_menu(save=True, rebuild=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Omnexa Car Rental: workspace sync failed")
