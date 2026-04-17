// Copyright (c) 2026, Omnexa and contributors
// License: See license.txt

frappe.ui.form.on("Rental Booking", {
	refresh(frm) {
		if (
			!frm.is_new() &&
			["Confirmed", "Inquiry"].includes(frm.doc.booking_status) &&
			!frm.doc.rental_contract &&
			frm.doc.booking_status !== "Cancelled"
		) {
			frm.add_custom_button(__("Create Rental Contract"), () => {
				frappe.call({
					method: "omnexa_car_rental.api.create_rental_contract_from_booking",
					args: { booking: frm.doc.name },
					freeze: true,
					callback(r) {
						if (r.message) {
							frappe.set_route("Form", "Rental Contract", r.message);
						}
					},
				});
			});
		}
		if (frm.doc.rental_contract) {
			frm.add_custom_button(
				__("Open Rental Contract"),
				() => frappe.set_route("Form", "Rental Contract", frm.doc.rental_contract),
				__("Links")
			);
		}
	},
});
