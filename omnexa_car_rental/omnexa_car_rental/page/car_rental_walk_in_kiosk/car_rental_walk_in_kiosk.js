frappe.pages["car-rental-walk-in-kiosk"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Walk-In Kiosk"), single_column: true });
	$(page.body).html(`<div class="p-4"><h5>Walk-In Kiosk</h5><p class="text-muted">${__("Walk-in rental kiosk mode")}</p></div>`);
};
