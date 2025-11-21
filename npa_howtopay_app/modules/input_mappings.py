"""Input mappings organized by UI sections with tooltips."""
PIPELINE_INPUTS = {
    # Pipeline Economics section
    "pipe_value_per_user": {
        "label": "Pipeline replacement cost",
        "config_path": ["npa", "pipe_value_per_user"],
        "tooltip": "Pipeline replacement cost per NPA household",
        "type": float,
        "min": 0
    },
    # "pipeline_decomm_cost_per_user": {
    #     "label": "Pipeline decommissioning cost per household",
    #     "config_path": ["npa", "pipeline_decomm_cost_per_user"],
    #     "tooltip": "Pipeline decommissioning cost per NPA household"
    # },
    "pipeline_depreciation_lifetime": {
        "label": "Pipeline depreciation",
        "config_path": ["gas", "pipeline_depreciation_lifetime"],
        "tooltip": "Number of years over which pipeline assets are depreciated for accounting purposes",
        "type": int,
        "min": 0
    },
    "pipeline_maintenance_cost_pct": {
        "label": "Maintenance cost (%)",
        "config_path": ["gas", "pipeline_maintenance_cost_pct"],
        "tooltip": "Annual maintenance costs as a percentage of total pipeline value",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    # NPA Program section
    "npa_install_costs_init": {
        "label": "NPA cost per household",
        "config_path": ["shared", "npa_install_costs_init"],
        "tooltip": "Initial cost per household to install NPA equipment (excluding any incentive programs). Cost will grow annually by the cost inflation rate.",
        "type": float,
        "min": 0
    },
    "npa_projects_per_year": {
        "label": "NPA projects per year",
        "config_path": ["npa", "npa_projects_per_year"],
        "tooltip": "Number of NPA projects completed annually. ",
        "type": int,
        "min": 0
    },
    "num_converts_per_project": {
        "label": "Conversions per project",
        "config_path": ["npa", "num_converts_per_project"],
        "tooltip": "Number of household conversions included in each NPA project",
        "type": int,
        "min": 0
    },
    "npa_year_start": {
        "label": "NPA start year",
        "config_path": ["npa", "npa_year_start"],
        "tooltip": "Year NPA projects start. ",
        "type": int,
        "min": 1900
    },
    "npa_year_end": {
        "label": "NPA end year",
        "config_path": ["npa", "npa_year_end"],
        "tooltip": "Year NPA projects end. After the year, the model assumes no more NPA projects are completed.",
        "type": int,
        "min": 1900
    },
    "npa_lifetime": {
        "label": "NPA lifetime (years)",
        "config_path": ["shared", "npa_lifetime"],
        "tooltip": "Depreciation lifetime for NPA expenses. Setting this to 0 would be the same as paying as operating expense rather than capital expense.",
        "type": int,
        "min": 0
    },
    "hp_efficiency": {
        "label": "HP efficiency",
        "config_path": ["electric", "hp_efficiency"],
        "tooltip": "Heat pump coefficient of performance (COP) - units of heat per unit of electricity. Used to estimate additional electric demand after conversion",
        "type": int,
        "min": 0
    },
    "water_heater_efficiency": {
        "label": "Water heater efficiency",
        "config_path": ["electric", "water_heater_efficiency"],
        "tooltip": "Water heater efficiency - units of heat per unit of electricity. Used to estimate additional electric demand after conversion",
        "type": int,
        "min": 0
    },
    "aircon_percent_adoption_pre_npa": {
        "label": "AC percent adoption pre-NPA",
        "config_path": ["npa", "aircon_percent_adoption_pre_npa"],
        "tooltip": "Percentage of households that already have air conditioning before NPA",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "peak_kw_summer_headroom": {
        "label": "Summer peak headroom (kW)",
        "config_path": ["npa", "peak_kw_summer_headroom"],
        "tooltip": "Peak headroom in summer for the grid feeding these households",
        "type": float,
        "min": 0
    },
    "peak_kw_winter_headroom": {
        "label": "Winter peak headroom (kW)",
        "config_path": ["npa", "peak_kw_winter_headroom"],
        "tooltip": "Peak headroom in winter for the grid feeding these households",
        "type": float,
        "min": 0
    }
}

ELECTRIC_INPUTS = {
    "electric_num_users_init": {
        "label": "Number of users",
        "config_path": ["electric", "num_users_init"],
        "tooltip": "Initial number of customers served by electric utility",
        "type": float,
        "min": 0
    },
    "scattershot_electrification_users_per_year": {
        "label": "Scattershot electrification users per year",
        "config_path": ["web_params", "scattershot_electrification_users_per_year"],
        "tooltip": "Number of customers who electrified each year, independent of NPAs. This increases overall electric demand and reduces the number of gas customers but has no impact on NPAs or grid upgrades. It is held constant in the BAU scenario.",
        "type": int,
        "min": 0
    },
    "baseline_non_npa_ratebase_growth": {
        "label": "Baseline non-NPA ratebase growth",
        "config_path": ["electric", "baseline_non_npa_ratebase_growth"],
        "tooltip": "Annual growth rate of utility ratebase excluding NPA investments",
        "type": float,
        "min": 0
    },
    "electric_default_depreciation_lifetime": {
        "label": "Electric default depreciation lifetime",
        "config_path": ["electric", "default_depreciation_lifetime"],
        "tooltip": "Default number of years over which electric utility assets are depreciated (excluding NPAs). Used to estimate depreciation for synthetic initial capex projects that would result in the initial ratebase.",
        "type": int,
        "min": 0
    },
    "electric_maintenance_cost_pct": {
        "label": "Electric maintenance cost (%)",
        "config_path": ["electric", "electric_maintenance_cost_pct"],
        "tooltip": "Annual maintenance costs as percentage of electric utility ratebase (excluding NPAs)",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "electricity_generation_cost_per_kwh_init": {
        "label": "Electricity generation cost per kWh",
        "config_path": ["electric", "electricity_generation_cost_per_kwh_init"],
        "tooltip": "Cost per kilowatt-hour of electricity generation in the initial year. This cost will grow annually by the cost inflation rate.",
        "type": float,
        "min": 0
    },
    "electric_ratebase_init": {
        "label": "Electric ratebase",
        "config_path": ["electric", "ratebase_init"],
        "tooltip": "Initial value of electric utility's ratebase (total assets)",
        "type": float,
        "min": 0
    },
    "electric_ror": {
        "label": "Rate of return (%)",
        "config_path": ["electric", "ror"],
        "tooltip": "Total rate of return, which is a combination of return on capital and return on debt for electric utility investments (after taxes)",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "electric_fixed_overhead_costs": {
        "label": "Electric fixed overhead costs",
        "config_path": ["web_params", "electric_fixed_overhead_costs"],
        "tooltip": "Fixed annual overhead costs for electric utility",
        "type": float,
        "min": 0
    },
    "electric_user_bill_fixed_charge": {
        "label": "Customer bill annual fixed charge ($)",
        "config_path": ["electric", "user_bill_fixed_charge"],
        "tooltip": "Annual fixed charge per customer ($)",
        "type": int,
        "min": 0
    },
    "grid_upgrade_depreciation_lifetime": {
        "label": "Grid upgrade depreciation lifetime (average)",
        "config_path": ["electric", "grid_upgrade_depreciation_lifetime"],
        "tooltip": "Average depreciation lifetime for grid infrastructure upgrades",
        "type": int,
        "min": 0
    },
    "per_user_electric_need_kwh": {
        "label": "Per user electric need (kWh)",
        "config_path": ["electric", "per_user_electric_need_kwh"],
        "tooltip": "Average annual electricity consumption per customer in kilowatt-hours",
        "type": float,
        "min": 0
    },
    "aircon_peak_kw": {
        "label": "AC peak kW",
        "config_path": ["electric", "aircon_peak_kw"],
        "tooltip": "Peak energy consumption of a household's new air conditioning unit. Used to estimate additional summer electric demand for converters without AC prior to NPA.",
        "type": float,
        "min": 0
    },
    "hp_peak_kw": {        
        "label": "Heat pump peak kW",
        "config_path": ["electric", "hp_peak_kw"],
        "tooltip": "Maximum electrical demand of new heat pump during peak operation",
        "type": float,
        "min": 0
    },
    "distribution_cost_per_peak_kw_increase_init": {
        "label": "Distribution cost per peak kW increase",
        "config_path": ["electric", "distribution_cost_per_peak_kw_increase_init"],
        "tooltip": "Cost to increase grid capacity by one kilowatt of peak demand. This cost will grow annually by the cost inflation rate.",
        "type": float,
        "min": 0
    }
}

GAS_INPUTS = {
    "gas_num_users_init": {
        "label": "Number of users",
        "config_path": ["gas", "num_users_init"],
        "tooltip": "Initial number of customers served by gas utility",
        "type": float,
        "min": 0
    },
    "gas_ratebase_init": {
        "label": "Gas ratebase",
        "config_path": ["gas", "ratebase_init"],
        "tooltip": "Initial value of gas utility's ratebase (total assets)",
        "type": float,
        "min": 0
    },
    "gas_ror": {
        "label": "Rate of return (%)",
        "config_path": ["gas", "ror"],
        "tooltip": "Total rate of return, which is a combination of return on capital and return on debt for gas utility investments (after taxes)",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "gas_fixed_overhead_costs": {
        "label": "Gas fixed overhead costs",
        "config_path": ["web_params", "gas_fixed_overhead_costs"],
        "tooltip": "Fixed annual overhead costs for gas utility. These costs will grow annually by the cost inflation rate.",
        "type": float,
        "min": 0
    },
    "gas_bau_lpp_costs_per_year": {
        "label": "Gas BAU pipeline replacement costs per year",
        "config_path": ["web_params", "gas_bau_lpp_costs_per_year"],
        "tooltip": "Gas pipeline replacement costs per year without any NPA projects (BAU). These costs will grow annually by the cost inflation rate.",
        "type": float,
        "min": 0
    },
    "baseline_non_lpp_ratebase_growth": {
        "label": "Baseline ratebase growth (excluding pipeline replacement programs)",
        "config_path": ["gas", "baseline_non_lpp_ratebase_growth"],
        "tooltip": "Baseline non-pipe replacement ratebase annual growth.",
        "type": float,
        "min": 0
    },
    "non_lpp_depreciation_lifetime": {
        "label": "Non-pipeline depreciation lifetime",
        "config_path": ["gas", "non_lpp_depreciation_lifetime"],
        "tooltip": "Depreciation lifetime for non-pipeline gas utility assets",
        "type": int,
        "min": 0
    },
    "gas_user_bill_fixed_charge": {
        "label": "Customer bill annual fixed charge ($)",
        "config_path": ["gas", "user_bill_fixed_charge"],
        "tooltip": "Annual fixed charge per customer ($)",
        "type": int,
        "min": 0
    },
    "gas_generation_cost_per_therm_init": {
        "label": "Gas commodity cost (per therm)",
        "config_path": ["gas", "gas_generation_cost_per_therm_init"],
        "tooltip": "Cost per therm of natural gas in the initial year. Used to estimate the variable costs of the gas utility. These costs will grow annually by the cost inflation rate.",
        "type": int,
        "min": 0
    },
    "per_user_heating_need_therms": {
        "label": "Per user heating need (therms)",
        "config_path": ["gas", "per_user_heating_need_therms"],
        "tooltip": "Average annual heating demand per customer in therms",
        "type": float,
        "min": 0
    },
    "per_user_water_heating_need_therms": {
        "label": "Per user water heating need (therms)",
        "config_path": ["gas", "per_user_water_heating_need_therms"],
        "tooltip": "Average annual water heating demand per customer in therms",
        "type": float,
        "min": 0
    }
}

FINANCIAL_INPUTS = {
    "cost_inflation_rate": {
        "label": "Cost inflation rate (%)",
        "config_path": ["shared", "cost_inflation_rate"],
        "tooltip": "Nominal annual growth rate applied to costs and expenses",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "construction_inflation_rate": {
        "label": "Construction inflation rate (%)",
        "config_path": ["shared", "construction_inflation_rate"],
        "tooltip": "Nominal annual growth rate applied to construction costs",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "real_dollar_discount_rate": {
        "label": "Inflation adjustment rate (%)",
        "config_path": ["shared", "real_dollar_discount_rate"],
        "tooltip": "Rate at which future costs and expenses are discounted to present results in today's dollars. Setting this to 0 will results in nominal values.",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "npv_discount_rate": {
        "label": "NPV discount rate (%)",
        "config_path": ["shared", "npv_discount_rate"],
        "tooltip": "Real discount rate for calculating net present value of capex projects (used for performance incentive scenario)",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "performance_incentive_pct": {
        "label": "Performance incentive percentage (%)",
        "config_path": ["shared", "performance_incentive_pct"],
        "tooltip": "Percentage of savings (avoided LPP spending) on which gas utility receives a performance incentive (used for performance incentive scenario)",
        "type": float,
        "min": 0,
        "max": 100,
        "is_pct": True
    },
    "incentive_payback_period": {
        "label": "Incentive payback period (years)",
        "config_path": ["shared", "incentive_payback_period"],
        "tooltip": "Number of years to pay incentives (used for performance incentive scenario)",
        "type": int,
        "min": 0
    }
}

SHARED_INPUTS = {
    "start_year": {
        "label": "Start year",
        "config_path": ["shared", "start_year"],
        "tooltip": "First year of the analysis period",
        "type": int,
        "min": 1900
    },
    "end_year": {
        "label": "End year",
        "config_path": ["shared", "end_year"],
        "tooltip": "Last year of the analysis period",
        "type": int,
        "min": 1900
    }
}

# Combine all mappings for the reactive update function
ALL_INPUT_MAPPINGS = {
    **PIPELINE_INPUTS,
    **ELECTRIC_INPUTS,
    **GAS_INPUTS,
    **FINANCIAL_INPUTS,
    **SHARED_INPUTS
}
