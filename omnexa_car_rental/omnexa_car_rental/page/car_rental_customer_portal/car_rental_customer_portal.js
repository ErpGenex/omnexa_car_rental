frappe.pages["car-rental-customer-portal"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Car Rental Customer Portal"), single_column: true });
	$(page.body).html(`<div class="p-4"><h5>Car Rental Customer Portal</h5><p class="text-muted">${__("Self-service booking, payments, extensions")}</p></div>`);
};
