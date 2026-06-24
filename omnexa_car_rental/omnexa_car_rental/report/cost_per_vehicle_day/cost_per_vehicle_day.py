import frappe

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt


def execute(filters=None):
	columns = [
		{"label": "Vehicle", "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 160},
		{"label": "Cost/Day", "fieldname": "cost_per_day", "fieldtype": "Currency", "width": 120},
		{"label": "Cost/KM", "fieldname": "cost_per_km", "fieldtype": "Currency", "width": 120},
	]
	data = []
	for v in frappe.get_all("Vehicle", fields=["name", "plate_number"], limit=200):
		maint = frappe.db.sql("SELECT COALESCE(SUM(cost_amount),0) FROM `tabVehicle Maintenance Record` WHERE vehicle=%s", v.name)[0][0]
		data.append({"vehicle": v.name, "cost_per_day": flt(maint) / 30.0, "cost_per_km": flt(maint) / 1000.0})
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart