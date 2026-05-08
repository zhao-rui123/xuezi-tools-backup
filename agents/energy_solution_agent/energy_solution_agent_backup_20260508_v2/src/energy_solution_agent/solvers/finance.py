from __future__ import annotations

import math
from typing import Any

from .arbitrage import _normalize_price_series_to_yuan_per_mwh, _select_best_daily_spot_cycles

def settlement_and_finance(
    data: dict[str, Any],
    simulation: dict[str, Any],
    carbon: dict[str, Any],
    storage_value_override: float | None = None,
    extra_annual_revenue: float = 0.0,
) -> dict[str, Any]:
    financial = data.get("financial", {})
    market = data.get("market_data", {})
    backup = data.get("equipment", {}).get("conventional_backup", {})
    degradation = financial.get("degradation") or {}
    tou = market.get("tou_tariff") or []
    avg_price = 0.72
    if tou:
        prices = [float(item.get("price", 0.0)) for item in tou if item.get("price") is not None]
        if prices:
            avg_price = sum(prices) / len(prices)
    gross_demand = (
        float(data.get("load_data", {}).get("annual_consumption_mwh") or 0.0)
        + float(simulation.get("annual_charging_energy_mwh") or 0.0)
        + (float(simulation.get("annual_cooling_energy_mwh") or 0.0) / 3.5 if simulation.get("annual_cooling_energy_mwh") else 0.0)
        + (float(simulation.get("annual_heating_energy_mwh") or 0.0) / 3.0 if simulation.get("annual_heating_energy_mwh") else 0.0)
    )
    market_mode = str(market.get("market_mode") or "").lower()
    fuel_cost = float(market.get("fuel_cost_per_kwh") or backup.get("fuel_cost_per_kwh") or avg_price)
    if market_mode == "offgrid_internal" and fuel_cost > 0:
        avg_price = fuel_cost
        renewable_served_mwh = max(0.0, gross_demand - float(simulation.get("annual_grid_purchase_mwh") or 0.0))
        direct_renewable_used_mwh = min(
            gross_demand,
            max(
                0.0,
                float(simulation.get("annual_pv_generation_mwh") or 0.0)
                + float(simulation.get("annual_wind_generation_mwh") or 0.0)
                - float(simulation.get("annual_export_mwh") or 0.0)
                - float(simulation.get("annual_curtailment_mwh") or 0.0),
            ),
        )
        direct_renewable_used_mwh = min(direct_renewable_used_mwh, renewable_served_mwh)
        renewable_total_mwh = max(
            0.0,
            float(simulation.get("annual_pv_generation_mwh") or 0.0) + float(simulation.get("annual_wind_generation_mwh") or 0.0),
        )
        pv_share = float(simulation.get("annual_pv_generation_mwh") or 0.0) / renewable_total_mwh if renewable_total_mwh > 0 else 0.0
        wind_share = float(simulation.get("annual_wind_generation_mwh") or 0.0) / renewable_total_mwh if renewable_total_mwh > 0 else 0.0
        pv_saving = direct_renewable_used_mwh * fuel_cost * 1000 * pv_share
        wind_saving = direct_renewable_used_mwh * fuel_cost * 1000 * wind_share
        charge_saving = max(0.0, renewable_served_mwh - direct_renewable_used_mwh) * fuel_cost * 1000
    else:
        charge_saving = float(simulation.get("annual_storage_discharge_mwh") or 0.0) * max(avg_price - 0.35, 0.1) * 1000
        pv_saving = float(simulation.get("annual_pv_generation_mwh") or 0.0) * avg_price * 0.78 * 1000
        wind_saving = float(simulation.get("annual_wind_generation_mwh") or 0.0) * avg_price * 0.72 * 1000
    if storage_value_override is not None:
        charge_saving = float(storage_value_override)
    charging_margin = float(simulation.get("annual_charging_energy_mwh") or 0.0) * 120
    thermal_saving = (float(simulation.get("annual_cooling_energy_mwh") or 0.0) + float(simulation.get("annual_heating_energy_mwh") or 0.0)) * 70
    carbon_value = float(carbon.get("annual_reduction_tco2e") or 0.0) * float(financial.get("carbon_price_assumption") or 0.0)
    export_revenue = float(simulation.get("annual_export_mwh") or 0.0) * _resolve_export_price_per_kwh(market, avg_price) * 1000
    annual_revenue = charge_saving + pv_saving + wind_saving + charging_margin + thermal_saving + carbon_value + export_revenue + extra_annual_revenue

    capex = financial.get("capex", {})
    storage_capex = (simulation.get("storage_energy_mwh") or 0.0) * 1000 * float(capex.get("storage_system_cost_per_kwh") or 850)
    pv_capex = (simulation.get("pv_mwp") or 0.0) * 1_000_000 * float(capex.get("pv_cost_per_w") or 3.2)
    wind_capex = (simulation.get("wind_mw") or 0.0) * 1_000_000 * float(capex.get("wind_cost_per_w") or 6.5)
    thermal_capex = float(capex.get("thermal_system_total") or 0.0)
    charging_capex = float(capex.get("charging_system_total") or 0.0)
    capex_total = storage_capex + pv_capex + wind_capex + thermal_capex + charging_capex
    opex_ratio = float((financial.get("opex") or {}).get("annual_om_ratio") or 0.015)
    opex_escalation_rate = float((financial.get("opex") or {}).get("annual_opex_escalation_rate") or 0.02)
    opex_annual = capex_total * opex_ratio
    storage_degradation = float(degradation.get("storage_capacity_fade_per_year") or 0.025)
    pv_degradation = float(degradation.get("pv_degradation_per_year") or 0.005)
    wind_degradation = float(degradation.get("wind_degradation_per_year") or 0.003)
    years = int(financial.get("project_years") or 15)
    discount_rate = float(financial.get("discount_rate") or 0.08)
    cycle_life = float((data.get("equipment", {}).get("storage", {}) or {}).get("cycle_life") or 6000.0)
    annual_fec = float(simulation.get("storage_equivalent_full_cycles_per_year") or 0.0)
    storage_life_years = (cycle_life / annual_fec) if annual_fec > 0 else None
    tax_profile = _resolve_tax_profile(data)
    replacement_year = None
    replacement_cost = 0.0
    if storage_life_years and storage_life_years < years:
        replacement_year = max(1, min(years, int(round(storage_life_years))))
        replacement_cost = storage_capex * float((financial.get("capex") or {}).get("storage_replacement_cost_ratio") or 0.55)

    # ── VAT input credit from initial capex ──
    # Chinese VAT is a credit-invoice system: input VAT on purchases offsets output VAT on sales.
    # Equipment purchases → 13% input VAT; construction/installation → 9% input VAT.
    tax_cfg = data.get("financial", {}).get("tax", {}) or {}
    equipment_ratio = float(tax_cfg.get("capex_equipment_ratio") or 0.85)
    eq_vat_rate = float(tax_profile.get("equipment_vat_rate") if tax_profile.get("equipment_vat_rate") is not None else 0.13)
    con_vat_rate = float(tax_profile.get("construction_vat_rate") if tax_profile.get("construction_vat_rate") is not None else 0.09)
    initial_input_vat = 0.0
    if capex_total > 0 and eq_vat_rate > 0:
        eq_capex = capex_total * equipment_ratio
        con_capex = capex_total * (1.0 - equipment_ratio)
        initial_input_vat = eq_capex / (1.0 + eq_vat_rate) * eq_vat_rate + con_capex / (1.0 + con_vat_rate) * con_vat_rate
    remaining_input_vat_credit = initial_input_vat

    price_includes_vat = bool(tax_profile.get("price_includes_vat"))
    output_vat_rate = float(tax_profile.get("vat_rate") if tax_profile.get("vat_rate") is not None else 0.13)
    surtax_total_rate = (
        float(tax_profile.get("surtax_urban_maintenance_rate") if tax_profile.get("surtax_urban_maintenance_rate") is not None else 0.07)
        + float(tax_profile.get("surtax_education_rate") if tax_profile.get("surtax_education_rate") is not None else 0.03)
        + float(tax_profile.get("surtax_local_education_rate") if tax_profile.get("surtax_local_education_rate") is not None else 0.02)
    )
    income_tax_rate = float(tax_profile.get("income_tax_rate") if tax_profile.get("income_tax_rate") is not None else 0.25)
    holiday_years = int(tax_profile.get("income_tax_holiday_years") if tax_profile.get("income_tax_holiday_years") is not None else 0)
    half_years = int(tax_profile.get("income_tax_half_years") if tax_profile.get("income_tax_half_years") is not None else 0)

    cashflows = [-capex_total + initial_input_vat]  # input VAT credit is a cash inflow at year 0
    running_cum = cashflows[0]
    payback = None
    annual_depreciation = _annual_depreciation(capex_total, years, tax_profile)
    first_year_income_tax = 0.0
    first_year_vat_and_surcharges = 0.0
    for year in range(1, years + 1):
        storage_factor = max(0.0, 1.0 - storage_degradation * (year - 1))
        pv_factor = max(0.0, 1.0 - pv_degradation * (year - 1))
        wind_factor = max(0.0, 1.0 - wind_degradation * (year - 1))
        year_revenue = (
            charge_saving * storage_factor
            + pv_saving * pv_factor
            + wind_saving * wind_factor
            + charging_margin
            + thermal_saving
            + carbon_value
            + export_revenue * max(storage_factor, pv_factor, wind_factor)
            + extra_annual_revenue
        )
        year_opex = opex_annual * ((1 + opex_escalation_rate) ** (year - 1))
        year_capex = replacement_cost if replacement_year and year == replacement_year else 0.0

        # ── VAT (增值税) ──
        # Output VAT: if revenue is VAT-inclusive, strip VAT first (价税分离)
        if price_includes_vat and output_vat_rate > 0:
            year_revenue_ex_vat = year_revenue / (1.0 + output_vat_rate)
            year_output_vat = year_revenue - year_revenue_ex_vat
        else:
            year_revenue_ex_vat = year_revenue
            year_output_vat = year_revenue * output_vat_rate

        # Input VAT credit from replacement capex (e.g. battery replacement)
        if year_capex > 0 and eq_vat_rate > 0:
            repl_input_vat = (
                year_capex * equipment_ratio / (1.0 + eq_vat_rate) * eq_vat_rate
                + year_capex * (1.0 - equipment_ratio) / (1.0 + con_vat_rate) * con_vat_rate
            )
            remaining_input_vat_credit += repl_input_vat

        # VAT payable = output VAT - available input VAT credits (留抵抵扣)
        year_vat_payable = max(0.0, year_output_vat - remaining_input_vat_credit)
        remaining_input_vat_credit = max(0.0, remaining_input_vat_credit - year_output_vat)

        # ── VAT surcharges (附加税: 城建税 + 教育费附加 + 地方教育附加) ──
        year_surcharges = year_vat_payable * surtax_total_rate

        year_vat_and_surcharges = year_vat_payable + year_surcharges

        # ── Income tax (企业所得税) ──
        # Surcharges are deductible (税金及附加)
        year_taxable_profit = max(0.0, year_revenue_ex_vat - year_opex - annual_depreciation - year_surcharges)

        # 三免三减半 incentive
        if holiday_years > 0 and year <= holiday_years:
            year_income_tax = 0.0
        elif half_years > 0 and year <= holiday_years + half_years:
            year_income_tax = year_taxable_profit * income_tax_rate * 0.5
        else:
            year_income_tax = year_taxable_profit * income_tax_rate

        year_cashflow = year_revenue - year_opex - year_capex - year_vat_payable - year_surcharges - year_income_tax
        if year == 1:
            first_year_income_tax = year_income_tax
            first_year_vat_and_surcharges = year_vat_and_surcharges
        cashflows.append(year_cashflow)
        running_cum += year_cashflow
        if payback is None and running_cum >= 0:
            payback = float(year)
    irr = _compute_irr(cashflows)
    npv = 0.0
    for year_idx, cashflow in enumerate(cashflows):
        npv += cashflow / ((1 + discount_rate) ** year_idx)
    abatement_cost = None
    if carbon.get("annual_reduction_tco2e"):
        lifetime_reduction = carbon["annual_reduction_tco2e"] * years
        if lifetime_reduction > 0:
            lifetime_cost = capex_total + replacement_cost + sum(opex_annual * ((1 + opex_escalation_rate) ** (year - 1)) for year in range(1, years + 1))
            lifetime_revenue = sum(cashflows[1:]) + replacement_cost + sum(opex_annual * ((1 + opex_escalation_rate) ** (year - 1)) for year in range(1, years + 1))
            abatement_cost = max(0.0, (lifetime_cost - lifetime_revenue) / lifetime_reduction)

    incentive_label = ""
    if holiday_years > 0 and half_years > 0:
        incentive_label = f"_3x3_incentive"
    elif holiday_years > 0:
        incentive_label = f"_holiday{holiday_years}"

    return {
        "price_mechanism_summary": _describe_price_mode(market),
        "revenue_breakdown": _revenue_breakdown_v2(charge_saving, pv_saving, wind_saving, charging_margin, thermal_saving, carbon_value, export_revenue),
        "annual_savings_or_revenue": round(annual_revenue, 2),
        "annual_tax_total": round(first_year_income_tax + first_year_vat_and_surcharges, 2),
        "annual_income_tax": round(first_year_income_tax, 2),
        "annual_vat_and_surcharges": round(first_year_vat_and_surcharges, 2),
        "annual_vat_payable": round(first_year_vat_and_surcharges - first_year_vat_and_surcharges * surtax_total_rate / (1.0 + surtax_total_rate), 2) if first_year_vat_and_surcharges else 0.0,
        "annual_vat_surcharges_only": round(first_year_vat_and_surcharges * surtax_total_rate / (1.0 + surtax_total_rate), 2) if surtax_total_rate > 0 and first_year_vat_and_surcharges else 0.0,
        "initial_input_vat_credit": round(initial_input_vat, 2),
        "tax_model": str(tax_profile.get("model") if tax_profile.get("model") is not None else "unspecified") + incentive_label,
        "capex_total": round(capex_total, 2),
        "opex_annual": round(opex_annual, 2),
        "annual_export_revenue": round(export_revenue, 2),
        "payback_years": round(payback, 2) if payback else None,
        "irr": round(irr, 4) if irr is not None else None,
        "npv": round(npv, 2),
        "abatement_cost_per_tco2e": round(abatement_cost, 2) if abatement_cost is not None else None,
        "storage_replacement_year": replacement_year,
        "storage_replacement_cost": round(replacement_cost, 2) if replacement_cost else None,
        "opex_escalation_rate": opex_escalation_rate,
    }


