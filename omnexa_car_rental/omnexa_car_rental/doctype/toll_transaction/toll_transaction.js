// Copyright (c) 2026, Omnexa and contributors
// License: See license.txt

frappe.ui.form.on("Toll Transaction", {
	refresh(frm) {
		if (frm.doc.name && !frm.is_new()) {
			frm.add_custom_button(__("Run Matching"), () => {
				frappe.call({
					method: "omnexa_car_rental.api.toll_run_matching",
					args: {
						toll_transaction: frm.doc.name,
						allow_last_known_renter: 1,
					},
					freeze: true,
					callback(r) {
						if (r.message) {
							frappe.show_alert({
								message: __("Status: {0}", [r.message.status || ""]),
								indicator: "green",
							});
							frm.reload_doc();
						}
					},
				});
			});

			frm.add_custom_button(__("Post Journal Entry (Company / Internal)"), () => {
				frappe.call({
					method: "omnexa_car_rental.api.toll_create_journal_entry",
					args: { toll_transaction: frm.doc.name },
					freeze: true,
					callback(r) {
						const m = r.message || {};
						if (m.journal_entry) {
							frappe.set_route("Form", "Journal Entry", m.journal_entry);
						} else if (m.error) {
							frappe.msgprint(m.error);
						} else if (m.skipped) {
							frappe.show_alert({ message: __("Skipped: {0}", [m.reason || ""]), indicator: "orange" });
						}
						frm.reload_doc();
					},
				});
			});

			frm.add_custom_button(__("Create Customer Invoice"), () => {
				frappe.call({
					method: "omnexa_car_rental.api.toll_create_customer_invoice",
					args: { toll_transaction: frm.doc.name },
					freeze: true,
					callback(r) {
						const m = r.message || {};
						if (m.sales_invoice) {
							frappe.set_route("Form", "Sales Invoice", m.sales_invoice);
						} else if (m.error) {
							frappe.msgprint(m.error);
						} else {
							frappe.show_alert({
								message: __("Billing skipped or not applicable"),
								indicator: "orange",
							});
							frm.reload_doc();
						}
					},
				});
			});

			frm.add_custom_button(__("Refresh FX"), () => {
				frappe.call({
					method: "omnexa_car_rental.api.toll_apply_fx",
					args: { toll_transaction: frm.doc.name },
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			});
		}
	},
});
