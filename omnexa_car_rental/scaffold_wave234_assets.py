#!/usr/bin/env python3
"""Wave 2–4 pages, reports, PWA assets."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "omnexa_car_rental"
PUBLIC = ROOT / "public"
ROLES = [{"role": "System Manager"}, {"role": "Fleet Manager"}, {"role": "Rental Agent"}]

PAGES = [
	("car_rental_customer_portal", "car-rental-customer-portal", "Car Rental Customer Portal", "Self-service booking, payments, extensions"),
	("car_rental_agent_tablet", "car-rental-agent-tablet", "Agent Tablet Check-In/Out", "Counter check-in and return workflow"),
	("car_rental_walk_in_kiosk", "car-rental-walk-in-kiosk", "Walk-In Kiosk", "Walk-in rental kiosk mode"),
	("car_rental_workshop_vendor_portal", "car-rental-workshop-vendor-portal", "Workshop Vendor Portal", "Vendor maintenance portal"),
	("car_rental_predictive_analytics", "car-rental-predictive-analytics", "Predictive Analytics Board", "Demand, maintenance, churn analytics"),
	("car_rental_franchise_dashboard", "car-rental-franchise-dashboard", "Franchise Rollup Dashboard", "Multi-branch franchise KPIs"),
]

REPORTS = [
	("cost_per_vehicle_day", "Vehicle", "Cost Per Vehicle Day"),
]


def _page(folder: str, page_name: str, title: str, hint: str) -> None:
	path = APP / "page" / folder
	path.mkdir(parents=True, exist_ok=True)
	(path / f"{folder}.json").write_text(
		json.dumps(
			{"doctype": "Page", "module": "Omnexa Car Rental", "name": page_name, "page_name": page_name, "standard": "Yes", "title": title, "roles": ROLES},
			indent="\t",
		)
		+ "\n"
	)
	(path / f"{folder}.js").write_text(
		f'frappe.pages["{page_name}"].on_page_load = function (wrapper) {{\n'
		f'\tconst page = frappe.ui.make_app_page({{ parent: wrapper, title: __("{title}"), single_column: true }});\n'
		f'\t$(page.body).html(`<div class="p-4"><h5>{title}</h5><p class="text-muted">${{__("{hint}")}}</p></div>`);\n'
		f"}};\n"
	)
	(path / f"{folder}.py").write_text("")
	(path / "__init__.py").write_text("")


def _report(folder: str, ref: str, title: str) -> None:
	path = APP / "report" / folder
	path.mkdir(parents=True, exist_ok=True)
	(path / f"{folder}.json").write_text(
		json.dumps(
			{
				"add_total_row": 0,
				"columns": [],
				"disabled": 0,
				"doctype": "Report",
				"is_standard": "Yes",
				"module": "Omnexa Car Rental",
				"name": title,
				"ref_doctype": ref,
				"report_name": title,
				"report_type": "Script Report",
				"roles": [{"role": "System Manager"}, {"role": "Fleet Manager"}, {"role": "Report Manager"}],
			},
			indent="\t",
		)
		+ "\n"
	)
	(path / f"{folder}.py").write_text(
		f'import frappe\nfrom frappe.utils import flt\n\n\ndef execute(filters=None):\n'
		f'\tcolumns = [\n\t\t{{"label": "Vehicle", "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 160}},\n'
		f'\t\t{{"label": "Cost/Day", "fieldname": "cost_per_day", "fieldtype": "Currency", "width": 120}},\n'
		f'\t\t{{"label": "Cost/KM", "fieldname": "cost_per_km", "fieldtype": "Currency", "width": 120}},\n\t]\n'
		f'\tdata = []\n\tfor v in frappe.get_all("Vehicle", fields=["name", "plate_number"], limit=200):\n'
		f'\t\tmaint = frappe.db.sql("SELECT COALESCE(SUM(cost_amount),0) FROM `tabVehicle Maintenance Record` WHERE vehicle=%s", v.name)[0][0]\n'
		f'\t\tdata.append({{"vehicle": v.name, "cost_per_day": flt(maint) / 30.0, "cost_per_km": flt(maint) / 1000.0}})\n'
		f'\treturn columns, data\n'
	)
	(path / f"{folder}.html").write_text("")
	(path / "__init__.py").write_text("")


def _pwa() -> None:
	pwa = PUBLIC / "pwa"
	pwa.mkdir(parents=True, exist_ok=True)
	(pwa / "manifest.json").write_text(
		json.dumps(
			{
				"name": "Omnexa Car Rental",
				"short_name": "OmnexaRent",
				"start_url": "/car-rental-portal",
				"display": "standalone",
				"background_color": "#0f172a",
				"theme_color": "#2563eb",
				"icons": [{"src": "/assets/omnexa_car_rental/car-rental.svg", "sizes": "192x192", "type": "image/svg+xml"}],
			},
			indent=2,
		)
		+ "\n"
	)
	(pwa / "sw.js").write_text(
		"self.addEventListener('install', (e) => { self.skipWaiting(); });\n"
		"self.addEventListener('activate', (e) => { e.waitUntil(clients.claim()); });\n"
		"self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request)); });\n"
	)


def main() -> None:
	for folder, page_name, title, hint in PAGES:
		_page(folder, page_name, title, hint)
	for folder, ref, title in REPORTS:
		_report(folder, ref, title)
	_pwa()
	print(f"Scaffolded {len(PAGES)} pages, {len(REPORTS)} reports, PWA")


if __name__ == "__main__":
	main()