def _resolve_tax_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Resolve tax profile for the project.

    Returns a dict with:
      - model: str
      - income_tax_rate: float (statutory rate before incentives)
      - income_tax_holiday_years: int (full exemption years, e.g. 三免)
      - income_tax_half_years: int (half-rate years, e.g. 三减半)
      - vat_rate: float (output VAT rate on sales)
      - equipment_vat_rate: float (input VAT on equipment purchases)
      - construction_vat_rate: float (input VAT on construction/installation)
      - surtax_urban_maintenance_rate: float (城建税)
      - surtax_education_rate: float (教育费附加)
      - surtax_local_education_rate: float (地方教育附加)
      - depreciation_years: float
      - price_includes_vat: bool (whether revenue figures already include VAT)
    """
    tax = data.get("financial", {}).get("tax", {}) or {}
    model = str(tax.get("model") or "").lower()

    if model in {"none", "overseas_exempt", "tax_exempt"}:
        return {
            "model": "overseas_exempt",
            "income_tax_rate": 0.0,
            "income_tax_holiday_years": 0,
            "income_tax_half_years": 0,
            "vat_rate": 0.0,
            "equipment_vat_rate": 0.0,
            "construction_vat_rate": 0.0,
            "surtax_urban_maintenance_rate": 0.0,
            "surtax_education_rate": 0.0,
            "surtax_local_education_rate": 0.0,
            "depreciation_years": 0.0,
            "price_includes_vat": False,
        }

    if not (model in {"china_domestic", "cn"} or _is_china_domestic_project(data)):
        return {
            "model": "overseas_exempt",
            "income_tax_rate": 0.0,
            "income_tax_holiday_years": 0,
            "income_tax_half_years": 0,
            "vat_rate": 0.0,
            "equipment_vat_rate": 0.0,
            "construction_vat_rate": 0.0,
            "surtax_urban_maintenance_rate": 0.0,
            "surtax_education_rate": 0.0,
            "surtax_local_education_rate": 0.0,
            "depreciation_years": 0.0,
            "price_includes_vat": False,
        }

    # ── China domestic ──────────────────────────────────────────────
    incentive_mode = str(tax.get("incentive_mode") or "").lower()

    # Income tax incentive: 三免三减半 (3yr exempt + 3yr half) per
    # 《企业所得税法》第27条 + 《公共基础设施项目企业所得税优惠目录》(财税〔2008〕116号)
    # Applies to solar power generation and other qualifying public infrastructure projects.
    has_renewable = bool(
        (data.get("resource_data", {}).get("solar", {}).get("available_area_m2"))
        or (data.get("resource_data", {}).get("solar", {}).get("installed_capacity_mwp"))
        or (data.get("resource_data", {}).get("wind", {}).get("annual_avg_speed_mps"))
    )
    if incentive_mode == "renewable_3x3" or (incentive_mode not in {"standard", "western_development", "high_tech"} and has_renewable):
        income_tax_holiday_years = int(tax.get("income_tax_holiday_years") or 3)
        income_tax_half_years = int(tax.get("income_tax_half_years") or 3)
    elif incentive_mode == "western_development":
        # 西部大开发优惠税率 15% (财税〔2020〕23号)
        income_tax_holiday_years = 0
        income_tax_half_years = 0
    elif incentive_mode == "high_tech":
        # 高新技术企业 15%
        income_tax_holiday_years = 0
        income_tax_half_years = 0
    else:
        income_tax_holiday_years = 0
        income_tax_half_years = 0

    statutory_rate = float(tax.get("income_tax_rate") or 0.25)
    if incentive_mode == "western_development":
        statutory_rate = float(tax.get("income_tax_rate") or 0.15)
    elif incentive_mode == "high_tech":
        statutory_rate = float(tax.get("income_tax_rate") or 0.15)

    # Surtax rates (附加税):
    #   城建税 7% (city) / 5% (town) / 1% (other)
    #   教育费附加 3%
    #   地方教育附加 2%
    city_level = str((data.get("project_info", {}) or {}).get("city_level") or "").lower()
    if city_level in {"county", "town", "village", "县域", "乡镇"}:
        urban_maintenance = 0.05
    elif city_level in {"other", "其他"}:
        urban_maintenance = 0.01
    else:
        urban_maintenance = 0.07

    return {
        "model": "china_domestic",
        "income_tax_rate": statutory_rate,
        "income_tax_holiday_years": income_tax_holiday_years,
        "income_tax_half_years": income_tax_half_years,
        "vat_rate": float(tax.get("vat_rate") or 0.13),
        "equipment_vat_rate": float(tax.get("equipment_vat_rate") or 0.13),
        "construction_vat_rate": float(tax.get("construction_vat_rate") or 0.09),
        "surtax_urban_maintenance_rate": float(tax.get("surtax_urban_maintenance_rate") or urban_maintenance),
        "surtax_education_rate": float(tax.get("surtax_education_rate") or 0.03),
        "surtax_local_education_rate": float(tax.get("surtax_local_education_rate") or 0.02),
        "depreciation_years": float(tax.get("depreciation_years") or 10.0),
        "price_includes_vat": bool(tax.get("price_includes_vat") if tax.get("price_includes_vat") is not None else True),
    }


def _is_china_domestic_project(data: dict[str, Any]) -> bool:
    project = data.get("project_info", {})
    country = str(project.get("country") or "").strip().lower()
    province = str(project.get("province") or "").strip().lower()
    if country in {"china", "prc", "cn", "中国", "中华人民共和国"}:
        return True
    if country and country not in {"china", "prc", "cn", "中国", "中华人民共和国"}:
        return False
    return province not in {"", "overseas", "海外"}


def _annual_depreciation(capex_total: float, project_years: int, tax_profile: dict[str, Any]) -> float:
    depreciation_years = float(tax_profile.get("depreciation_years") if tax_profile.get("depreciation_years") is not None else 0.0)
    if depreciation_years <= 0 or capex_total <= 0:
        return 0.0
    horizon = max(1.0, min(float(project_years), depreciation_years))
    return capex_total / horizon


def _compute_irr(cashflows: list[float]) -> float | None:
    """Compute Internal Rate of Return using Newton's method.

    Handles the common energy-project cashflow pattern: negative initial outflow
    followed by positive annual returns. Returns None if IRR cannot be determined.
    """
    if len(cashflows) < 2:
        return None
    if all(c >= 0 for c in cashflows) or all(c <= 0 for c in cashflows):
        return None

    # Initial guess via 1/payback approximation, bounded
    cumulative = cashflows[0]
    payback = None
    for year_idx in range(1, len(cashflows)):
        cumulative += cashflows[year_idx]
        if payback is None and cumulative >= 0:
            payback = float(year_idx)
            break
    guess = 1.0 / payback if payback and payback > 0 else 0.08
    guess = max(0.001, min(0.50, guess))

    # Newton's method: find r such that NPV(r) = 0
    for _ in range(50):
        npv_val = 0.0
        dnpv_val = 0.0
        for t, cf in enumerate(cashflows):
            denom = (1.0 + guess) ** t
            npv_val += cf / denom
            if t > 0:
                dnpv_val -= t * cf / ((1.0 + guess) ** (t + 1))
        if abs(npv_val) < 1e-6:
            return guess
        if abs(dnpv_val) < 1e-12:
            break
        guess -= npv_val / dnpv_val
        guess = max(-0.99, min(2.0, guess))

    # Verify result
    check_npv = sum(cf / ((1.0 + guess) ** t) for t, cf in enumerate(cashflows))
    if abs(check_npv) < 1e-4 and -0.05 <= guess <= 1.0:
        return max(-0.05, guess)
    return None


def _describe_price_mode(market: dict[str, Any]) -> str:
    mode = market.get("market_mode") or ""
    if mode:
        return mode
    if market.get("market_price_series"):
        return "market_price_series"
    if market.get("tou_tariff"):
        return "tou_tariff"
    return "unspecified"


def _revenue_breakdown(charge: float, pv: float, wind: float, charging: float, thermal: float, carbon: float) -> list[str]:
    items = []
    if charge > 0:
        items.append("储能节费/削峰收益")
    if pv > 0:
        items.append("光伏自发自用收益")
    if wind > 0:
        items.append("风电替代收益")
    if charging > 0:
        items.append("充电服务毛收益")
    if thermal > 0:
        items.append("冷热系统节费收益")
    if carbon > 0:
        items.append("碳减排价值")
    return items


def _resolve_export_price_per_kwh(market: dict[str, Any], fallback_price: float) -> float:
    if market.get("export_price_per_kwh") not in (None, ""):
        return float(market.get("export_price_per_kwh") or 0.0)
    export_series = [float(v) for v in (market.get("export_price_series") or []) if v is not None]
    if export_series:
        return sum(export_series) / len(export_series)
    market_prices = [float(v) for v in (market.get("market_price_series") or []) if v is not None]
    if market_prices:
        positive = [value for value in market_prices if value > 0]
        if positive:
            return sum(positive) / len(positive)
    return fallback_price * 0.7


def _build_market_cooptimization_daily_plan(
    day_prices: list[float],
    interval_hours: float,
    power_mw: float,
    energy_mwh: float,
    threshold_price: float,
    spread_margin: float,
    min_charge_hours: int,
    min_discharge_hours: int,
    max_charge_hours: int,
    max_discharge_hours: int,
    effective_rte: float,
    usable_depth: float,
    discharge_path_eff: float,
) -> dict[str, Any]:
    if not day_prices:
        return {
            "charge_steps": [],
            "discharge_steps": [],
            "future_peak_price": 0.0,
        }
    steps_per_hour = max(1, int(round(1.0 / max(interval_hours, 1e-9))))
    hourly_prices = [
        sum(float(v) for v in day_prices[idx : idx + steps_per_hour]) / steps_per_hour
        for idx in range(0, len(day_prices), steps_per_hour)
    ]
    future_peak_price = max(float(value) for value in hourly_prices)
    charge_steps = [False] * len(day_prices)
    discharge_steps = [False] * len(day_prices)
    if future_peak_price <= threshold_price + spread_margin:
        return {
            "charge_steps": charge_steps,
            "discharge_steps": discharge_steps,
            "future_peak_price": future_peak_price,
        }
    normalized_prices = _normalize_price_series_to_yuan_per_mwh(hourly_prices, unit_hint="yuan_per_kwh")
    candidate_cycles = _select_best_daily_spot_cycles(
        normalized_prices,
        min_charge_hours=min_charge_hours,
        min_discharge_hours=min_discharge_hours,
        min_spread_yuan_per_mwh=spread_margin * 1000.0,
        power_mw=power_mw,
        energy_mwh=energy_mwh,
        usable_depth=usable_depth,
        charge_path_eff=1.0,
        discharge_path_eff=discharge_path_eff,
        effective_rte=effective_rte,
        max_charge_hours=max_charge_hours,
        max_discharge_hours=max_discharge_hours,
    )
    filtered_cycles = [
        cycle
        for cycle in candidate_cycles
        if float(cycle.get("charge_avg_price") or 0.0) / 1000.0 <= threshold_price
    ]
    for cycle in filtered_cycles:
        charge_start = int(cycle["charge_start"]) * steps_per_hour
        charge_end = int(cycle["charge_end"]) * steps_per_hour
        discharge_start = int(cycle["discharge_start"]) * steps_per_hour
        discharge_end = int(cycle["discharge_end"]) * steps_per_hour
        for idx in range(charge_start, min(charge_end, len(charge_steps))):
            charge_steps[idx] = True
        for idx in range(discharge_start, min(discharge_end, len(discharge_steps))):
            discharge_steps[idx] = True
    return {
        "charge_steps": charge_steps,
        "discharge_steps": discharge_steps,
        "future_peak_price": future_peak_price,
    }


def _append_market_daily_cycle_schedule(
    daily_schedule: list[dict[str, Any]],
    day_index: int,
    interval_hours: float,
    charge_energy_kwh: list[float],
    discharge_energy_kwh: list[float],
    renewable_charge_kwh: list[float],
    grid_charge_kwh: list[float],
    charge_prices: list[float],
    discharge_prices: list[float],
) -> None:
    charge_segments = _extract_energy_segments(charge_energy_kwh, charge_prices)
    discharge_segments = _extract_energy_segments(discharge_energy_kwh, discharge_prices)
    if not charge_segments and not discharge_segments:
        return
    cycles = []
    pair_count = min(len(charge_segments), len(discharge_segments))
    for idx in range(pair_count):
        charge_seg = charge_segments[idx]
        discharge_seg = discharge_segments[idx]
        charge_energy_mwh = charge_seg["energy_kwh"] / 1000
        discharge_energy_mwh = discharge_seg["energy_kwh"] / 1000
        gross_margin = discharge_energy_mwh * discharge_seg["avg_price"] - charge_energy_mwh * charge_seg["avg_price"]
        renewable_charge = sum(renewable_charge_kwh[charge_seg["start"] : charge_seg["end"]])
        grid_charge = sum(grid_charge_kwh[charge_seg["start"] : charge_seg["end"]])
        if renewable_charge > 0 and grid_charge > 0:
            charge_source = "mixed"
        elif renewable_charge > 0:
            charge_source = "renewable"
        elif grid_charge > 0:
            charge_source = "grid"
        else:
            charge_source = "unknown"
        cycles.append(
            {
                "cycle_index": idx + 1,
                "charge_window": _format_step_window(charge_seg["start"], charge_seg["end"], interval_hours),
                "discharge_window": _format_step_window(discharge_seg["start"], discharge_seg["end"], interval_hours),
                "charge_price_avg": round(charge_seg["avg_price"], 6),
                "discharge_price_avg": round(discharge_seg["avg_price"], 6),
                "spread_yuan_per_mwh": round((discharge_seg["avg_price"] - charge_seg["avg_price"]) * 1000, 2),
                "effective_spread_yuan_per_mwh": round((gross_margin / max(discharge_energy_mwh, 1e-9)), 2) if discharge_energy_mwh > 0 else None,
                "charge_energy_mwh": round(charge_energy_mwh, 6),
                "discharge_energy_mwh": round(discharge_energy_mwh, 6),
                "gross_margin": round(gross_margin, 2),
                "charge_source": charge_source,
            }
        )
    daily_schedule.append(
        {
            "date": f"day_{day_index}",
            "cycle_count": len(cycles),
            "gross_margin": round(sum(float(cycle["gross_margin"]) for cycle in cycles), 2),
            "cycles": cycles,
        }
    )


def _extract_energy_segments(energy_kwh: list[float], prices: list[float]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    start = None
    weighted_price = 0.0
    total_energy = 0.0
    for idx, energy in enumerate(energy_kwh):
        if energy > 0 and start is None:
            start = idx
            weighted_price = energy * prices[idx]
            total_energy = energy
            continue
        if energy > 0 and start is not None:
            weighted_price += energy * prices[idx]
            total_energy += energy
            continue
        if energy <= 0 and start is not None:
            segments.append(
                {
                    "start": start,
                    "end": idx,
                    "energy_kwh": total_energy,
                    "avg_price": weighted_price / max(total_energy, 1e-9),
                }
            )
            start = None
            weighted_price = 0.0
            total_energy = 0.0
    if start is not None:
        segments.append(
            {
                "start": start,
                "end": len(energy_kwh),
                "energy_kwh": total_energy,
                "avg_price": weighted_price / max(total_energy, 1e-9),
            }
        )
    return segments


def _format_step_window(start: int, end: int, interval_hours: float) -> str:
    start_hour = start * interval_hours
    end_hour = end * interval_hours
    return f"{_format_fractional_hour(start_hour)}-{_format_fractional_hour(end_hour)}"


def _format_fractional_hour(value: float) -> str:
    total_minutes = int(round(value * 60))
    hour = (total_minutes // 60) % 24
    minute = total_minutes % 60
    return f"{hour:02d}:{minute:02d}"


def _revenue_breakdown_v2(charge: float, pv: float, wind: float, charging: float, thermal: float, carbon: float, export: float) -> list[str]:
    items = []
    if charge > 0:
        items.append("储能节费/市场释放收益")
    if pv > 0:
        items.append("光伏替代购电收益")
    if wind > 0:
        items.append("风电替代购电收益")
    if charging > 0:
        items.append("充电服务毛收益")
    if thermal > 0:
        items.append("冷热系统节费收益")
    if carbon > 0:
        items.append("碳减排价值")
    if export > 0:
        items.append("余电上网/市场外送收益")
    return items


