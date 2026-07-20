# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Global car rental benchmark — Rentall / TSD / HQ Rental / Rent Centric target 4.85."""

from __future__ import annotations

import frappe

from omnexa_car_rental.car_rental_gap_register import GLOBAL_LEADER_TARGET, get_gap_status

REFERENCE_LEADERS = {
	"rentall": 4.72,
	"tsd_rental": 4.68,
	"hq_rental_software": 4.70,
	"rent_centric": 4.65
	}

# Baseline scores (0–5) before gap closure; uplift applied from closed gaps per domain.
DOMAIN_MATRIX: list[dict] = [
	{"id": "vehicle_management", "label": "Vehicle Management", "weight": 8, "baseline": 2.8, "refs": "Rentall/HQ"
	},
	{"id": "fleet_management", "label": "Fleet Lifecycle & Utilization", "weight": 9, "baseline": 3.0, "refs": "TSD/Rentall"
	},
	{"id": "reservation", "label": "Reservations & Booking", "weight": 10, "baseline": 2.5, "refs": "All"
	},
	{"id": "contract", "label": "Contracts & Agreements", "weight": 8, "baseline": 2.7, "refs": "HQ/Rent Centric"
	},
	{"id": "customer", "label": "Customer & CRM", "weight": 7, "baseline": 2.4, "refs": "Rentall"
	},
	{"id": "driver", "label": "Driver Management", "weight": 5, "baseline": 2.6, "refs": "TSD"
	},
	{"id": "maintenance", "label": "Maintenance & Workshop", "weight": 8, "baseline": 2.9, "refs": "TSD"
	},
	{"id": "accident", "label": "Accidents & Damage", "weight": 6, "baseline": 2.8, "refs": "Rentall"
	},
	{"id": "insurance", "label": "Insurance", "weight": 5, "baseline": 2.7, "refs": "HQ"
	},
	{"id": "digital_channels", "label": "Web / Mobile / Portal", "weight": 9, "baseline": 1.8, "refs": "Rent Centric"
	},
	{"id": "ai_automation", "label": "AI & Automation", "weight": 6, "baseline": 1.5, "refs": "Workday-class"
	},
	{"id": "gps_telematics", "label": "GPS & Telematics", "weight": 7, "baseline": 1.6, "refs": "Enterprise fleet"
	},
	{"id": "financial", "label": "Finance & Revenue", "weight": 8, "baseline": 3.4, "refs": "ERP integrated"
	},
	{"id": "bi", "label": "BI & Executive KPIs", "weight": 6, "baseline": 2.8, "refs": "HQ"
	},
	{"id": "integrations", "label": "Integrations", "weight": 6, "baseline": 2.2, "refs": "All"
	},
	{"id": "security", "label": "Security & Compliance", "weight": 5, "baseline": 3.1, "refs": "ISO/SOC"
	},
]

EXECUTIVE_SCORES_BASELINE = {
	"global_competitiveness": 52,
	"market_readiness": 48,
	"enterprise_readiness": 55,
	"scalability": 50,
	"innovation": 38,
	"security": 58,
	"customer_experience": 42,
	"fleet_management_maturity": 62,
	"financial_management_maturity": 65
	}


def _domain_uplift(domain_id: str, closed_in_domain: int, total_in_domain: int, baseline: float) -> float:
	if total_in_domain <= 0:
		return 0.0
	ratio = closed_in_domain / total_in_domain
	return round(ratio * (4.95 - baseline), 2)


def _score_matrix(gap_rows: list[dict]) -> list[dict]:
	by_domain: dict[str, list[dict]] = {}
	for g in gap_rows:
		by_domain.setdefault(g["domain"], []).append(g)
	out = []
	for row in DOMAIN_MATRIX:
		domain_gaps = by_domain.get(row["id"], [])
		total = len(domain_gaps) or 1
		closed = sum(1 for g in domain_gaps if g.get("status") == "closed")
		score = min(4.95, round(row["baseline"] + _domain_uplift(row["id"], closed, total, row["baseline"]), 2))
		out.append({**row, "score": score, "gaps_closed": closed, "gaps_in_domain": total
	})
	return out


def _executive_scores(weighted: float, gap_pct: float) -> dict[str, int]:
	out = {}
	factor = weighted / GLOBAL_LEADER_TARGET if GLOBAL_LEADER_TARGET else 0
	for key, base in EXECUTIVE_SCORES_BASELINE.items():
		boost = int(round(gap_pct * 40))
		out[key] = min(100, int(round(base * factor + boost * 0.3)))
	return out


def _estimate_ranking(weighted: float) -> dict:
	if weighted >= 4.85:
		return {"tier": "Global #1", "label_ar": "المركز الأول عالمياً (بوابة التقييم الداخلي)", "confidence": "high"
	}
	if weighted >= 4.5:
		return {"tier": "Global Top 10", "label_ar": "أفضل 10 عالمياً", "confidence": "medium"
	}
	if weighted >= 4.0:
		return {"tier": "Global Top 50", "label_ar": "أفضل 50 عالمياً", "confidence": "medium"
	}
	if weighted >= 3.5:
		return {"tier": "Regional Leader", "label_ar": "رائد إقليمي", "confidence": "medium"
	}
	if weighted >= 3.0:
		return {"tier": "National Level", "label_ar": "مستوى وطني", "confidence": "high"
	}
	return {"tier": "Local Level", "label_ar": "مستوى محلي", "confidence": "high"
	}


@frappe.whitelist()
def get_global_rental_score() -> dict:
	gap_status = get_gap_status()
	matrix = _score_matrix(gap_status["gaps"])
	total_weight = sum(r["weight"] for r in matrix)
	weighted = round(sum(r["weight"] * r["score"] for r in matrix) / total_weight, 2) if total_weight else 0
	leader_avg = round(sum(REFERENCE_LEADERS.values()) / len(REFERENCE_LEADERS), 2)
	gap_pct = gap_status["gaps_closed"] / gap_status["gaps_total"] if gap_status["gaps_total"] else 0
	return {
		"weighted_score": weighted,
		"global_leader_target": GLOBAL_LEADER_TARGET,
		"global_leader_gate": weighted >= GLOBAL_LEADER_TARGET and gap_status["gaps_open"] == 0,
		"leader_reference_avg": leader_avg,
		"reference_leaders": REFERENCE_LEADERS,
		"parity_pct_vs_leaders": round(weighted / leader_avg * 100, 1) if leader_avg else 0,
		"matrix": matrix,
		"executive_scores": _executive_scores(weighted, gap_pct),
		"ranking": _estimate_ranking(weighted),
		**{k: gap_status[k] for k in ("gaps_closed", "gaps_total", "gaps_open", "version")},
		"app": "omnexa_car_rental",
		"wave": "global-rental-4"
	}
