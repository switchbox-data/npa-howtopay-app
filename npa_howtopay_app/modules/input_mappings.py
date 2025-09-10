"""Input mappings organized by UI sections with tooltips."""
PIPELINE_INPUTS = {
    # Pipeline Economics section
    "pipe_value_per_user": {
        "label": "Pipeline replacement cost",
        "config_path": ["npa", "pipe_value_per_user"],
        "tooltip": "Pipeline replacement cost per NPA household"
    },
    "pipeline_decomm_cost_per_user": {
        "label": "Pipeline decommissioning cost per household",
        "config_path": ["npa", "pipeline_decomm_cost_per_user"],
        "tooltip": "Pipeline decommissioning cost per NPA household"
    },
    "pipeline_depreciation_lifetime": {
        "label": "Pipeline depreciation",
        "config_path": ["gas", "pipeline_depreciation_lifetime"],
        "tooltip": "Number of years over which pipeline assets are depreciated for accounting purposes"
    },
    "pipeline_maintenance_cost_pct": {
        "label": "Maintenance cost (%)",
        "config_path": ["gas", "pipeline_maintenance_cost_pct"],
        "tooltip": "Annual maintenance costs as a percentage of total pipeline value"
    },
    # NPA Program section
    "npa_install_costs_init": {
        "label": "NPA cost per household",
        "config_path": ["shared", "npa_install_costs_init"],
        "tooltip": "Initial cost per household to install NPA equipment"
    },
    "npa_projects_per_year": {
        "label": "NPA projects per year",
        "config_path": ["npa", "npa_projects_per_year"],
        "tooltip": "Number of NPA projects completed annually. "
    },
    "num_converts_per_project": {
        "label": "Conversions per project",
        "config_path": ["npa", "num_converts_per_project"],
        "tooltip": "Number of household conversions included in each NPA project"
    },
    "npa_lifetime": {
        "label": "NPA lifetime (years)",
        "config_path": ["shared", "npa_lifetime"],
        "tooltip": "Expected operational lifetime of NPA equipment"
    },
    "hp_efficiency": {
        "label": "HP efficiency",
        "config_path": ["electric", "hp_efficiency"],
        "tooltip": "Heat pump coefficient of performance (COP) - units of heat per unit of electricity"
    },
    "aircon_percent_adoption_pre_npa": {
        "label": "Aircon percent adoption pre-NPA",
        "config_path": ["electric", "aircon_percent_adoption_pre_npa"],
        "tooltip": "Percentage of households that already have air conditioning before NPA"
    },
    "peak_kw_summer_headroom": {
        "label": "Summer peak headroom (kW)",
        "config_path": ["npa", "peak_kw_summer_headroom"],
        "tooltip": "Maximum electrical demand of heat pump during peak operation"
    },
    "peak_kw_winter_headroom": {
        "label": "Winter peak headroom (kW)",
        "config_path": ["npa", "peak_kw_winter_headroom"],
        "tooltip": "Maximum electrical demand of heat pump during peak operation"
    }
}

