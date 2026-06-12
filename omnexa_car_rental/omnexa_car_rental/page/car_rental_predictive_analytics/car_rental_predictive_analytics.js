frappe.pages["car-rental-predictive-analytics"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Predictive Analytics Board"), single_column: true });
	$(page.body).html(`<div class="p-4"><h5>Predictive Analytics Board</h5><p class="text-muted">${__("Demand, maintenance, churn analytics")}</p></div>`);
};
