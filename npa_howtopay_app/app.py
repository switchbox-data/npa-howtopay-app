import plotly.express as px
import yaml
from pathlib import Path

# Load data and compute static values 
# from shared import app_dir, tips
from shinywidgets import output_widget, render_plotly
from shiny import App, reactive, render, ui


def load_all_configs():
    """Load all YAML configuration files and return a dictionary."""
    configs = {}
    data_dir = Path(__file__).parent / "data"
    for yaml_file in data_dir.glob("*.yaml"):
        with open(yaml_file, 'r') as f:
            config_data = yaml.safe_load(f)
            run_name = config_data.get("run_name", yaml_file.stem)
            configs[run_name] = {
                "description": config_data.get("description", f"Configuration from {yaml_file.name}"),
                "config": config_data
            }
    return configs

all_configs = load_all_configs()
run_name_choices = {name: name for name in all_configs.keys()}  # Use run_name as both key and display value



# Load default values from YAML
def load_defaults():
    """Load default values from YAML configuration file."""
    config_path = Path(__file__).parent / "data" / "sample.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Load configuration
config = load_defaults()

# run_name_choices = {
#     yaml.safe_load(f.read())["run_name"]: yaml.safe_load(f.read())["description"]
#     for f in (Path(__file__).parent / "data").glob("*.yaml")
# }

# Group mappings by navset_tab panels
PIPELINE_INPUTS = {
    # Pipeline Economics section
    "lpp_cost": {
        "config_path": ["npa", "lpp_cost"],
        "tooltip": "Total cost to replace the pipeline infrastructure"
    },
    "pipeline_depreciation_lifetime": {
        "config_path": ["gas", "pipeline_depreciation_lifetime"],
        "tooltip": "Number of years over which pipeline assets are depreciated for accounting purposes"
    },
    "pipeline_maintenance_cost_pct": {
        "config_path": ["gas", "pipeline_maintenance_cost_pct"],
        "tooltip": "Annual maintenance costs as a percentage of total pipeline value"
    },
    # NPA Program section
    "npa_install_costs_init": {
        "config_path": ["shared", "npa_install_costs_init"],
        "tooltip": "Initial cost per household to install Non-Pipeline Alternative equipment"
    },
    "npa_projects_per_year": {
        "config_path": ["npa", "npa_projects_per_year"],
        "tooltip": "Number of NPA installations completed annually"
    },
    "npa_lifetime": {
        "config_path": ["shared", "npa_lifetime"],
        "tooltip": "Expected operational lifetime of NPA equipment in years"
    },
    "hp_efficiency": {
        "config_path": ["electric", "hp_efficiency"],
        "tooltip": "Heat pump coefficient of performance (COP) - units of heat per unit of electricity"
    },
    "hp_peak_kw": {
        "config_path": ["electric", "hp_peak_kw"],
        "tooltip": "Maximum electrical demand of heat pump during peak operation"
    }
}

ELECTRIC_INPUTS = {
    "electric_num_users_init": {
        "config_path": ["electric", "num_users_init"],
        "tooltip": "Initial number of customers served by electric utility"
    },
    "baseline_non_npa_ratebase_growth": {
        "config_path": ["electric", "baseline_non_npa_ratebase_growth"],
        "tooltip": "Annual growth rate of utility assets excluding NPA investments"
    },
    "electric_default_depreciation_lifetime": {
        "config_path": ["electric", "default_depreciation_lifetime"],
        "tooltip": "Number of years over which electric utility assets are depreciated"
    },
    "electric_maintenance_cost_pct": {
        "config_path": ["electric", "electric_maintenance_cost_pct"],
        "tooltip": "Annual maintenance costs as percentage of electric utility assets"
    },
    "electricity_generation_cost_per_kwh_init": {
        "config_path": ["electric", "electricity_generation_cost_per_kwh_init"],
        "tooltip": "Cost per kilowatt-hour of electricity generation in the initial year"
    },
    "electric_ratebase_init": {
        "config_path": ["electric", "ratebase_init"],
        "tooltip": "Initial value of electric utility's rate base (total assets)"
    },
    "ror": {
        "config_path": ["electric", "ror"],
        "tooltip": "Return on capital rate for electric utility investments"
    },
    "user_bill_fixed_cost_pct": {
        "config_path": ["electric", "user_bill_fixed_cost_pct"],
        "tooltip": "Percentage of revenue requirement allocated as fixed costs on customer bills"
    },
    "grid_upgrade_depreciation_lifetime": {
        "config_path": ["electric", "grid_upgrade_depreciation_lifetime"],
        "tooltip": "Depreciation lifetime for grid infrastructure upgrades"
    },
    "per_user_electric_need_kwh": {
        "config_path": ["electric", "per_user_electric_need_kwh"],
        "tooltip": "Annual electricity consumption per customer in kilowatt-hours"
    },
    "distribution_cost_per_peak_kw_increase_init": {
        "config_path": ["electric", "distribution_cost_per_peak_kw_increase_init"],
        "tooltip": "Cost to increase grid capacity by one kilowatt of peak demand"
    }
}

