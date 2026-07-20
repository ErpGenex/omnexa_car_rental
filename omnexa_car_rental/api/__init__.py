# Re-export desk APIs so omnexa_car_rental.api.* paths resolve (package shadows api.py).
from omnexa_car_rental.api.desk import (  # noqa: F401
	create_rental_contract_from_booking,
	kpi_active_rentals,
	kpi_maintenance_cost_mtd,
	kpi_revenue_today,
	kpi_utilization_percent,
	preview_sector_kpi,
	toll_apply_fx,
	toll_create_customer_invoice,
	toll_create_journal_entry,
	toll_ingest_batch_file,
	toll_run_matching,
	toll_run_monthly_consolidation,
	toll_run_previous_month_consolidation,
)

import frappe


@frappe.whitelist(allow_guest=True)
def get_site_config() -> dict:
	"""Public car rental website configuration."""
	return {
		"brand_name_ar": "Omnexa Car Rental",
		"brand_name_en": "Omnexa Car Rental",
		"tagline_ar": "تأجير سيارات مرن وموثوق لرحلاتك",
		"tagline_en": "Flexible, reliable car rental for your journeys",
		"hero_text_ar": "من السيارات الاقتصادية إلى الفاخرة — أسطول متنوع لكل احتياجاتك",
		"hero_text_en": "From economy to luxury — a diverse fleet for all your needs",
		"hero_image": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&w=1920&q=85",
		"logo": "/assets/omnexa_car_rental/logo.png",
		"primary_color": "#2196f3",
		"secondary_color": "#ff5722",
		"accent_color": "#00bcd4",
		"gold_color": "#ffc107",
		"fleet": [
			{"key": "economy", "name_ar": "اقتصادية", "name_en": "Economy", "icon": "🚗", "price": "from $25/day"},
			{"key": "sedan", "name_ar": "سيدان", "name_en": "Sedan", "icon": "🚙", "price": "from $35/day"},
			{"key": "suv", "name_ar": "دفع رباعي", "name_en": "SUV", "icon": "🚙", "price": "from $50/day"},
			{"key": "luxury", "name_ar": "فاخرة", "name_en": "Luxury", "icon": "🏎️", "price": "from $80/day"},
		],
		"services": [
			{"icon": "🔑", "ar": "تأجير مرن", "en": "Flexible Rental"},
			{"icon": "📱", "ar": "حجز أونلاين", "en": "Online Booking"},
			{"icon": "🛡️", "ar": "تأمين شامل", "en": "Full Insurance"},
			{"icon": "🚗", "ar": "توصيل للمنزل", "en": "Home Delivery"},
			{"icon": "🔧", "ar": "صيانة مجانية", "en": "Free Maintenance"},
			{"icon": "📍", "ar": "خدمة 24/7", "en": "24/7 Support"},
		],
		"stats": {"cars": 200, "customers": 5000, "locations": 10, "years": 8},
	}
