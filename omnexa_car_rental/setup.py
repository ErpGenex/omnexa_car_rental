from __future__ import annotations

import frappe


def ensure_car_rental_kpi_cards():
	card_defs = [
		("Utilization %", "omnexa_car_rental.api.kpi_utilization_percent"),
		("Active Rentals", "omnexa_car_rental.api.kpi_active_rentals"),
		("Revenue Today", "omnexa_car_rental.api.kpi_revenue_today"),
		("Maintenance Cost MTD", "omnexa_car_rental.api.kpi_maintenance_cost_mtd"),
	]

	card_names: list[str] = []
	for label, method in card_defs:
		card_name = frappe.db.get_value("Number Card", {"label": label, "method": method}, "name")
		if not card_name:
			card = frappe.new_doc("Number Card")
			card.label = label
			card.type = "Custom"
			card.method = method
			card.module = "Omnexa Car Rental"
			card.is_public = 1
			card.show_percentage_stats = 0
			card.insert(ignore_permissions=True)
			card_name = card.name
		card_names.append(card_name)

	workspace = frappe.get_doc("Workspace", "Car Rental")
	workspace.number_cards = []
	for name in card_names:
		workspace.append("number_cards", {"number_card_name": name})
	workspace.save(ignore_permissions=True)
	frappe.db.commit()
	return {"workspace": workspace.name, "number_cards": card_names}

