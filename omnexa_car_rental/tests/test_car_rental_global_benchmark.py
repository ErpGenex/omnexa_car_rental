# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_car_rental.car_rental_gap_register import GLOBAL_LEADER_TARGET, get_gap_status
from omnexa_car_rental.car_rental_global_benchmark import get_global_rental_score
from omnexa_car_rental.workspace.car_rental_workspace import sync_car_rental_workspace_menu


class TestCarRentalGlobalBenchmark(FrappeTestCase):
	def test_global_score_returns_matrix(self):
		score = get_global_rental_score()
		self.assertIn("weighted_score", score)
		self.assertGreaterEqual(score["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(score.get("global_leader_gate"))
		self.assertEqual(score["gaps_total"], 96)
		self.assertEqual(score["gaps_open"], 0)

	def test_gap_register_structure(self):
		gaps = get_gap_status()
		self.assertEqual(len(gaps["gaps"]), 96)
		self.assertIn("gaps_open", gaps)

	def test_workspace_sync(self):
		stats = sync_car_rental_workspace_menu(save=True, rebuild=True)
		self.assertGreater(stats["sections"], 5)
		self.assertGreater(stats["total_links"], 20)
