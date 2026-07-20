frappe.pages["car-rental-franchise-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Franchise Rollup Dashboard"), single_column: true });
	$(page.body).html(`<div class="p-4"><h5>Franchise Rollup Dashboard</h5><p class="text-muted">${__("Multi-branch franchise KPIs")}</p></div>`);
};
