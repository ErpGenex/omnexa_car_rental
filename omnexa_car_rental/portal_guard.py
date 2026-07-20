# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Restrict car rental portal users to allowed desk routes and APIs."""

from __future__ import annotations

import json

import frappe
from frappe import _

CUSTOMER_PORTAL_ROLE = "Car Rental Customer Portal"
VENDOR_PORTAL_ROLE = "Car Rental Vendor Portal"
STAFF_CAR_RENTAL_ROLES = frozenset({"Car Rental Manager", "Car Rental User", "System Manager"})

PORTAL_HOME_ROUTES: dict[str, str] = {
	CUSTOMER_PORTAL_ROLE: "/app/car-rental-customer-portal",
	VENDOR_PORTAL_ROLE: "/app/car-rental-workshop-vendor-portal",
}

PORTAL_WORKSPACE_SPECS: dict[str, dict] = {
	CUSTOMER_PORTAL_ROLE: {
		"name": "car-rental-ws-customer",
		"title": "Car Rental Customer Hub",
		"label": "Customer Portal",
		"icon": "car-rental-customer",
	},
	VENDOR_PORTAL_ROLE: {
		"name": "car-rental-ws-vendor",
		"title": "Car Rental Vendor Hub",
		"label": "Vendor Portal",
		"icon": "car-rental-vendor",
	},
}

CUSTOMER_ALLOWED_PAGES = frozenset(
	{
		"car-rental-customer-portal",
	}
)

VENDOR_ALLOWED_PAGES = frozenset(
	{
		"car-rental-workshop-vendor-portal",
	}
)

CUSTOMER_ALLOWED_DOCTYPES = frozenset(
	{
		"car-rental-booking",
		"car-rental-vehicle",
		"sales-invoice",
	}
)

VENDOR_ALLOWED_DOCTYPES = frozenset(
	{
		"car-rental-workshop-order",
		"car-rental-vehicle",
	}
)


def portal_role_for_user(user: str | None = None) -> str | None:
	user = user or frappe.session.user
	if not user or user == "Guest":
		return None
	roles = set(frappe.get_roles(user))
	if CUSTOMER_PORTAL_ROLE in roles and not roles & STAFF_CAR_RENTAL_ROLES:
		return CUSTOMER_PORTAL_ROLE
	if VENDOR_PORTAL_ROLE in roles and not roles & STAFF_CAR_RENTAL_ROLES:
		return VENDOR_PORTAL_ROLE
	return None


def portal_allowed_pages(role: str | None) -> frozenset[str]:
	if role == CUSTOMER_PORTAL_ROLE:
		return CUSTOMER_ALLOWED_PAGES
	if role == VENDOR_PORTAL_ROLE:
		return VENDOR_ALLOWED_PAGES
	return frozenset()


def portal_allowed_doctypes(role: str | None) -> frozenset[str]:
	if role == CUSTOMER_PORTAL_ROLE:
		return CUSTOMER_ALLOWED_DOCTYPES
	if role == VENDOR_PORTAL_ROLE:
		return VENDOR_ALLOWED_DOCTYPES
	return frozenset()


def portal_home_route(user: str | None = None) -> str | None:
	role = portal_role_for_user(user)
	return PORTAL_HOME_ROUTES.get(role or "") if role else None


def extend_bootinfo(bootinfo):
	"""Expose portal restrictions to desk JS."""
	role = portal_role_for_user()
	if not role:
		return
	bootinfo.car_rental_portal = {
		"portal_only": True,
		"portal_role": role,
		"home_route": PORTAL_HOME_ROUTES[role],
		"allowed_pages": sorted(portal_allowed_pages(role)),
		"allowed_doctypes": sorted(portal_allowed_doctypes(role)),
	}


def ensure_car_rental_workspace_portal_roles() -> dict:
	"""Hide full Car Rental workspace from portal users; add minimal customer/vendor workspaces."""
	from omnexa_car_rental.api.car_rental_role_demo import CAR_RENTAL_STAFF_ROLES

	stats = {"car_rental_roles_set": 0, "customer_ws": False, "vendor_ws": False}
	staff_roles = [r for r in CAR_RENTAL_STAFF_ROLES if frappe.db.exists("Role", r)]

	if frappe.db.exists("Workspace", "Car Rental"):
		ws = frappe.get_doc("Workspace", "Car Rental")
		ws.set("roles", [])
		for role in staff_roles:
			ws.append("roles", {"role": role})
		ws.flags.ignore_permissions = True
		ws.save()
		stats["car_rental_roles_set"] = len(staff_roles)
		frappe.db.commit()

	try:
		stats["customer_ws"] = _ensure_portal_workspace(
			CUSTOMER_PORTAL_ROLE,
			[
				("Page", "car-rental-customer-portal", "Customer Portal"),
				("DocType", "Car Rental Booking", "My Bookings"),
				("DocType", "Car Rental Vehicle", "Vehicles"),
				("DocType", "Sales Invoice", "Invoices"),
			],
		)
	except Exception as exc:
		stats["customer_ws_error"] = str(exc)[:200]
	try:
		stats["vendor_ws"] = _ensure_portal_workspace(
			VENDOR_PORTAL_ROLE,
			[
				("Page", "car-rental-workshop-vendor-portal", "Vendor Portal"),
				("DocType", "Car Rental Workshop Order", "Workshop Orders"),
				("DocType", "Car Rental Vehicle", "Vehicles"),
			],
		)
	except Exception as exc:
		stats["vendor_ws_error"] = str(exc)[:200]
	frappe.clear_cache(doctype="Workspace")
	return stats


def _ensure_portal_workspace(role: str, links: list[tuple]) -> bool:
	if not frappe.db.exists("Role", role):
		return False
	spec = PORTAL_WORKSPACE_SPECS[role]
	name = spec["name"]
	if frappe.db.exists("Workspace", name):
		ws = frappe.get_doc("Workspace", name)
	else:
		ws = frappe.new_doc("Workspace")
		ws.update(
			{
				"name": name,
				"label": spec["label"],
				"title": spec["title"],
				"module": "Omnexa Car Rental",
				"icon": spec["icon"],
				"public": 0,
				"is_hidden": 0,
			}
		)
	ws.set("roles", [])
	ws.append("roles", {"role": role})
	ws.set("links", [])
	for link_type, link_to, link_label in links:
		ws.append(
			"links",
			{
				"type": "Link",
				"link_type": link_type,
				"link_to": link_to,
				"label": link_label,
				"hidden": 0,
				"onboard": 0,
				"is_query_report": 0,
			},
		)
	shortcuts = []
	content = [{"id": "hdr", "type": "header", "data": {"text": f"<b>{spec['label']}</b>", "col": 12}}]
	for idx, (_lt, link_to, link_label) in enumerate(links):
		shortcuts.append(
			{
				"type": "DocType" if _lt == "DocType" else "Page",
				"link_to": link_to,
				"label": link_label,
				"color": "Blue",
			}
		)
		content.append(
			{
				"id": f"sc{idx}",
				"type": "shortcut",
				"data": {"shortcut_name": link_label, "col": 4},
			}
		)
	ws.shortcuts = []
	for sc in shortcuts:
		ws.append("shortcuts", sc)

	ws.content = json.dumps(content, separators=(",", ":"))
	ws.flags.ignore_permissions = True
	if ws.is_new():
		ws.insert()
	else:
		ws.save()
	return True
