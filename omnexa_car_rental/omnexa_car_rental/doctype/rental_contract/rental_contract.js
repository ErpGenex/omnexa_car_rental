// Copyright (c) 2026, Omnexa and contributors
// License: See license.txt

frappe.ui.form.on("Rental Contract", {
	refresh(frm) {
		if (frm.doc.booking) {
			frm.add_custom_button(
				__("Open Booking"),
				() => frappe.set_route("Form", "Rental Booking", frm.doc.booking),
				__("Links")
			);
		}
	},
});
