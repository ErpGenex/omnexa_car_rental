# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Full Car Rental workspace — fleet, reservations, tolls, Wave 1 global SIS parity."""

from __future__ import annotations

import json

import frappe

from omnexa_core.omnexa_core.vertical_workspace_sync import (
	build_link_rows_for_app,
	drop_missing_workspace_dashboard_links,
)

WorkspaceLink = tuple[str, str, str]

WORKSPACE_SECTIONS: list[tuple[str, list[WorkspaceLink]]] = [
	(
		"📊 Dashboards & Portals",
		[
			("Page", "car-rental-executive-dashboard", "Executive Dashboard"),
			("Page", "car-rental-booking-desk", "Online Booking Desk"),
			("Page", "car-rental-customer-portal", "Customer Portal"),
			("Page", "car-rental-agent-tablet", "Agent Tablet"),
			("Page", "car-rental-walk-in-kiosk", "Walk-In Kiosk"),
			("Page", "car-rental-workshop-vendor-portal", "Workshop Vendor"),
			("Page", "car-rental-predictive-analytics", "Predictive Analytics"),
			("Page", "car-rental-franchise-dashboard", "Franchise Dashboard"),
		],
	),
	(
		"🚗 Fleet & catalog",
		[
			("DocType", "Vehicle", "Vehicle"),
			("DocType", "Rental Vehicle Group", "Vehicle Group"),
			("DocType", "Rental Station", "Rental Station"),
			("DocType", "Supplier Fleet Contract", "Supplier Fleet Contract"),
			("DocType", "Vehicle Insurance Policy", "Insurance Policy"),
		],
	),
	(
		"📅 Reservations & pricing",
		[
			("DocType", "Rental Rate Plan", "Rate Plan"),
			("DocType", "Rental Extra Service", "Extra Services"),
			("DocType", "Rental Booking", "Rental Booking"),
			("DocType", "Rental Contract", "Rental Contract"),
			("DocType", "Rental Vehicle Inspection", "Vehicle Inspection"),
			("DocType", "Rental Group Booking", "Group Booking"),
			("DocType", "Rental Subscription Plan", "Subscription Plan"),
			("DocType", "Rental Franchise Agent", "Franchise Agent"),
			("DocType", "Rental OTA Channel", "OTA Channel"),
			("DocType", "Rental Contract Signature", "E-Signature"),
			("DocType", "Rental Contract Version", "Contract Version"),
			("DocType", "Rental Leasing Template", "Leasing Template"),
			("DocType", "Rental Contract Approval", "Contract Approval"),
		],
	),
	(
		"👥 Customers & drivers",
		[
			("DocType", "Customer Profile", "Customer Profile"),
			("DocType", "Customer", "Customer"),
			("DocType", "Rental Driver", "Rental Driver"),
			("DocType", "Rental Corporate Account", "Corporate Account"),
			("DocType", "Rental Loyalty Tier", "Loyalty Tier"),
			("DocType", "Rental Customer Wallet", "Customer Wallet"),
			("DocType", "Rental Customer Blacklist", "Blacklist"),
			("DocType", "Rental CRM Campaign", "CRM Campaign"),
			("DocType", "Rental Driver Violation", "Driver Violation"),
			("DocType", "Rental Driver Training", "Driver Training"),
		],
	),
	(
		"🔧 Maintenance & risk",
		[
			("DocType", "Maintenance Work Order", "Work Order"),
			("DocType", "Vehicle Maintenance Record", "Maintenance Record"),
			("DocType", "Vehicle Fuel Log", "Fuel Log"),
			("DocType", "Vehicle Damage Report", "Damage Report"),
			("DocType", "Rental Preventive Schedule", "Preventive Schedule"),
			("DocType", "Rental Predictive Alert", "Predictive Alert"),
			("DocType", "Rental Insurance Claim", "Insurance Claim"),
			("DocType", "Rental Warranty Claim", "Warranty Claim"),
			("DocType", "Rental Downtime SLA", "Downtime SLA"),
			("DocType", "Rental Spare Part", "Spare Parts"),
		],
	),
	(
		"📡 Telematics & lifecycle",
		[
			("DocType", "Vehicle GPS Track", "GPS Track"),
			("DocType", "Rental Geofence Zone", "Geofence Zone"),
			("DocType", "EV Charging Session", "EV Charging"),
			("DocType", "Rental Fuel IoT Reading", "Fuel IoT"),
			("DocType", "Vehicle Acquisition", "Acquisition"),
			("DocType", "Vehicle Disposal", "Disposal"),
			("DocType", "Vehicle Tire Record", "Tire Record"),
			("DocType", "Rental Revenue Recognition", "Revenue Recognition"),
			("DocType", "Rental Country Pack", "Country Pack"),
			("DocType", "Rental DR Runbook", "DR Runbook"),
			("DocType", "Rental ISO Control", "ISO Controls"),
		],
	),
	(
		"🛣️ Tolls & road charges",
		[
			("DocType", "Toll Provider", "Toll Provider"),
			("DocType", "Toll Allocation Rule", "Allocation Rule"),
			("DocType", "Toll Transaction", "Toll Transaction"),
			("DocType", "Toll Invoice Line", "Toll Invoice Line"),
		],
	),
	(
		"💰 Finance",
		[
			("DocType", "Sales Invoice", "Sales Invoice"),
			("DocType", "Payment Entry", "Payment Entry"),
			("DocType", "Journal Entry", "Journal Entry"),
		],
	),
	(
		"📈 Reports · Fleet",
		[
			("Report", "Fleet Utilization", "Fleet Utilization"),
			("Report", "Revenue per Vehicle", "Revenue per Vehicle"),
			("Report", "Maintenance Cost Analysis", "Maintenance Cost"),
			("Report", "Fuel & Energy Cost Summary", "Fuel & Energy"),
		],
	),
	(
		"📈 Reports · Operations",
		[
			("Report", "Rental Booking Pipeline", "Booking Pipeline"),
			("Report", "Rental Contract Summary", "Contract Summary"),
			("Report", "Toll Cost Summary", "Toll Cost Summary"),
			("Report", "Damage & Liability Exposure", "Damage & Liability"),
			("Report", "Cost Per Vehicle Day", "Cost Per Vehicle Day"),
		],
	),
]


def _link_exists(link_type: str, link_to: str) -> bool:
	if link_type == "DocType":
		return bool(frappe.db.exists("DocType", link_to))
	if link_type == "Report":
		return bool(frappe.db.exists("Report", link_to))
	if link_type == "Page":
		return bool(frappe.db.exists("Page", link_to))
	return False


_SHORTCUT_COLORS = ("Blue", "Green", "Orange", "Red", "Cyan", "Purple", "Teal", "Pink", "Yellow")


def _build_link_rows() -> list[dict]:
	return build_link_rows_for_app("omnexa_car_rental", WORKSPACE_SECTIONS)


def _build_shortcuts(link_rows: list[dict]) -> list[dict]:
	"""Workspace home shortcuts — labels must match EditorJS shortcut blocks."""
	shortcuts: list[dict] = []
	idx = 0
	priority_types = ("Page", "DocType", "Report", "Dashboard")
	links = [r for r in link_rows if r.get("type") == "Link"]
	for lt in priority_types:
		for row in links:
			if row.get("link_type") != lt:
				continue
			entry = {
				"label": row["label"],
				"link_to": row["link_to"],
				"type": row["link_type"],
				"color": _SHORTCUT_COLORS[idx % len(_SHORTCUT_COLORS)]
	}
			if lt == "DocType":
				entry["doc_view"] = "List"
			if lt == "Report" and row.get("report_ref_doctype"):
				entry["report_ref_doctype"] = row["report_ref_doctype"]
			shortcuts.append(entry)
			idx += 1
	return shortcuts


def _onboarding_blocks(existing_content: str | None) -> list[dict]:
	if not existing_content:
		return []
	try:
		blocks = json.loads(existing_content)
	except json.JSONDecodeError:
		return []
	return [b for b in blocks if b.get("type") == "onboarding"]


