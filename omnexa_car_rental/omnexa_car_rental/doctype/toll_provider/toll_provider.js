frappe.ui.form.on("Toll Provider", {
	refresh(frm) {
		if (frm.is_new()) return;
		const code = (frm.doc.provider_code || "").toUpperCase();
		if (!["SALIK", "DARB"].includes(code)) return;

		frm.add_custom_button(__("Test Connection"), () => {
			const method =
				code === "SALIK"
					? "omnexa_car_rental.api.toll_integrations.test_salik_connection"
					: "omnexa_car_rental.api.toll_integrations.test_darb_connection";
			frappe.call({
				method,
				callback(r) {
					frappe.msgprint({
						title: __("Connection OK"),
						message: `<pre>${frappe.utils.escape_html(JSON.stringify(r.message, null, 2))}</pre>`,
						indicator: "green",
					});
				},
			});
		});

		if (frm.doc.integration_type === "API Polling") {
			frm.add_custom_button(__("Sync Now"), () => {
				frappe.call({
					method: "omnexa_car_rental.api.toll_integrations.sync_toll_provider",
					args: { provider_code: code, force: 1 },
					callback(r) {
						frappe.msgprint({
							title: __("Sync Complete"),
							message: `<pre>${frappe.utils.escape_html(JSON.stringify(r.message, null, 2))}</pre>`,
						});
						frm.reload_doc();
					},
				});
			});
		}
	},
});
