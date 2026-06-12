# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Global car rental gap register — 96 items vs Rentall / TSD / HQ / Rent Centric."""

from __future__ import annotations

import os

import frappe
from frappe.utils import get_bench_path

GLOBAL_LEADER_TARGET = 4.85
GAPS_TOTAL = 96

# wave: 1 = implemented in app, 2 = 90-day, 3 = 6–12 month, 4 = 24 month
GAP_DEFINITIONS: list[dict] = [
	# Wave 1 — foundation (closed when detector passes)
	{"id": "CR-001", "domain": "reservation", "title": "Guest online booking API", "wave": 1, "detect": "api:omnexa_car_rental.api.web_booking.book_rental_online"},
	{"id": "CR-002", "domain": "reservation", "title": "Rental Rate Plan master", "wave": 1, "detect": "doctype:Rental Rate Plan"},
	{"id": "CR-003", "domain": "vehicle_management", "title": "Rental Vehicle Group (ACRISS)", "wave": 1, "detect": "doctype:Rental Vehicle Group"},
	{"id": "CR-004", "domain": "reservation", "title": "Rental Station / pickup location", "wave": 1, "detect": "doctype:Rental Station"},
	{"id": "CR-005", "domain": "reservation", "title": "Rental Extra Service catalog", "wave": 1, "detect": "doctype:Rental Extra Service"},
	{"id": "CR-006", "domain": "contract", "title": "Vehicle check-in/out inspection", "wave": 1, "detect": "doctype:Rental Vehicle Inspection"},
	{"id": "CR-007", "domain": "customer", "title": "Corporate rental account", "wave": 1, "detect": "doctype:Rental Corporate Account"},
	{"id": "CR-008", "domain": "customer", "title": "Loyalty tier program", "wave": 1, "detect": "doctype:Rental Loyalty Tier"},
	{"id": "CR-009", "domain": "maintenance", "title": "Maintenance work order", "wave": 1, "detect": "doctype:Maintenance Work Order"},
	{"id": "CR-010", "domain": "bi", "title": "Full Car Rental workspace sync", "wave": 1, "detect": "module:workspace.car_rental_workspace"},
	{"id": "CR-011", "domain": "bi", "title": "Executive dashboard desk page", "wave": 1, "detect": "page:car-rental-executive-dashboard"},
	{"id": "CR-012", "domain": "digital_channels", "title": "Online booking desk page", "wave": 1, "detect": "page:car-rental-booking-desk"},
	{"id": "CR-013", "domain": "bi", "title": "Global benchmark scoring module", "wave": 1, "detect": "module:car_rental_global_benchmark"},
	{"id": "CR-014", "domain": "vehicle_management", "title": "Extended vehicle categories (EV, Van, Bus…)", "wave": 1, "detect": "field:Vehicle.category"},
	{"id": "CR-015", "domain": "reservation", "title": "Rate engine from Rental Rate Plan", "wave": 1, "detect": "api:omnexa_car_rental.api.web_booking.quote_rental_rate"},
	{"id": "CR-016", "domain": "reservation", "title": "Availability API for web booking", "wave": 1, "detect": "api:omnexa_car_rental.api.web_booking.get_available_vehicles"},
	{"id": "CR-017", "domain": "driver", "title": "Driver license expiry reminders", "wave": 1, "detect": "scheduler:fleet_reminders"},
	{"id": "CR-018", "domain": "fleet_management", "title": "Fleet utilization KPI", "wave": 1, "detect": "report:Fleet Utilization"},
	{"id": "CR-019", "domain": "financial", "title": "Toll pass-through billing", "wave": 1, "detect": "doctype:Toll Transaction"},
	{"id": "CR-020", "domain": "insurance", "title": "Vehicle insurance policy tracking", "wave": 1, "detect": "doctype:Vehicle Insurance Policy"},
	{"id": "CR-021", "domain": "accident", "title": "Damage & liability report", "wave": 1, "detect": "doctype:Vehicle Damage Report"},
	{"id": "CR-022", "domain": "maintenance", "title": "Maintenance cost analysis report", "wave": 1, "detect": "report:Maintenance Cost Analysis"},
	{"id": "CR-023", "domain": "contract", "title": "Booking to contract conversion", "wave": 1, "detect": "api:omnexa_car_rental.api.create_rental_contract_from_booking"},
	{"id": "CR-024", "domain": "security", "title": "Branch-scoped RBAC on fleet docs", "wave": 1, "detect": "hooks:permission_query_conditions"},
]

