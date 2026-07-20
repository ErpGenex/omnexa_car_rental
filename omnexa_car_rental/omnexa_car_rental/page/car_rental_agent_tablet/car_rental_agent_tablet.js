frappe.pages["car-rental-agent-tablet"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Agent Tablet Check-In/Out"), single_column: true });
	$(page.body).html(`<div class="p-4"><h5>Agent Tablet Check-In/Out</h5><p class="text-muted">${__("Counter check-in and return workflow")}</p></div>`);
};
