frappe.pages["car-rental-workshop-vendor-portal"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Workshop Vendor Portal"), single_column: true });
	$(page.body).html(`<div class="p-4"><h5>Workshop Vendor Portal</h5><p class="text-muted">${__("Vendor maintenance portal")}</p></div>`);
};