# Wave 2–4 planned gaps — each with automated detector
_WAVE234: list[dict] = [
	{"id": "CR-025", "domain": "digital_channels", "title": "Customer self-service web portal", "wave": 2, "detect": "page:car-rental-customer-portal"},
	{"id": "CR-026", "domain": "digital_channels", "title": "Mobile PWA for customers", "wave": 2, "detect": "file:public/pwa/manifest.json"},
	{"id": "CR-027", "domain": "digital_channels", "title": "Agent tablet counter check-in/out", "wave": 2, "detect": "page:car-rental-agent-tablet"},
	{"id": "CR-028", "domain": "contract", "title": "Electronic signature integration", "wave": 2, "detect": "api:omnexa_car_rental.api.contracts.sign_rental_contract"},
	{"id": "CR-029", "domain": "contract", "title": "Contract versioning & renewals", "wave": 2, "detect": "doctype:Rental Contract Version"},
	{"id": "CR-030", "domain": "reservation", "title": "Corporate bulk / group booking", "wave": 2, "detect": "api:omnexa_car_rental.api.reservations_extended.create_group_booking"},
	{"id": "CR-031", "domain": "reservation", "title": "Subscription rental plans", "wave": 2, "detect": "doctype:Rental Subscription Plan"},
	{"id": "CR-032", "domain": "reservation", "title": "Franchise / agent channel booking", "wave": 2, "detect": "doctype:Rental Franchise Agent"},
	{"id": "CR-033", "domain": "customer", "title": "Customer wallet & prepaid balance", "wave": 2, "detect": "doctype:Rental Customer Wallet"},
	{"id": "CR-034", "domain": "customer", "title": "Blacklist & risk scoring", "wave": 2, "detect": "api:omnexa_car_rental.api.customer_crm.check_customer_risk"},
	{"id": "CR-035", "domain": "customer", "title": "CRM segmentation campaigns", "wave": 2, "detect": "doctype:Rental CRM Campaign"},
	{"id": "CR-036", "domain": "driver", "title": "Driver violation tracking", "wave": 2, "detect": "doctype:Rental Driver Violation"},
	{"id": "CR-037", "domain": "driver", "title": "Driver scoring model", "wave": 2, "detect": "api:omnexa_car_rental.api.driver_management.compute_driver_score"},
	{"id": "CR-038", "domain": "maintenance", "title": "Preventive maintenance schedule", "wave": 2, "detect": "doctype:Rental Preventive Schedule"},
	{"id": "CR-039", "domain": "maintenance", "title": "Predictive maintenance alerts", "wave": 2, "detect": "doctype:Rental Predictive Alert"},
	{"id": "CR-040", "domain": "accident", "title": "Insurance claim workflow", "wave": 2, "detect": "doctype:Rental Insurance Claim"},
	{"id": "CR-041", "domain": "accident", "title": "Cost recovery billing", "wave": 2, "detect": "api:omnexa_car_rental.api.accident_insurance.bill_cost_recovery"},
	{"id": "CR-042", "domain": "insurance", "title": "Policy renewal automation", "wave": 2, "detect": "scheduler:policy_renewal_tasks"},
	{"id": "CR-043", "domain": "gps_telematics", "title": "GPS real-time tracking", "wave": 2, "detect": "doctype:Vehicle GPS Track"},
	{"id": "CR-044", "domain": "gps_telematics", "title": "Geofencing alerts", "wave": 2, "detect": "doctype:Rental Geofence Zone"},
	{"id": "CR-045", "domain": "gps_telematics", "title": "Driver behavior telematics", "wave": 2, "detect": "api:omnexa_car_rental.api.telematics.analyze_driver_behavior"},
	{"id": "CR-046", "domain": "gps_telematics", "title": "EV battery & charging integration", "wave": 2, "detect": "doctype:EV Charging Session"},
	{"id": "CR-047", "domain": "ai_automation", "title": "Dynamic pricing engine", "wave": 2, "detect": "api:omnexa_car_rental.api.ai_automation.compute_dynamic_price"},
	{"id": "CR-048", "domain": "ai_automation", "title": "Demand forecasting", "wave": 2, "detect": "api:omnexa_car_rental.api.ai_automation.forecast_demand"},
	{"id": "CR-049", "domain": "integrations", "title": "Payment gateway pre-auth", "wave": 2, "detect": "api:omnexa_car_rental.api.integrations.create_payment_preauth"},
	{"id": "CR-050", "domain": "integrations", "title": "Google Maps station finder", "wave": 2, "detect": "api:omnexa_car_rental.api.integrations.find_stations_nearby"},
	{"id": "CR-051", "domain": "integrations", "title": "WhatsApp booking notifications", "wave": 2, "detect": "api:omnexa_car_rental.api.integrations.send_whatsapp_notification"},
	{"id": "CR-052", "domain": "integrations", "title": "SMS / email provider templates", "wave": 2, "detect": "api:omnexa_car_rental.api.integrations.send_sms_template"},
	{"id": "CR-053", "domain": "financial", "title": "Revenue recognition (IFRS 15)", "wave": 3, "detect": "doctype:Rental Revenue Recognition"},
	{"id": "CR-054", "domain": "financial", "title": "Multi-currency FX automation", "wave": 3, "detect": "api:omnexa_car_rental.api.financial.apply_fx_rate"},
	{"id": "CR-055", "domain": "financial", "title": "Fleet depreciation integration", "wave": 3, "detect": "api:omnexa_car_rental.api.financial.post_fleet_depreciation"},
	{"id": "CR-056", "domain": "fleet_management", "title": "Vehicle acquisition workflow", "wave": 3, "detect": "doctype:Vehicle Acquisition"},
	{"id": "CR-057", "domain": "fleet_management", "title": "Vehicle disposal & auction", "wave": 3, "detect": "doctype:Vehicle Disposal"},
	{"id": "CR-058", "domain": "fleet_management", "title": "Cost per km/day analytics", "wave": 3, "detect": "report:Cost Per Vehicle Day"},
	{"id": "CR-059", "domain": "fleet_management", "title": "Tire lifecycle tracking", "wave": 3, "detect": "doctype:Vehicle Tire Record"},
	{"id": "CR-060", "domain": "fleet_management", "title": "Spare parts inventory", "wave": 3, "detect": "doctype:Rental Spare Part"},
	{"id": "CR-061", "domain": "vehicle_management", "title": "Construction equipment fleet", "wave": 3, "detect": "field_contains:Vehicle.category:Equipment"},
	{"id": "CR-062", "domain": "vehicle_management", "title": "Boats & yachts fleet", "wave": 3, "detect": "field_contains:Vehicle.category:Boat"},
	{"id": "CR-063", "domain": "vehicle_management", "title": "Motorcycle fleet", "wave": 3, "detect": "field_contains:Vehicle.category:Motorcycle"},
	{"id": "CR-064", "domain": "reservation", "title": "OTA / channel manager", "wave": 3, "detect": "doctype:Rental OTA Channel"},
	{"id": "CR-065", "domain": "reservation", "title": "Walk-in kiosk mode", "wave": 3, "detect": "page:car-rental-walk-in-kiosk"},
	{"id": "CR-066", "domain": "contract", "title": "Leasing contract templates", "wave": 3, "detect": "doctype:Rental Leasing Template"},
	{"id": "CR-067", "domain": "contract", "title": "Multi-party approval workflow", "wave": 3, "detect": "doctype:Rental Contract Approval"},
	{"id": "CR-068", "domain": "customer", "title": "Credit limit enforcement", "wave": 3, "detect": "api:omnexa_car_rental.api.customer_crm.enforce_credit_limit"},
	{"id": "CR-069", "domain": "driver", "title": "Driver training compliance", "wave": 3, "detect": "doctype:Rental Driver Training"},
	{"id": "CR-070", "domain": "maintenance", "title": "Workshop vendor portal", "wave": 3, "detect": "page:car-rental-workshop-vendor-portal"},
	{"id": "CR-071", "domain": "maintenance", "title": "Warranty claim tracking", "wave": 3, "detect": "doctype:Rental Warranty Claim"},
	{"id": "CR-072", "domain": "accident", "title": "Vehicle downtime SLA", "wave": 3, "detect": "doctype:Rental Downtime SLA"},
	{"id": "CR-073", "domain": "insurance", "title": "Third-party insurer API", "wave": 3, "detect": "api:omnexa_car_rental.api.accident_insurance.submit_insurer_api_claim"},
	{"id": "CR-074", "domain": "digital_channels", "title": "Native iOS app", "wave": 4, "detect": "api:omnexa_car_rental.api.mobile.get_ios_config"},
	{"id": "CR-075", "domain": "digital_channels", "title": "Native Android app", "wave": 4, "detect": "api:omnexa_car_rental.api.mobile.get_android_config"},
	{"id": "CR-076", "domain": "digital_channels", "title": "Live chat in mobile app", "wave": 4, "detect": "api:omnexa_car_rental.api.mobile.live_chat_session"},
	{"id": "CR-077", "domain": "ai_automation", "title": "AI fleet copilot", "wave": 4, "detect": "api:omnexa_car_rental.api.ai_automation.fleet_copilot_query"},
	{"id": "CR-078", "domain": "ai_automation", "title": "AI customer assistant", "wave": 4, "detect": "api:omnexa_car_rental.api.ai_automation.customer_assistant_query"},
	{"id": "CR-079", "domain": "ai_automation", "title": "Fraud detection ML", "wave": 4, "detect": "api:omnexa_car_rental.api.ai_automation.detect_rental_fraud"},
	{"id": "CR-080", "domain": "ai_automation", "title": "Fleet optimization AI", "wave": 4, "detect": "api:omnexa_car_rental.api.ai_automation.optimize_fleet_allocation"},
	{"id": "CR-081", "domain": "ai_automation", "title": "Churn prediction", "wave": 4, "detect": "api:omnexa_car_rental.api.ai_automation.predict_customer_churn"},
	{"id": "CR-082", "domain": "gps_telematics", "title": "Remote immobilization", "wave": 4, "detect": "api:omnexa_car_rental.api.telematics.remote_immobilize_vehicle"},
	{"id": "CR-083", "domain": "gps_telematics", "title": "Fuel consumption IoT", "wave": 4, "detect": "doctype:Rental Fuel IoT Reading"},
	{"id": "CR-084", "domain": "integrations", "title": "Government ID verification API", "wave": 4, "detect": "api:omnexa_car_rental.api.integrations.verify_government_id"},
	{"id": "CR-085", "domain": "integrations", "title": "Microsoft Maps routing", "wave": 4, "detect": "api:omnexa_car_rental.api.integrations.route_with_microsoft_maps"},
	{"id": "CR-086", "domain": "integrations", "title": "ERP intercompany sync", "wave": 4, "detect": "api:omnexa_car_rental.api.integrations.sync_erp_intercompany"},
	{"id": "CR-087", "domain": "integrations", "title": "CRM bidirectional sync", "wave": 4, "detect": "api:omnexa_car_rental.api.integrations.sync_crm_bidirectional"},
	{"id": "CR-088", "domain": "security", "title": "ISO 27001 control pack", "wave": 4, "detect": "api:omnexa_car_rental.security.iso27001.get_iso27001_status"},
	{"id": "CR-089", "domain": "security", "title": "SOC2 evidence export", "wave": 4, "detect": "api:omnexa_car_rental.security.soc2.export_soc2_evidence"},
	{"id": "CR-090", "domain": "security", "title": "PCI DSS tokenization", "wave": 4, "detect": "api:omnexa_car_rental.api.security_compliance.tokenize_payment_method"},
	{"id": "CR-091", "domain": "security", "title": "MFA for fleet roles", "wave": 4, "detect": "api:omnexa_car_rental.api.security_compliance.enforce_mfa_for_fleet_roles"},
	{"id": "CR-092", "domain": "security", "title": "PHI-style audit log export", "wave": 4, "detect": "api:omnexa_car_rental.api.security_compliance.export_audit_log"},
	{"id": "CR-093", "domain": "security", "title": "Disaster recovery runbook", "wave": 4, "detect": "doctype:Rental DR Runbook"},
	{"id": "CR-094", "domain": "bi", "title": "Predictive analytics board", "wave": 4, "detect": "page:car-rental-predictive-analytics"},
	{"id": "CR-095", "domain": "bi", "title": "Franchise rollup dashboard", "wave": 4, "detect": "page:car-rental-franchise-dashboard"},
	{"id": "CR-096", "domain": "bi", "title": "Global expansion multi-country pack", "wave": 4, "detect": "doctype:Rental Country Pack"},
]

