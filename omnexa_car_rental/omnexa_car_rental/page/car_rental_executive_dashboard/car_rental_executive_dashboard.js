frappe.pages["car-rental-executive-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Car Rental Executive Dashboard"), single_column: true });
	frappe.call({
		method: "omnexa_car_rental.car_rental_global_benchmark.get_global_rental_score",
		callback(r) {
			const s = r.message || {};
			$(page.body).html(`
				<div class="p-4">
					<h4>${__("Global Rental Score")}: <b>${s.weighted_score || 0}</b> / ${s.global_leader_target || 4.85}</h4>
					<p class="text-muted">${__("Target")}: Rentall · TSD · HQ Rental · Rent Centric</p>
					<p>${__("Gaps closed")}: ${s.gaps_closed || 0} / ${s.gaps_total || 96}</p>
					<p>${__("Ranking")}: ${(s.ranking && s.ranking.label_ar) || ""}</p>
				</div>`);
		},
	});
};
