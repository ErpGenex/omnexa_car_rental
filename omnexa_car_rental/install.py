# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe


def ensure_fleet_roles():
	for role_name in ("Fleet Manager", "Rental Agent"):
		if frappe.db.exists("Role", role_name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 1,
			}
		)
		doc.insert(ignore_permissions=True)


def after_install():
	"""Ensure fleet operations roles exist (desk users)."""
	ensure_fleet_roles()


def after_migrate():
	ensure_fleet_roles()