GAS_INPUTS = {
    "gas_num_users_init": {
        "config_path": ["gas", "num_users_init"],
        "tooltip": "Initial number of customers served by gas utility"
    },
    "gas_ratebase_init": {
        "config_path": ["gas", "ratebase_init"],
        "tooltip": "Initial value of gas utility's rate base (total assets)"
    },
    "gas_ror": {
        "config_path": ["gas", "ror"],
        "tooltip": "Return on capital rate for gas utility investments"
    },
    "baseline_non_lpp_ratebase_growth": {
        "config_path": ["gas", "baseline_non_lpp_ratebase_growth"],
        "tooltip": "Annual growth rate of gas utility assets excluding pipeline replacements"
    },
    "gas_default_depreciation_lifetime": {
        "config_path": ["gas", "default_depreciation_lifetime"],
        "tooltip": "Standard depreciation lifetime for gas utility assets"
    },
    "non_lpp_depreciation_lifetime": {
        "config_path": ["gas", "non_lpp_depreciation_lifetime"],
        "tooltip": "Depreciation lifetime for non-pipeline gas utility assets"
    },
    "gas_generation_cost_per_therm_init": {
        "config_path": ["gas", "gas_generation_cost_per_therm_init"],
        "tooltip": "Cost per therm of natural gas in the initial year"
    },
    "per_user_heating_need_therms": {
        "config_path": ["gas", "per_user_heating_need_therms"],
        "tooltip": "Annual heating demand per customer in therms"
    }
}

FINANCIAL_INPUTS = {
    "cost_inflation_rate": {
        "config_path": ["shared", "cost_inflation_rate"],
        "tooltip": "Annual inflation rate applied to costs and expenses"
    },
    "discount_rate": {
        "config_path": ["shared", "discount_rate"],
        "tooltip": "Discount rate used for present value calculations"
    }
}

