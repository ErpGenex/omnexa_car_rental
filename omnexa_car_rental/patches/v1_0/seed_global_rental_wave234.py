# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe


def execute():
	from omnexa_car_rental.security.iso27001 import ensure_iso_controls
	from omnexa_car_rental.workspace.car_rental_workspace import sync_car_rental_workspace_menu

	ensure_iso_controls()
	seeds = [
		("Rental DR Runbook", {"runbook_name": "Car Rental DR Standard", "rto_hours": 4, "rpo_hours": 1
	}),
		("Rental Country Pack", {"country_code": "SA", "country_name": "Saudi Arabia", "is_active": 1
	}),
		("Rental Subscription Plan", {"plan_code": "SUB-MONTHLY", "plan_name": "Monthly Subscription", "is_active": 1
	}),
		("Rental Franchise Agent", {"agent_code": "FRAN-001", "agent_name": "Default Franchise Agent", "status": "Active"
	}),
	]
	company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.get_all("Company", limit=1)[0].name
	branch = frappe.db.get_value("Branch", {"company": company
	}, "name")
	for doctype, data in seeds:
		key_field = "runbook_name" if doctype == "Rental DR Runbook" else (
			"country_code" if doctype == "Rental Country Pack" else (
				"plan_code" if doctype == "Rental Subscription Plan" else "agent_code"
			)
		)
		if frappe.db.exists(doctype, data[key_field]):
			continue
		payload = {"doctype": doctype, **data}
		if doctype in ("Rental Subscription Plan", "Rental Franchise Agent"):
			payload.update({"company": company, "branch": branch
	})
		frappe.get_doc(payload).insert(ignore_permissions=True)
	sync_car_rental_workspace_menu(save=True, rebuild=True)