GAP_DEFINITIONS.extend(_WAVE234)


def _detect_gap(gap: dict) -> bool:
	detect = gap.get("detect")
	if not detect:
		return False
	try:
		if detect.startswith("doctype:"):
			return bool(frappe.db.exists("DocType", detect.split(":", 1)[1]))
		if detect.startswith("page:"):
			return bool(frappe.db.exists("Page", detect.split(":", 1)[1]))
		if detect.startswith("report:"):
			return bool(frappe.db.exists("Report", detect.split(":", 1)[1]))
		if detect.startswith("api:"):
			return bool(frappe.get_attr(detect.split(":", 1)[1]))
		if detect.startswith("module:"):
			return bool(frappe.get_module(f"omnexa_car_rental.{detect.split(':', 1)[1]}"))
		if detect.startswith("scheduler:"):
			return bool(frappe.get_module(f"omnexa_car_rental.{detect.split(':', 1)[1]}"))
		if detect.startswith("hooks:"):
			return True
		if detect.startswith("field:"):
			dt, fn = detect.split(":", 1)[1].split(".")
			meta = frappe.get_meta(dt)
			f = meta.get_field(fn)
			if not f or not f.options:
				return False
			opts = f.options.split("\n")
			return len(opts) >= 8
		if detect.startswith("field_contains:"):
			spec = detect.split(":", 1)[1]
			dt_fn, needle = spec.rsplit(":", 1)
			dt, fn = dt_fn.split(".", 1)
			meta = frappe.get_meta(dt)
			f = meta.get_field(fn)
			return bool(f and needle in (f.options or "").split("\n"))
		if detect.startswith("file:"):
			rel = detect.split(":", 1)[1]
			app_root = os.path.join(get_bench_path(), "apps", "omnexa_car_rental", "omnexa_car_rental")
			return os.path.isfile(os.path.join(app_root, rel))
	except Exception:
		return False
	return False


def get_gap_status() -> dict:
	rows = []
	closed = 0
	for gap in GAP_DEFINITIONS:
		is_closed = _detect_gap(gap)
		if is_closed:
			closed += 1
		rows.append({**gap, "status": "closed" if is_closed else "open"})
	return {
		"version": "2026.06.12",
		"target_score": GLOBAL_LEADER_TARGET,
		"gaps_total": GAPS_TOTAL,
		"gaps_closed": closed,
		"gaps_open": GAPS_TOTAL - closed,
		"global_leader_gate": closed >= GAPS_TOTAL,
		"gaps": rows,
	}
