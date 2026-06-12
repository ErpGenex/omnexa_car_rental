# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

"""Map provider-specific payloads to the canonical Omnexa toll JSON shape.

Canonical keys expected by toll_ingestion._map_payload_to_row:
transaction_id, crossing_datetime, amount, currency,
plate_number, tag_id, toll_gate_name, toll_gate_code, country, entry_time, exit_time

Official Salik/DARB APIs differ; mappers cover RTA Salik + ITC DARB fleet feed field names.
"""

from __future__ import annotations

from typing import Any


def adapt_provider_payload(provider_code: str, data: dict[str, Any]) -> dict[str, Any]:
	if not data or not isinstance(data, dict):
		return data
	code = (provider_code or "").strip().upper()
	if code == "SALIK":
		return _adapt_salik(data)
	if code == "DARB":
		return _adapt_darb(data)
	return data


def _adapt_salik(data: dict[str, Any]) -> dict[str, Any]:
	"""Placeholder mapping for RTA Salik-style feeds (field names vary by integration tier)."""
	out = dict(data)
	if "transaction_id" not in out and data.get("transactionId"):
		out["transaction_id"] = data.get("transactionId")
	if "crossing_datetime" not in out and data.get("transactionDateTime"):
		out["crossing_datetime"] = data.get("transactionDateTime")
	if "amount" not in out and data.get("amount") is None:
		out["amount"] = data.get("tollAmount") or data.get("fee")
	if "plate_number" not in out or not out.get("plate_number"):
		out["plate_number"] = data.get("plateNumber") or data.get("plate")
	if "tag_id" not in out or not out.get("tag_id"):
		out["tag_id"] = data.get("tagNumber") or data.get("salikTagId")
	if "toll_gate_name" not in out or not out.get("toll_gate_name"):
		out["toll_gate_name"] = data.get("gateName") or data.get("locationDescription")
	if "toll_gate_code" not in out or not out.get("toll_gate_code"):
		out["toll_gate_code"] = data.get("gateCode") or data.get("tollGateId")
	if "currency" not in out or not out.get("currency"):
		out["currency"] = data.get("currencyCode") or "AED"
	if "country" not in out or not out.get("country"):
		out["country"] = data.get("countryCode") or "AE"
	return out


def _adapt_darb(data: dict[str, Any]) -> dict[str, Any]:
	"""Placeholder mapping for ITC Abu Dhabi DARB-style payloads."""
	out = dict(data)
	if "transaction_id" not in out and data.get("trans_id"):
		out["transaction_id"] = data.get("trans_id")
	if "crossing_datetime" not in out and data.get("passage_time"):
		out["crossing_datetime"] = data.get("passage_time")
	if "amount" not in out and data.get("amount") is None:
		out["amount"] = data.get("toll_fee") or data.get("fee")
	if "plate_number" not in out or not out.get("plate_number"):
		out["plate_number"] = data.get("plate") or data.get("licensePlate")
	if "tag_id" not in out or not out.get("tag_id"):
		out["tag_id"] = data.get("tag_serial") or data.get("obu_id")
	if "toll_gate_name" not in out or not out.get("toll_gate_name"):
		out["toll_gate_name"] = data.get("checkpoint") or data.get("gantry_name")
	if "toll_gate_code" not in out or not out.get("toll_gate_code"):
		out["toll_gate_code"] = data.get("checkpoint_code")
	if "currency" not in out or not out.get("currency"):
		out["currency"] = data.get("currency") or "AED"
	if "country" not in out or not out.get("country"):
		out["country"] = "AE"
	return out
