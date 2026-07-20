# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""AI pricing, forecasting, copilots, fraud, optimization, churn."""

from __future__ import annotations

import frappe
from frappe.utils import flt


@frappe.whitelist()
def compute_dynamic_price(company: str, branch: str, vehicle_group: str | None = None, rental_type: str = "Daily") -> dict:
	from omnexa_car_rental.api.web_booking import quote_rental_rate

	base = quote_rental_rate(company, branch, vehicle_group, rental_type)
	demand_factor = 1.0 + (frappe.db.count("Rental Booking", {"company": company, "branch": branch
	}) % 10) * 0.02
	price = flt(base.get("amount")) * demand_factor
	return {"base": base.get("amount"), "dynamic_price": round(price, 2), "demand_factor": demand_factor
	}


@frappe.whitelist()
def forecast_demand(company: str, branch: str, days: int = 30) -> dict:
	bookings = frappe.db.count("Rental Booking", {"company": company, "branch": branch
	})
	return {"company": company, "branch": branch, "horizon_days": days, "forecast_bookings": bookings + days // 3
	}


@frappe.whitelist()
def fleet_copilot_query(query: str) -> dict:
	return {"query": query, "answer": f"Fleet insight: {frappe.db.count('Vehicle')
	} vehicles in fleet.", "agent": "fleet"
	}


@frappe.whitelist(allow_guest=True)
def customer_assistant_query(query: str) -> dict:
	return {"query": query, "answer": "I can help you book, extend, or return a rental.", "agent": "customer"
	}


@frappe.whitelist()
def operations_assistant_query(query: str) -> dict:
	return {"query": query, "answer": f"Active rentals: {frappe.db.count('Rental Contract', {'status': 'Active Rental'})}", "agent": "operations"
	}


@frappe.whitelist()
def management_assistant_query(query: str) -> dict:
	return {"query": query, "answer": "Executive summary available on car-rental-executive-dashboard.", "agent": "management"
	}


@frappe.whitelist()
def detect_rental_fraud(customer_profile: str, amount: float) -> dict:
	risk = frappe.db.count("Rental Customer Blacklist", {"customer_profile": customer_profile, "status": "Active"
	})
	return {"fraud_risk": "High" if risk else "Low", "blocked": bool(risk), "amount": flt(amount)
	}


@frappe.whitelist()
def optimize_fleet_allocation(company: str, branch: str) -> dict:
	available = frappe.db.count("Vehicle", {"company": company, "branch": branch, "status": "Available"
	})
	rented = frappe.db.count("Vehicle", {"company": company, "branch": branch, "status": "Rented"
	})
	return {"available": available, "rented": rented, "recommendation": "Maintain current mix" if available else "Acquire vehicles"
	}


@frappe.whitelist()
def predict_customer_churn(customer_profile: str) -> dict:
	bookings = frappe.db.count("Rental Booking", {"customer_profile": customer_profile
	})
	return {"customer_profile": customer_profile, "churn_probability": max(0.05, 0.5 - bookings * 0.1), "bookings": bookings
	}
