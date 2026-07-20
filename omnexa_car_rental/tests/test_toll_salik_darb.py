# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_car_rental.api.toll_integrations import get_toll_integration_status, sync_toll_provider, test_darb_connection, test_salik_connection
from omnexa_car_rental.omnexa_car_rental.toll.toll_adapters import adapt_provider_payload
from omnexa_car_rental.omnexa_car_rental.toll.toll_ingestion import ingest_payload


class TestTollSalikDarb(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		from omnexa_car_rental.patches.v1_0.seed_salik_darb_providers import execute

		execute()

	def test_salik_adapter_maps_fields(self):
		raw = {
			"transactionId": "SAL-100",
			"transactionDateTime": "2026-06-12 10:00:00",
			"tollAmount": 4,
			"plateNumber": "DXB-1234",
			"salikTagId": "TAG-001",
			"gateName": "Al Safa",
			"gateCode": "G01",
		}
		out = adapt_provider_payload("SALIK", raw)
		self.assertEqual(out["transaction_id"], "SAL-100")
		self.assertEqual(out["amount"], 4)
		self.assertEqual(out["tag_id"], "TAG-001")
		self.assertEqual(out["currency"], "AED")

	def test_darb_adapter_maps_fields(self):
		raw = {
			"trans_id": "DARB-200",
			"passage_time": "2026-06-12 11:00:00",
			"toll_fee": 4,
			"licensePlate": "AUH-5678",
			"obu_id": "OBU-99",
			"checkpoint": "Mussafah",
			"checkpoint_code": "D01",
		}
		out = adapt_provider_payload("DARB", raw)
		self.assertEqual(out["transaction_id"], "DARB-200")
		self.assertEqual(out["plate_number"], "AUH-5678")
		self.assertEqual(out["tag_id"], "OBU-99")

	def test_sandbox_connection_and_sync(self):
		self.assertTrue(test_salik_connection().get("ok"))
		self.assertTrue(test_darb_connection().get("ok"))
		status = get_toll_integration_status()
		self.assertGreaterEqual(len(status["providers"]), 2)
		# Reset cursor for repeatable sandbox ingest
		for code in ("SALIK", "DARB"):
			name = frappe.db.get_value("Toll Provider", {"provider_code": code}, "name")
			frappe.db.set_value("Toll Provider", name, "last_sync_token", "")
		frappe.db.commit()
		result = sync_toll_provider("SALIK", force=1)
		self.assertTrue(result.get("ok"))

	def test_webhook_ingest_salik_payload(self):
		company = frappe.defaults.get_global_default("company") or frappe.get_all("Company", limit=1)[0].name
		branch = frappe.db.get_value("Branch", {"company": company}, "name")
		payload = {
			"transactionId": f"SAL-WH-{frappe.generate_hash(length=6)}",
			"transactionDateTime": "2026-06-12 12:00:00",
			"tollAmount": 4,
			"currencyCode": "AED",
			"plateNumber": "DXB-WH-1",
			"salikTagId": "TAG-WH-1",
			"gateName": "Webhook Gate",
			"gateCode": "WH1",
			"company": company,
			"branch": branch,
		}
		import json

		result = ingest_payload("SALIK", json.dumps(payload), auto_match=True, auto_bill=False)
		self.assertTrue(result.get("ok"))