ELECTRIC_INPUTS = {
    "electric_num_users_init": {
        "label": "Number of users",
        "config_path": ["electric", "num_users_init"],
        "tooltip": "Initial number of customers served by electric utility"
    },
    "baseline_non_npa_ratebase_growth": {
        "label": "Baseline non-NPA ratebase growth",
        "config_path": ["electric", "baseline_non_npa_ratebase_growth"],
        "tooltip": "Annual growth rate of utility ratebase excluding NPA investments"
    },
    "electric_default_depreciation_lifetime": {
        "label": "Electric default depreciation lifetime",
        "config_path": ["electric", "default_depreciation_lifetime"],
        "tooltip": "Number of years over which electric utility assets are depreciated (exlcuding NPAs)"
    },
    "electric_maintenance_cost_pct": {
        "label": "Electric maintenance cost (%)",
        "config_path": ["electric", "electric_maintenance_cost_pct"],
        "tooltip": "Annual maintenance costs as percentage of electric utility ratebase (excluding NPAs)"
    },
    "electricity_generation_cost_per_kwh_init": {
        "label": "Electricity generation cost per kWh",
        "config_path": ["electric", "electricity_generation_cost_per_kwh_init"],
        "tooltip": "Cost per kilowatt-hour of electricity generation in the initial year"
    },
    "electric_ratebase_init": {
        "label": "Electric ratebase",
        "config_path": ["electric", "ratebase_init"],
        "tooltip": "Initial value of electric utility's ratebase (total assets)"
    },
    "electric_ror": {
        "label": "Rate on return (%)",
        "config_path": ["electric", "ror"],
        "tooltip": "Return on capital rate for electric utility investments"
    },
    "electric_fixed_overhead_costs": {
        "label": "Electric fixed overhead costs",
        "config_path": ["electric", "electric_fixed_overhead_costs"],
        "tooltip": "Fixed annual overhead costs for electric utility"
    },
    "user_bill_fixed_cost_pct": {
        "label": "User bill fixed cost (%)",
        "config_path": ["electric", "user_bill_fixed_cost_pct"],
        "tooltip": "Percentage of revenue requirement allocated as fixed costs on customer bills"
    },
    "grid_upgrade_depreciation_lifetime": {
        "label": "Grid upgrade depreciation lifetime",
        "config_path": ["electric", "grid_upgrade_depreciation_lifetime"],
        "tooltip": "Depreciation lifetime for grid infrastructure upgrades"
    },
    "per_user_electric_need_kwh": {
        "label": "Per user electric need (kWh)",
        "config_path": ["electric", "per_user_electric_need_kwh"],
        "tooltip": "Average annual electricity consumption per customer in kilowatt-hours"
    },
    "aircon_peak_kw": {
        "label": "Aircon peak kW",
        "config_path": ["electric", "aircon_peak_kw"],
        "tooltip": "Peak energy consumption of a household airconditioning unit"
    },
    "hp_peak_kw": {        
        "label": "HP peak kW",
        "config_path": ["electric", "hp_peak_kw"],
        "tooltip": "Maximum electrical demand of heat pump during peak operation"
    },
    "distribution_cost_per_peak_kw_increase_init": {
        "label": "Distribution cost per peak kW increase",
        "config_path": ["electric", "distribution_cost_per_peak_kw_increase_init"],
        "tooltip": "Cost to increase grid capacity by one kilowatt of peak demand"
    }
}

GAS_INPUTS = {
    "gas_num_users_init": {
        "label": "Number of users",
        "config_path": ["gas", "num_users_init"],
        "tooltip": "Initial number of customers served by gas utility"
    },
    "gas_ratebase_init": {
        "label": "Gas ratebase",
        "config_path": ["gas", "ratebase_init"],
        "tooltip": "Initial value of gas utility's ratebase (total assets)"
    },
    "gas_ror": {
        "label": "Rate on return (%)",
        "config_path": ["gas", "ror"],
        "tooltip": "Return on capital rate for gas utility investments"
    },
    "gas_fixed_overhead_costs": {
        "label": "Gas fixed overhead costs",
        "config_path": ["gas", "gas_fixed_overhead_costs"],
        "tooltip": "Fixed annual overhead costs for gas utility"
    },
    "gas_bau_lpp_costs_per_year": {
        "label": "Gas BAU pipeline replacement costs per year",
        "config_path": ["gas", "gas_bau_lpp_costs_per_year"],
        "tooltip": "Gas pipeline repacement costs per year without any NPA projects (BAU)"
    },
    "baseline_non_lpp_ratebase_growth": {
        "label": "Baseline non-LPP ratebase growth",
        "config_path": ["gas", "baseline_non_lpp_ratebase_growth"],
        "tooltip": "Annual growth rate of gas utility ratebase excluding pipeline replacements"
    },
    "non_lpp_depreciation_lifetime": {
        "label": "Non-pipeline depreciation lifetime",
        "config_path": ["gas", "non_lpp_depreciation_lifetime"],
        "tooltip": "Depreciation lifetime for non-pipeline gas utility assets"
    },
    "gas_generation_cost_per_therm_init": {
        "label": "Gas generation cost per therm",
        "config_path": ["gas", "gas_generation_cost_per_therm_init"],
        "tooltip": "Cost per therm of natural gas in the initial year"
    },
    "per_user_heating_need_therms": {
        "label": "Per user heating need (therms)",
        "config_path": ["gas", "per_user_heating_need_therms"],
        "tooltip": "Average annual heating demand per customer in therms"
    }
}

FINANCIAL_INPUTS = {
    "cost_inflation_rate": {
        "label": "Cost inflation rate (%)",
        "config_path": ["shared", "cost_inflation_rate"],
        "tooltip": "Annual inflation rate applied to costs and expenses"
    },
    "discount_rate": {
        "label": "Discount rate (%)",
        "config_path": ["shared", "discount_rate"],
        "tooltip": "Discount rate used for present value calculations"
    }
}

SHARED_INPUTS = {
    "start_year": {
        "label": "Start year",
        "config_path": ["shared", "start_year"],
        "tooltip": "First year of the analysis period"
    },
    "end_year": {
        "label": "End year",
        "config_path": ["shared", "end_year"],
        "tooltip": "Last year of the analysis period"
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
