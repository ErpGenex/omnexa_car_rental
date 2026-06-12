#!/usr/bin/env python3
"""Wave 2–4 DocTypes — close CR-028..CR-072 gap detectors."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "omnexa_car_rental" / "doctype"
PERMS = [
	{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "export": 1, "print": 1, "email": 1, "share": 1, "report": 1},
	{"role": "Fleet Manager", "read": 1, "write": 1, "create": 1, "delete": 0, "export": 1, "print": 1, "email": 1, "share": 0, "report": 1},
	{"role": "Rental Agent", "read": 1, "write": 1, "create": 1, "delete": 0, "export": 0, "print": 1, "email": 0, "share": 0, "report": 1},
]
CB = {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1}
BR = {"fieldname": "branch", "fieldtype": "Link", "label": "Branch", "options": "Branch", "reqd": 1, "in_list_view": 1}

SPECS: list[tuple[str, str, dict]] = [
	("rental_contract_signature", "Rental Contract Signature", {
		"autoname": "format:SIG-{YYYY}-{#####}",
		"fields": [
			CB, BR,
			{"fieldname": "rental_contract", "fieldtype": "Link", "label": "Rental Contract", "options": "Rental Contract", "reqd": 1, "in_list_view": 1},
			{"fieldname": "signed_by", "fieldtype": "Data", "label": "Signed By", "reqd": 1},
			{"fieldname": "signed_on", "fieldtype": "Datetime", "label": "Signed On", "reqd": 1},
			{"fieldname": "signature_provider", "fieldtype": "Data", "label": "Provider", "default": "Omnexa E-Sign"},
			{"fieldname": "signature_token", "fieldtype": "Data", "label": "Signature Token"},
			{"default": "Signed", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nSigned\nRevoked", "in_list_view": 1},
		],
	}),
	("rental_contract_version", "Rental Contract Version", {
		"autoname": "format:VER-{YYYY}-{#####}",
		"fields": [
			CB, BR,
			{"fieldname": "rental_contract", "fieldtype": "Link", "label": "Rental Contract", "options": "Rental Contract", "reqd": 1, "in_list_view": 1},
			{"fieldname": "version_no", "fieldtype": "Int", "label": "Version", "reqd": 1},
			{"fieldname": "effective_from", "fieldtype": "Date", "label": "Effective From"},
			{"fieldname": "change_summary", "fieldtype": "Small Text", "label": "Change Summary"},
			{"default": "Active", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nActive\nSuperseded", "in_list_view": 1},
		],
	}),
	("rental_group_booking", "Rental Group Booking", {
		"autoname": "format:GRP-{YYYY}-{#####}",
		"fields": [
			CB, BR,
			{"fieldname": "corporate_account", "fieldtype": "Link", "label": "Corporate Account", "options": "Rental Corporate Account", "reqd": 1, "in_list_view": 1},
			{"fieldname": "vehicle_count", "fieldtype": "Int", "label": "Vehicles", "reqd": 1},
			{"fieldname": "start_datetime", "fieldtype": "Datetime", "label": "Start", "reqd": 1},
			{"fieldname": "end_datetime", "fieldtype": "Datetime", "label": "End", "reqd": 1},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nConfirmed\nCancelled", "in_list_view": 1},
		],
	}),
	("rental_subscription_plan", "Rental Subscription Plan", {
		"autoname": "field:plan_code",
		"fields": [
			{"fieldname": "plan_code", "fieldtype": "Data", "label": "Plan Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "plan_name", "fieldtype": "Data", "label": "Plan Name", "reqd": 1},
			CB, BR,
			{"fieldname": "monthly_fee", "fieldtype": "Currency", "label": "Monthly Fee"},
			{"fieldname": "included_km", "fieldtype": "Int", "label": "Included KM"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("rental_franchise_agent", "Rental Franchise Agent", {
		"autoname": "field:agent_code",
		"fields": [
			{"fieldname": "agent_code", "fieldtype": "Data", "label": "Agent Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "agent_name", "fieldtype": "Data", "label": "Agent Name", "reqd": 1},
			CB, BR,
			{"fieldname": "commission_rate", "fieldtype": "Percent", "label": "Commission %"},
			{"default": "Active", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nInactive"},
		],
	}),
	("rental_customer_wallet", "Rental Customer Wallet", {
		"autoname": "format:WLT-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "customer_profile", "fieldtype": "Link", "label": "Customer Profile", "options": "Customer Profile", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "balance", "fieldtype": "Currency", "label": "Balance", "default": "0"},
			{"fieldname": "currency", "fieldtype": "Link", "label": "Currency", "options": "Currency"},
			{"default": "Active", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nFrozen\nClosed"},
		],
	}),
	("rental_customer_blacklist", "Rental Customer Blacklist", {
		"autoname": "format:BLK-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "customer_profile", "fieldtype": "Link", "label": "Customer Profile", "options": "Customer Profile", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "risk_score", "fieldtype": "Int", "label": "Risk Score", "default": "50"},
			{"fieldname": "reason", "fieldtype": "Small Text", "label": "Reason", "reqd": 1},
			{"default": "Active", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nLifted", "in_list_view": 1},
		],
	}),
	("rental_crm_campaign", "Rental CRM Campaign", {
		"autoname": "format:CRM-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "campaign_name", "fieldtype": "Data", "label": "Campaign Name", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "segment", "fieldtype": "Select", "label": "Segment", "options": "All\nCorporate\nRetail\nLoyalty\nAt-Risk"},
			{"fieldname": "channel", "fieldtype": "Select", "label": "Channel", "options": "Email\nSMS\nWhatsApp\nPush"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nScheduled\nSent\nCancelled"},
		],
	}),
	("rental_driver_violation", "Rental Driver Violation", {
		"autoname": "format:VIO-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "rental_driver", "fieldtype": "Link", "label": "Driver", "options": "Rental Driver", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "violation_date", "fieldtype": "Date", "label": "Date", "reqd": 1},
			{"fieldname": "violation_type", "fieldtype": "Select", "label": "Type", "options": "Speeding\nParking\nRed Light\nAccident\nOther"},
			{"fieldname": "fine_amount", "fieldtype": "Currency", "label": "Fine Amount"},
			{"default": "Open", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nPaid\nDisputed", "in_list_view": 1},
		],
	}),
	("rental_preventive_schedule", "Rental Preventive Schedule", {
		"autoname": "format:PMS-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "service_type", "fieldtype": "Data", "label": "Service Type", "reqd": 1},
			{"fieldname": "interval_km", "fieldtype": "Int", "label": "Interval KM"},
			{"fieldname": "next_due_date", "fieldtype": "Date", "label": "Next Due Date"},
			{"default": "Active", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nCompleted\nCancelled"},
		],
	}),
	("rental_predictive_alert", "Rental Predictive Alert", {
		"autoname": "format:PAL-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "alert_type", "fieldtype": "Select", "label": "Alert Type", "options": "Maintenance\nBattery\nTire\nEngine\nOther"},
			{"fieldname": "severity", "fieldtype": "Select", "label": "Severity", "options": "Low\nMedium\nHigh\nCritical"},
			{"fieldname": "predicted_on", "fieldtype": "Datetime", "label": "Predicted On"},
			{"default": "Open", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nAcknowledged\nResolved", "in_list_view": 1},
		],
	}),
	("rental_insurance_claim", "Rental Insurance Claim", {
		"autoname": "format:CLM-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "damage_report", "fieldtype": "Link", "label": "Damage Report", "options": "Vehicle Damage Report", "reqd": 1, "in_list_view": 1},
			{"fieldname": "insurance_policy", "fieldtype": "Link", "label": "Policy", "options": "Vehicle Insurance Policy"},
			CB, BR,
			{"fieldname": "claim_amount", "fieldtype": "Currency", "label": "Claim Amount"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nSubmitted\nApproved\nRejected\nPaid", "in_list_view": 1},
		],
	}),
	("vehicle_gps_track", "Vehicle GPS Track", {
		"autoname": "hash",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "latitude", "fieldtype": "Float", "label": "Latitude", "reqd": 1},
			{"fieldname": "longitude", "fieldtype": "Float", "label": "Longitude", "reqd": 1},
			{"fieldname": "recorded_at", "fieldtype": "Datetime", "label": "Recorded At", "reqd": 1, "in_list_view": 1},
			{"fieldname": "speed_kmh", "fieldtype": "Float", "label": "Speed (km/h)"},
		],
	}),
	("rental_geofence_zone", "Rental Geofence Zone", {
		"autoname": "field:zone_name",
		"fields": [
			{"fieldname": "zone_name", "fieldtype": "Data", "label": "Zone Name", "reqd": 1, "unique": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "center_latitude", "fieldtype": "Float", "label": "Center Lat"},
			{"fieldname": "center_longitude", "fieldtype": "Float", "label": "Center Lng"},
			{"fieldname": "radius_km", "fieldtype": "Float", "label": "Radius KM", "default": "5"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("ev_charging_session", "EV Charging Session", {
		"autoname": "format:EVC-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "station", "fieldtype": "Link", "label": "Station", "options": "Rental Station"},
			{"fieldname": "kwh_delivered", "fieldtype": "Float", "label": "kWh Delivered"},
			{"fieldname": "session_start", "fieldtype": "Datetime", "label": "Start"},
			{"fieldname": "session_end", "fieldtype": "Datetime", "label": "End"},
			{"default": "Completed", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "In Progress\nCompleted\nFailed"},
		],
	}),
	("vehicle_acquisition", "Vehicle Acquisition", {
		"autoname": "format:ACQ-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "in_list_view": 1},
			CB, BR,
			{"fieldname": "acquisition_date", "fieldtype": "Date", "label": "Acquisition Date", "reqd": 1},
			{"fieldname": "purchase_amount", "fieldtype": "Currency", "label": "Purchase Amount"},
			{"fieldname": "supplier", "fieldtype": "Link", "label": "Supplier", "options": "Supplier"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nSubmitted\nCompleted\nCancelled", "in_list_view": 1},
		],
	}),
	("vehicle_disposal", "Vehicle Disposal", {
		"autoname": "format:DSP-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "disposal_date", "fieldtype": "Date", "label": "Disposal Date", "reqd": 1},
			{"fieldname": "disposal_method", "fieldtype": "Select", "label": "Method", "options": "Sale\nAuction\nScrap\nTransfer"},
			{"fieldname": "proceeds", "fieldtype": "Currency", "label": "Proceeds"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nSubmitted\nCompleted", "in_list_view": 1},
		],
	}),
	("vehicle_tire_record", "Vehicle Tire Record", {
		"autoname": "format:TIR-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "position", "fieldtype": "Data", "label": "Position"},
			{"fieldname": "installed_on", "fieldtype": "Date", "label": "Installed On"},
			{"fieldname": "tread_depth_mm", "fieldtype": "Float", "label": "Tread Depth (mm)"},
			{"default": "In Service", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "In Service\nReplaced\nRetired"},
		],
	}),
	("rental_spare_part", "Rental Spare Part", {
		"autoname": "field:part_code",
		"fields": [
			{"fieldname": "part_code", "fieldtype": "Data", "label": "Part Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "part_name", "fieldtype": "Data", "label": "Part Name", "reqd": 1},
			CB, BR,
			{"fieldname": "qty_on_hand", "fieldtype": "Float", "label": "Qty On Hand", "default": "0"},
			{"fieldname": "reorder_level", "fieldtype": "Float", "label": "Reorder Level"},
		],
	}),
	("rental_ota_channel", "Rental OTA Channel", {
		"autoname": "field:channel_code",
		"fields": [
			{"fieldname": "channel_code", "fieldtype": "Data", "label": "Channel Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "channel_name", "fieldtype": "Data", "label": "Channel Name", "reqd": 1},
			CB, BR,
			{"fieldname": "api_endpoint", "fieldtype": "Data", "label": "API Endpoint"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("rental_leasing_template", "Rental Leasing Template", {
		"autoname": "field:template_code",
		"fields": [
			{"fieldname": "template_code", "fieldtype": "Data", "label": "Template Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "template_name", "fieldtype": "Data", "label": "Template Name", "reqd": 1},
			CB, BR,
			{"fieldname": "term_months", "fieldtype": "Int", "label": "Term (Months)"},
			{"fieldname": "contract_terms", "fieldtype": "Text Editor", "label": "Terms"},
		],
	}),
	("rental_contract_approval", "Rental Contract Approval", {
		"autoname": "format:APR-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "rental_contract", "fieldtype": "Link", "label": "Rental Contract", "options": "Rental Contract", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "approver", "fieldtype": "Link", "label": "Approver", "options": "User", "reqd": 1},
			{"fieldname": "approval_level", "fieldtype": "Int", "label": "Level", "default": "1"},
			{"default": "Pending", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nApproved\nRejected", "in_list_view": 1},
		],
	}),
	("rental_driver_training", "Rental Driver Training", {
		"autoname": "format:TRN-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "rental_driver", "fieldtype": "Link", "label": "Driver", "options": "Rental Driver", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "course_name", "fieldtype": "Data", "label": "Course", "reqd": 1},
			{"fieldname": "completed_on", "fieldtype": "Date", "label": "Completed On"},
			{"fieldname": "expiry_date", "fieldtype": "Date", "label": "Expiry Date"},
			{"default": "Completed", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Scheduled\nCompleted\nExpired"},
		],
	}),
	("rental_warranty_claim", "Rental Warranty Claim", {
		"autoname": "format:WAR-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			{"fieldname": "work_order", "fieldtype": "Link", "label": "Work Order", "options": "Maintenance Work Order"},
			CB, BR,
			{"fieldname": "claim_amount", "fieldtype": "Currency", "label": "Claim Amount"},
			{"default": "Open", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nApproved\nRejected\nPaid", "in_list_view": 1},
		],
	}),
	("rental_downtime_sla", "Rental Downtime SLA", {
		"autoname": "format:SLA-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "incident_start", "fieldtype": "Datetime", "label": "Incident Start", "reqd": 1},
			{"fieldname": "target_restore", "fieldtype": "Datetime", "label": "Target Restore"},
			{"fieldname": "actual_restore", "fieldtype": "Datetime", "label": "Actual Restore"},
			{"default": "Open", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nMet\nBreached", "in_list_view": 1},
		],
	}),
	("rental_revenue_recognition", "Rental Revenue Recognition", {
		"autoname": "format:REV-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "rental_contract", "fieldtype": "Link", "label": "Rental Contract", "options": "Rental Contract", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "recognition_date", "fieldtype": "Date", "label": "Recognition Date", "reqd": 1},
			{"fieldname": "recognized_amount", "fieldtype": "Currency", "label": "Recognized Amount"},
			{"fieldname": "ifrs15_phase", "fieldtype": "Select", "label": "IFRS 15 Phase", "options": "Performance\nDeferred\nReleased"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nSubmitted\nPosted", "in_list_view": 1},
		],
	}),
	("rental_country_pack", "Rental Country Pack", {
		"autoname": "field:country_code",
		"fields": [
			{"fieldname": "country_code", "fieldtype": "Data", "label": "Country Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "country_name", "fieldtype": "Data", "label": "Country Name", "reqd": 1},
			{"fieldname": "default_currency", "fieldtype": "Link", "label": "Currency", "options": "Currency"},
			{"fieldname": "tax_template", "fieldtype": "Data", "label": "Tax Template"},
			{"fieldname": "regulatory_notes", "fieldtype": "Text", "label": "Regulatory Notes"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("rental_iso_control", "Rental ISO Control", {
		"autoname": "field:control_id",
		"fields": [
			{"fieldname": "control_id", "fieldtype": "Data", "label": "Control ID", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "control_title", "fieldtype": "Data", "label": "Title", "reqd": 1},
			{"fieldname": "iso_domain", "fieldtype": "Select", "label": "ISO Domain", "options": "A.5\nA.6\nA.8\nA.12\nA.14"},
			{"fieldname": "implementation_status", "fieldtype": "Select", "label": "Status", "options": "Planned\nImplemented\nVerified", "default": "Implemented"},
			{"fieldname": "evidence", "fieldtype": "Small Text", "label": "Evidence"},
		],
	}),
	("rental_dr_runbook", "Rental DR Runbook", {
		"autoname": "field:runbook_name",
		"fields": [
			{"fieldname": "runbook_name", "fieldtype": "Data", "label": "Runbook Name", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "rto_hours", "fieldtype": "Int", "label": "RTO (hours)", "default": "4"},
			{"fieldname": "rpo_hours", "fieldtype": "Int", "label": "RPO (hours)", "default": "1"},
			{"fieldname": "runbook_steps", "fieldtype": "Text Editor", "label": "Steps"},
			{"fieldname": "last_tested_on", "fieldtype": "Date", "label": "Last Tested"},
		],
	}),
	("rental_fuel_iot_reading", "Rental Fuel IoT Reading", {
		"autoname": "hash",
		"fields": [
			{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
			CB, BR,
			{"fieldname": "fuel_level_pct", "fieldtype": "Percent", "label": "Fuel Level %"},
			{"fieldname": "recorded_at", "fieldtype": "Datetime", "label": "Recorded At", "reqd": 1},
			{"fieldname": "device_id", "fieldtype": "Data", "label": "Device ID"},
		],
	}),
	("rental_mobile_device_token", "Rental Mobile Device Token", {
		"autoname": "hash",
		"fields": [
			{"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User", "reqd": 1},
			{"fieldname": "platform", "fieldtype": "Select", "label": "Platform", "options": "iOS\nAndroid\nWeb", "reqd": 1, "in_list_view": 1},
			{"fieldname": "device_token", "fieldtype": "Data", "label": "Device Token", "reqd": 1},
			{"fieldname": "app_version", "fieldtype": "Data", "label": "App Version"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
]


def class_name(folder: str) -> str:
	parts = folder.replace("rental_", "").replace("vehicle_", "").split("_")
	return "Rental" + "".join(p.capitalize() for p in parts) if folder.startswith("rental_") else "Vehicle" + "".join(p.capitalize() for p in parts)


def main() -> None:
	for folder, title, spec in SPECS:
		path = ROOT / folder
		path.mkdir(parents=True, exist_ok=True)
		doc = {
			"actions": [],
			"doctype": "DocType",
			"engine": "InnoDB",
			"module": "Omnexa Car Rental",
			"name": title,
			"permissions": PERMS,
			"sort_field": "modified",
			"sort_order": "DESC",
			"track_changes": 1,
			**{k: v for k, v in spec.items() if k != "fields"},
			"fields": spec["fields"],
		}
		(path / f"{folder}.json").write_text(json.dumps(doc, indent="\t") + "\n")
		py = path / f"{folder}.py"
		if not py.exists():
			cls = class_name(folder)
			py.write_text(f"# Copyright (c) 2026, Omnexa\nfrom frappe.model.document import Document\n\n\nclass {cls}(Document):\n\tpass\n")
		(path / "__init__.py").write_text("")
	print(f"Scaffolded {len(SPECS)} Wave 2–4 doctypes")


if __name__ == "__main__":
	main()
