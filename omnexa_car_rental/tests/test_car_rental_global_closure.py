# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_car_rental.car_rental_gap_register import GLOBAL_LEADER_TARGET, get_gap_status
from omnexa_car_rental.car_rental_global_benchmark import get_global_rental_score


class TestCarRentalGlobalClosure(FrappeTestCase):
	def test_all_gaps_closed(self):
		gaps = get_gap_status()
		self.assertEqual(gaps["gaps_total"], 96)
		open_gaps = [g for g in gaps["gaps"] if g["status"] == "open"]
		self.assertEqual(gaps["gaps_open"], 0, msg=f"Open: {[g['id'] for g in open_gaps]}")
		self.assertTrue(gaps["global_leader_gate"])

	def test_global_leader_score_gate(self):
		score = get_global_rental_score()
		self.assertGreaterEqual(score["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(score["global_leader_gate"])
		self.assertEqual(score["gaps_open"], 0)
		self.assertEqual(score["ranking"]["tier"], "Global #1")

	def test_wave234_apis_smoke(self):
		from omnexa_car_rental.api.ai_automation import compute_dynamic_price, fleet_copilot_query
		from omnexa_car_rental.api.mobile import get_pwa_config
		from omnexa_car_rental.security.iso27001 import get_iso27001_status

		self.assertIn("manifest", get_pwa_config())
		self.assertIn("answer", fleet_copilot_query("utilization"))
		self.assertIn("controls_total", get_iso27001_status())
