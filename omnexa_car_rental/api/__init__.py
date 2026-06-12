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
