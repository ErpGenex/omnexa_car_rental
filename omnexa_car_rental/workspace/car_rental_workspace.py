# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Full Car Rental workspace — fleet, reservations, tolls, Wave 1 global SIS parity."""

from __future__ import annotations

import json

import frappe

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


def _build_link_rows() -> list[dict]:
	rows: list[dict] = []
	seen: set[tuple[str, str]] = set()
	for section_label, items in WORKSPACE_SECTIONS:
		valid = [(t, to, label) for t, to, label in items if _link_exists(t, to)]
		if not valid:
			continue
		rows.append({"label": section_label, "type": "Card Break", "link_type": "DocType"})
		for link_type, link_to, label in valid:
			key = (link_type, link_to)
			if key in seen:
				continue
			seen.add(key)
			row = {
				"type": "Link",
				"label": label,
				"link_type": link_type,
				"link_to": link_to,
				"is_query_report": 1 if link_type == "Report" else 0,
			}
			if link_type == "Report":
				row["report_ref_doctype"] = frappe.db.get_value("Report", link_to, "ref_doctype")
			rows.append(row)
	return rows


def sync_car_rental_workspace_menu(*, save: bool = True, rebuild: bool = True) -> dict:
	stats = {"sections": 0, "links": 0}
	if not frappe.db.exists("Workspace", "Car Rental"):
		return stats
	rows = _build_link_rows()
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
		if row["type"] == "Link":
			sc = {"type": row["link_type"], "label": row["label"], "link_to": row["link_to"]}
			if row.get("report_ref_doctype"):
				sc["report_ref_doctype"] = row["report_ref_doctype"]
			ws.append("shortcuts", sc)
	if save:
		ws.flags.ignore_permissions = True
		ws.flags.ignore_version = True
		ws.save()
		frappe.clear_cache(doctype="Workspace")
	stats["total_links"] = stats["links"]
	return stats


@frappe.whitelist()
def get_workspace_coverage() -> dict:
	rows = _build_link_rows()
	link_rows = [r for r in rows if r.get("type") == "Link"]
	return {"sections": len([r for r in rows if r.get("type") == "Card Break"]), "links_catalogued": len(link_rows)}
