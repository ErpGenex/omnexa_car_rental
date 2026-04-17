# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

from frappe.tests.utils import FrappeTestCase

from omnexa_car_rental.omnexa_car_rental.rental_availability import intervals_overlap


class TestRentalAvailability(FrappeTestCase):
	def test_intervals_overlap_touching_boundary_no_overlap(self):
		# end A == start B → no overlap (half-open interpretation via strict <)
		self.assertFalse(
			intervals_overlap("2026-01-01 10:00:00", "2026-01-02 10:00:00", "2026-01-02 10:00:00", "2026-01-03 10:00:00")
		)

	def test_intervals_overlap_true(self):
		self.assertTrue(
			intervals_overlap("2026-01-01 10:00:00", "2026-01-03 10:00:00", "2026-01-02 10:00:00", "2026-01-04 10:00:00")
		)
