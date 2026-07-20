# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""GPS, geofencing, telematics, EV, immobilization, fuel IoT."""

from __future__ import annotations

import frappe
from frappe.utils import flt, now_datetime


@frappe.whitelist()
def record_gps_position(vehicle: str, latitude: float, longitude: float, speed_kmh: float = 0) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Vehicle GPS Track",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"latitude": flt(latitude),
			"longitude": flt(longitude),
			"speed_kmh": flt(speed_kmh),
			"recorded_at": now_datetime()
	}
	)
	doc.insert(ignore_permissions=True)
	return {"track": doc.name
	}


@frappe.whitelist()
def check_geofence(vehicle: str, latitude: float, longitude: float) -> dict:
	zones = frappe.get_all("Rental Geofence Zone", filters={"is_active": 1
	}, fields=["name", "center_latitude", "center_longitude", "radius_km"])
	inside = []
	for z in zones:
		if z.center_latitude and z.center_longitude:
			dist = abs(flt(latitude) - flt(z.center_latitude)) + abs(flt(longitude) - flt(z.center_longitude))
			if dist <= flt(z.radius_km or 5) / 100.0:
				inside.append(z.name)
	return {"vehicle": vehicle, "zones": inside, "alert": bool(inside)
	}


@frappe.whitelist()
def analyze_driver_behavior(rental_driver: str) -> dict:
	tracks = frappe.db.count("Vehicle GPS Track", {"vehicle": ["in", frappe.get_all("Rental Contract", filters={"driver": rental_driver
	}, pluck="vehicle") or ["NONE"]]})
	return {"rental_driver": rental_driver, "samples": tracks, "score": max(60, 100 - tracks // 10)}


@frappe.whitelist()
def record_ev_charging_session(vehicle: str, kwh_delivered: float, station: str | None = None) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "EV Charging Session",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"station": station,
			"kwh_delivered": flt(kwh_delivered),
			"session_start": now_datetime(),
			"status": "Completed"
	}
	)
	doc.insert()
	return {"session": doc.name
	}


@frappe.whitelist()
def remote_immobilize_vehicle(vehicle: str, enable: int = 1) -> dict:
	frappe.get_doc("Vehicle", vehicle)
	return {"vehicle": vehicle, "immobilized": bool(int(enable)), "command_id": frappe.generate_hash(length=8)
	}


@frappe.whitelist()
def ingest_fuel_iot_reading(vehicle: str, fuel_level_pct: float, device_id: str) -> dict:
	v = frappe.get_doc("Vehicle", vehicle)
	doc = frappe.get_doc(
		{
			"doctype": "Rental Fuel IoT Reading",
			"vehicle": vehicle,
			"company": v.company,
			"branch": v.branch,
			"fuel_level_pct": flt(fuel_level_pct),
			"device_id": device_id,
			"recorded_at": now_datetime()
	}
	)
	doc.insert()
	return {"reading": doc.name
	}
