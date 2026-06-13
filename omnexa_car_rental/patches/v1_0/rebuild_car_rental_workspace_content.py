# Copyright (c) 2026, Omnexa

import frappe


def execute() -> None:
	if not frappe.db.exists("Workspace", "Car Rental"):
		return
	from omnexa_car_rental.workspace.car_rental_workspace import sync_car_rental_workspace_menu

	sync_car_rental_workspace_menu(save=True, rebuild=True)