SHARED_INPUTS = {
    "start_year": {
        "config_path": ["shared", "start_year"],
        "tooltip": "First year of the analysis period"
    },
    "end_year": {
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

# Helper functions
def get_config_value(config, path):
    """Get nested config value"""
    value = config
    for key in path:
        value = value[key]
    return value

def create_input_with_tooltip(input_id, label, value, tooltip):
    """Create numeric input with tooltip"""
    return ui.tooltip(
        ui.input_numeric(input_id, label, value=value),
        tooltip
    )

app_ui = ui.page_sidebar(
  ui.sidebar(
    ui.input_selectize("run_name", "Select Default Settings", choices=run_name_choices, selected='sample'),
    ui.output_text("selected_description"),
    ui.navset_tab(
      ui.nav_panel("pipeline", ui.h2("Pipeline Economics"),
        # Pipeline Economics inputs
        create_input_with_tooltip("lpp_cost", "Pipeline Replacement Cost", 
                                 get_config_value(config, PIPELINE_INPUTS["lpp_cost"]["config_path"]), 
                                 PIPELINE_INPUTS["lpp_cost"]["tooltip"]),
        create_input_with_tooltip("pipeline_depreciation_lifetime", "Pipeline Depreciation", 
                                 get_config_value(config, PIPELINE_INPUTS["pipeline_depreciation_lifetime"]["config_path"]), 
                                 PIPELINE_INPUTS["pipeline_depreciation_lifetime"]["tooltip"]),
        create_input_with_tooltip("pipeline_maintenance_cost_pct", "Maintenance Cost (%)", 
                                 get_config_value(config, PIPELINE_INPUTS["pipeline_maintenance_cost_pct"]["config_path"]), 
                                 PIPELINE_INPUTS["pipeline_maintenance_cost_pct"]["tooltip"]),
        ui.h2("NPA Program"),
        # NPA Program inputs
        create_input_with_tooltip("npa_install_costs_init", "NPA Cost per Household", 
                                 get_config_value(config, PIPELINE_INPUTS["npa_install_costs_init"]["config_path"]), 
                                 PIPELINE_INPUTS["npa_install_costs_init"]["tooltip"]),
        create_input_with_tooltip("npa_projects_per_year", "NPA Projects per Year", 
                                 get_config_value(config, PIPELINE_INPUTS["npa_projects_per_year"]["config_path"]), 
                                 PIPELINE_INPUTS["npa_projects_per_year"]["tooltip"]),
        create_input_with_tooltip("npa_lifetime", "NPA Lifetime (years)", 
                                 get_config_value(config, PIPELINE_INPUTS["npa_lifetime"]["config_path"]), 
                                 PIPELINE_INPUTS["npa_lifetime"]["tooltip"]),
        create_input_with_tooltip("hp_efficiency", "HP Efficiency", 
                                 get_config_value(config, PIPELINE_INPUTS["hp_efficiency"]["config_path"]), 
                                 PIPELINE_INPUTS["hp_efficiency"]["tooltip"]),
        create_input_with_tooltip("hp_peak_kw", "HP Peak kW", 
                                 get_config_value(config, PIPELINE_INPUTS["hp_peak_kw"]["config_path"]), 
                                 PIPELINE_INPUTS["hp_peak_kw"]["tooltip"]),
      ),
      ui.nav_panel("electric", ui.h2("Electric Utility Financials"),
        # Generate all electric inputs with tooltips
        *[create_input_with_tooltip(input_id, 
                                   # Convert input_id to readable label
                                   input_id.replace('_', ' ').title().replace('Init', '').replace('Pct', '(%)').replace('Kwh', 'kWh').replace('Kw', 'kW'),
                                   get_config_value(config, input_data["config_path"]), 
                                   input_data["tooltip"]) 
          for input_id, input_data in ELECTRIC_INPUTS.items()],
      ),
      ui.nav_panel("gas", ui.h2("Gas"),
        # Generate all gas inputs with tooltips
        *[create_input_with_tooltip(input_id, 
                                   input_id.replace('_', ' ').title().replace('Init', '').replace('Pct', '(%)').replace('Lpp', 'LPP'),
                                   get_config_value(config, input_data["config_path"]), 
                                   input_data["tooltip"]) 
          for input_id, input_data in GAS_INPUTS.items()],
      ),
      ui.nav_panel("Financials", ui.h2("Inflation"),
        # Generate financial inputs with tooltips
        *[create_input_with_tooltip(input_id, 
                                   input_id.replace('_', ' ').title().replace('Pct', '(%)'),
                                   get_config_value(config, input_data["config_path"]), 
                                   input_data["tooltip"]) 
          for input_id, input_data in FINANCIAL_INPUTS.items()],
      ),
      ui.nav_panel("growth", ui.h1("Growth")
      )
    ),
  ),
  ui.layout_columns(
    ui.card(
      ui.layout_columns(
        # Shared inputs with tooltips
        *[create_input_with_tooltip(input_id, 
                                   input_id.replace('_', ' ').title(),
                                   get_config_value(config, input_data["config_path"]), 
                                   input_data["tooltip"]) 
          for input_id, input_data in SHARED_INPUTS.items()],
        col_widths={"sm": (6, 6)}
      ),
    ),
    ui.card(
      ui.card_header("Changes to Average Household Delivery Charges"),
      output_widget("changes_to_hh_delivery_charges_chart"),
    ),
    ui.card(
      ui.card_header("Utility Revenue Requirements"),
      output_widget("utility_revenue_reqs_chart"),
    ),
    ui.card(
      ui.card_header("Volumetric Tariff"),
      output_widget("volumetric_tariff_chart"),
    ),
    ui.card(
      ui.card_header("Ratebase"),
      output_widget("ratebase_chart"),
    ),
    ui.card(
      ui.card_header("Depreciation Accruals"),
      output_widget("depreciation_accruals_chart"),
    ),
    col_widths={"sm": (12, 6, 6, 6, 6)},
  ),
)

def server(input, output, session):
    """Server function for the Shiny app."""
    
    @reactive.calc
    def current_config():
        selected_run = input.run_name()
        return all_configs[selected_run]["config"]
    
    @render.text
    def selected_description():
        selected_run = input.run_name()
        return all_configs[selected_run]["description"]
    
    # Update all inputs when config changes
    @reactive.effect
    def update_all_inputs():
        config = current_config()
        
        # Update all inputs using the combined mapping
        for input_id, input_data in ALL_INPUT_MAPPINGS.items():
            try:
                config_path = input_data["config_path"]
                value = config
                for key in config_path:
                    value = value[key]
                ui.update_numeric(input_id, value=value)
            except KeyError:
                pass  # Skip if path doesn't exist
    
    @render_plotly
    def changes_to_hh_delivery_charges_chart():
        start = input.start_year()
        end = input.end_year()

        ratebase = input.electric_ratebase_init()
        ratebase_growth = input.baseline_non_npa_ratebase_growth()
        ratebase_list = [ratebase]
        for year in range(start, end-1):
            ratebase = ratebase * (1 + ratebase_growth)
            ratebase_list.append(ratebase)
        return px.line(x=list(range(start, end)), y=ratebase_list, title="Ratebase")

    @render_plotly
    def utility_revenue_reqs_chart():
        start = 2025
        end = 2050

        ratebase = input.electric_ratebase_init()
        ratebase_growth = input.baseline_non_npa_ratebase_growth()
        ratebase_list = [ratebase]
        for year in range(start, end-1):
            ratebase = ratebase * (1 + ratebase_growth)
            ratebase_list.append(ratebase)
        return px.line(x=list(range(start, end)), y=ratebase_list, title="Ratebase")

    @render_plotly
    def volumetric_tariff_chart():
        start = 2025
        end = 2050

        ratebase = input.electric_ratebase_init()
        ratebase_growth = input.baseline_non_npa_ratebase_growth()
        ratebase_list = [ratebase]
        for year in range(start, end-1):
            ratebase = ratebase * (1 + ratebase_growth)
            ratebase_list.append(ratebase)
        return px.line(x=list(range(start, end)), y=ratebase_list, title="Ratebase")

    @render_plotly
    def ratebase_chart():
        start = 2025
        end = 2050

        ratebase = input.electric_ratebase_init()
        ratebase_growth = input.baseline_non_npa_ratebase_growth()
        ratebase_list = [ratebase]
        for year in range(start, end-1):
            ratebase = ratebase * (1 + ratebase_growth)
            ratebase_list.append(ratebase)
        return px.line(x=list(range(start, end)), y=ratebase_list, title="Ratebase")

    @render_plotly
    def depreciation_accruals_chart():
        start = 2025
        end = 2050

        ratebase = input.electric_ratebase_init()
        ratebase_growth = input.baseline_non_npa_ratebase_growth()
        ratebase_list = [ratebase]
        for year in range(start, end-1):
            ratebase = ratebase * (1 + ratebase_growth)
            ratebase_list.append(ratebase)
        return px.line(x=list(range(start, end)), y=ratebase_list, title="Ratebase")


app = App(app_ui, server)