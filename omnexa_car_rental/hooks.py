app_name = "omnexa_car_rental"
app_title = "ErpGenEx Car Rental"
app_publisher = "ErpGenEx"
app_description = "Global Car Rental and Fleet Management"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_accounting", "omnexa_fixed_assets", "omnexa_customer_core", "omnexa_services"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "omnexa_car_rental",
		"logo": "/assets/omnexa_car_rental/logo.png",
		"title": "Car Rental",
		"route": "/app/car-rental"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_car_rental/css/omnexa_car_rental.css"
# app_include_js = "/assets/omnexa_car_rental/js/omnexa_car_rental.js"

# include js, css files in header of web template
web_include_css = "/assets/omnexa_car_rental/css/car_rental_website.css"
web_include_js = "/assets/omnexa_car_rental/js/car_rental_website.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_car_rental/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_car_rental/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_car_rental.utils.jinja_methods",
# 	"filters": "omnexa_car_rental.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "omnexa_car_rental.install.enforce_supported_frappe_version"
before_migrate = "omnexa_car_rental.install.enforce_supported_frappe_version"
after_install = "omnexa_car_rental.install.after_install"
after_migrate = "omnexa_car_rental.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "omnexa_car_rental.uninstall.before_uninstall"
# after_uninstall = "omnexa_car_rental.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_car_rental.utils.before_app_install"
# after_app_install = "omnexa_car_rental.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_car_rental.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_car_rental.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_car_rental.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Toll Provider": "omnexa_car_rental.permissions.toll_provider_query_conditions",
	"Vehicle": "omnexa_car_rental.permissions.vehicle_query_conditions",
	"Rental Booking": "omnexa_car_rental.permissions.rental_booking_query_conditions",
	"Rental Contract": "omnexa_car_rental.permissions.rental_contract_query_conditions",
	"Rental Driver": "omnexa_car_rental.permissions.rental_driver_query_conditions",
	"Supplier Fleet Contract": "omnexa_car_rental.permissions.supplier_fleet_contract_query_conditions",
	"Vehicle Maintenance Record": "omnexa_car_rental.permissions.vehicle_maintenance_record_query_conditions",
	"Vehicle Fuel Log": "omnexa_car_rental.permissions.vehicle_fuel_log_query_conditions",
	"Vehicle Damage Report": "omnexa_car_rental.permissions.vehicle_damage_report_query_conditions",
	"Vehicle Insurance Policy": "omnexa_car_rental.permissions.vehicle_insurance_policy_query_conditions",
	"Toll Transaction": "omnexa_car_rental.permissions.toll_transaction_query_conditions",
	"Toll Allocation Rule": "omnexa_car_rental.permissions.toll_allocation_rule_query_conditions",
	"Toll Invoice Line": "omnexa_car_rental.permissions.toll_invoice_line_query_conditions",
	"Rental Rate Plan": "omnexa_car_rental.permissions.rental_rate_plan_query_conditions",
	"Rental Station": "omnexa_car_rental.permissions.rental_station_query_conditions",
	"Rental Vehicle Inspection": "omnexa_car_rental.permissions.rental_vehicle_inspection_query_conditions",
	"Maintenance Work Order": "omnexa_car_rental.permissions.maintenance_work_order_query_conditions"
	}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

override_doctype_dashboards = {
	"Vehicle": "omnexa_car_rental.omnexa_car_rental.dashboard.vehicle_dashboard.get_vehicle_dashboard_data"
	}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Vehicle": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Rental Booking": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Rental Contract": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Rental Driver": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Supplier Fleet Contract": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Vehicle Maintenance Record": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Vehicle Fuel Log": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Vehicle Damage Report": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Vehicle Insurance Policy": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Toll Transaction": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Toll Allocation Rule": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Toll Invoice Line": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Rental Rate Plan": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Rental Station": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Rental Vehicle Inspection": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"
	},
	"Maintenance Work Order": {
		"before_validate": "omnexa_car_rental.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_car_rental.permissions.enforce_branch_access_for_doc"}
	}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		"*/15 * * * *": [
			"omnexa_car_rental.toll_tasks.poll_toll_providers",
			"omnexa_car_rental.toll_tasks.process_unmatched_toll_queue",
		],
		"5 4 1 * *": [
			"omnexa_car_rental.toll_tasks.run_scheduled_monthly_toll_billing",
		]},
	"daily": [
		"omnexa_car_rental.fleet_reminders.run_daily",
		"omnexa_car_rental.policy_renewal_tasks.run_policy_renewal_reminders",
	]}

# Testing
# -------

# before_tests = "omnexa_car_rental.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_car_rental.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_car_rental.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["omnexa_car_rental.utils.before_request"]
# after_request = ["omnexa_car_rental.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_car_rental.utils.before_job"]
# after_job = ["omnexa_car_rental.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{}",
# 		"filter_by": "{}",
# 		"redact_fields": ["{}", "{}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{}",
# 		"filter_by": "{}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_car_rental.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

