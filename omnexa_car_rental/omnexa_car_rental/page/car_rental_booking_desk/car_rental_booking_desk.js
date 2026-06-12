frappe.pages["car-rental-booking-desk"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Online Booking Desk"), single_column: true });
	$(page.body).html(`
		<div class="p-4">
			<p>${__("Guest API")}: <code>omnexa_car_rental.api.web_booking.book_rental_online</code></p>
			<p>${__("Availability")}: <code>get_available_vehicles</code> · ${__("Quote")}: <code>quote_rental_rate</code></p>
			<a class="btn btn-primary" href="/app/rental-booking">${__("Open Rental Bookings")}</a>
		</div>`);
};
