# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _


def get_vehicle_dashboard_data(data=None):
	data = frappe._dict(data or {})
	data.setdefault("transactions", [])
	data["transactions"].append(
		{
			"label": _("Car Rental"),
			"items": ["Rental Contract", "Rental Booking"],
		}
	)
	data["transactions"].append(
		{
			"label": _("Operations"),
			"items": [
				"Vehicle Maintenance Record",
				"Vehicle Fuel Log",
				"Vehicle Damage Report",
				"Vehicle Insurance Policy",
			],
		}
	)
	data["transactions"].append(
		{
			"label": _("Toll & Highways"),
			"items": ["Toll Transaction"],
		}
	)
	return data