def _build_content(link_rows: list[dict], ws) -> str:
	"""Rebuild workspace home layout — section headers + shortcuts + KPIs + charts."""
	content: list[dict] = []
	content.extend(_onboarding_blocks(ws.content))
	content.append(
		{
			"id": "car-rental-title",
			"type": "header",
			"data": {"text": '<span class="h4"><b>Car Rental</b></span>', "col": 12}
	}
	)

	section_idx = 0
	link_idx = 0
	for row in link_rows:
		if row.get("type") == "Card Break":
			if section_idx:
				content.append({"id": f"car-rental-sp-{section_idx
	}", "type": "spacer", "data": {"col": 12}
	})
			content.append(
				{
					"id": f"car-rental-sec-{section_idx
	}",
					"type": "header",
					"data": {"text": f'<span class="h5"><b>{row["label"]
	}</b></span>', "col": 12}
	}
			)
			section_idx += 1
			continue
		content.append(
			{
				"id": f"car-rental-lnk-{link_idx
	}",
				"type": "shortcut",
				"data": {"shortcut_name": row["label"], "col": 4}
	}
		)
		link_idx += 1

	if ws.number_cards:
		content.append({"id": "car-rental-kpi-sp", "type": "spacer", "data": {"col": 12}
	})
		content.append(
			{
				"id": "car-rental-kpi-h",
				"type": "header",
				"data": {"text": '<span class="h5"><b>📊 KPIs</b></span>', "col": 12}
	}
		)
		for idx, nc in enumerate(ws.number_cards):
			content.append(
				{
					"id": f"car-rental-nc-{idx
	}",
					"type": "number_card",
					"data": {"number_card_name": nc.number_card_name, "col": 4}
	}
			)

	if ws.charts:
		content.append({"id": "car-rental-ch-sp", "type": "spacer", "data": {"col": 12}
	})
		content.append(
			{
				"id": "car-rental-ch-h",
				"type": "header",
				"data": {"text": '<span class="h5"><b>📈 Charts</b></span>', "col": 12}
	}
		)
		for idx, ch in enumerate(ws.charts):
			content.append(
				{
					"id": f"car-rental-ch-{idx
	}",
					"type": "chart",
					"data": {"chart_name": ch.label or ch.chart_name, "col": 4}
	}
			)

	return json.dumps(content, separators=(",", ":"))


def sync_car_rental_workspace_menu(*, save: bool = True, rebuild: bool = True) -> dict:
	stats = {"sections": 0, "links": 0, "shortcuts": 0
	}
	if not frappe.db.exists("Workspace", "Car Rental"):
		return stats
	rows = _build_link_rows()
	link_rows = [r for r in rows if r.get("type") == "Link"]
	new_shortcuts = _build_shortcuts(rows)
	ws = frappe.get_doc("Workspace", "Car Rental")
	if rebuild:
		ws.set("links", [])
		ws.set("shortcuts", [])
	for row in rows:
		if row["type"] == "Card Break":
			stats["sections"] += 1
		else:
			stats["links"] += 1
		ws.append("links", row)
	for sc in new_shortcuts:
		ws.append("shortcuts", sc)
	stats["shortcuts"] = len(new_shortcuts)
	drop_missing_workspace_dashboard_links(ws)
	ws.content = _build_content(rows, ws)
	stats["content_blocks"] = len(json.loads(ws.content))
	if save:
		ws.flags.ignore_permissions = True
		ws.save(ignore_permissions=True, ignore_version=True)
		frappe.clear_cache(doctype="Workspace")
	stats["total_links"] = len(link_rows)
	return stats


@frappe.whitelist()
def get_workspace_coverage() -> dict:
	rows = _build_link_rows()
	link_rows = [r for r in rows if r.get("type") == "Link"]
	return {"sections": len([r for r in rows if r.get("type") == "Card Break"]), "links_catalogued": len(link_rows)
	}
