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

app_ui = ui.page_sidebar(
  ui.sidebar(
    ui.input_selectize("run_name", "Select Default Settings", choices=run_name_choices),
    ui.output_text("selected_description"),
    ui.navset_tab(
      ui.nav_panel("pipeline", ui.h2("Pipeline Economics"),
        ui.input_numeric("lpp_cost", "Pipeline Replacement Cost", value=config["npa"]["lpp_cost"]),
        ui.input_numeric("pipeline_depreciation_lifetime", "Pipeline Depreciation", value=config["gas"]["pipeline_depreciation_lifetime"]),
        ui.input_numeric("pipeline_maintenance_cost_pct", "Maintenance Cost (%)", value=config["gas"]["pipeline_maintenance_cost_pct"]),
        ui.h2("NPA Program"),
        ui.input_numeric("npa_install_costs_init", "NPA Cost per Household", value=config["shared"]["npa_install_costs_init"]),
        ui.input_numeric("npa_projects_per_year", "NPA Projects per Year", value=config["npa"]["npa_projects_per_year"]),
        ui.input_numeric("npa_lifetime", "NPA Lifetime (years)", value=config["shared"]["npa_lifetime"]),
        ui.input_numeric("hp_efficiency", "HP Efficiency", value=config["electric"]["hp_efficiency"]),
        ui.input_numeric("hp_peak_kw", "HP Peak kW", value=config["electric"]["hp_peak_kw"]),
      ),
      ui.nav_panel("electric", ui.h2("Electric Utility Financials"),
        ui.input_numeric("electric_num_users_init", "Number of Users", value=config["electric"]["num_users_init"]),
        ui.input_numeric("baseline_non_npa_ratebase_growth", "Baseline Ratebase growth (%)", value=config["electric"]["baseline_non_npa_ratebase_growth"]),
        ui.input_numeric("electric_default_depreciation_lifetime", "Depreciation Lifetime (years)", value=config["electric"]["default_depreciation_lifetime"]),
        ui.input_numeric("electric_maintenance_cost_pct", "Electric Maintenance Cost (%)", value=config["electric"]["electric_maintenance_cost_pct"]),
        ui.input_numeric("electricity_generation_cost_per_kwh_init", "Electricity Generation Cost per kWh", value=config["electric"]["electricity_generation_cost_per_kwh_init"]),
        ui.input_numeric("electric_ratebase_init", "Ratebase (dollars)", value=config["electric"]["ratebase_init"]),
        ui.input_numeric("ror", "Return on Capital (%)", value=config["electric"]["ror"]),
        ui.input_numeric("user_bill_fixed_cost_pct", "User Bill Fixed Cost (%)", value=config["electric"]["user_bill_fixed_cost_pct"]),
        ui.h2("Electric Grid Parameters"),
        ui.input_numeric("grid_upgrade_depreciation_lifetime", "Grid Upgrade Depreciation Lifetime (years)", value=config["electric"]["grid_upgrade_depreciation_lifetime"]),
        ui.input_numeric("per_user_electric_need_kwh", "Per User Electricity Need (kWh)", value=config["electric"]["per_user_electric_need_kwh"]),
        ui.input_numeric("distribution_cost_per_peak_kw_increase_init", "Distribution Cost per Peak kW Increase (dollars)", value=config["electric"]["distribution_cost_per_peak_kw_increase_init"]),
      ),
      ui.nav_panel("gas", ui.h2("Gas"),
      ui.input_numeric("gas_num_users_init", "Number of Users", value=config["gas"]["num_users_init"]),
      ui.input_numeric("gas_ratebase_init", "Ratebase (dollars)", value=config["gas"]["ratebase_init"]),
      ui.input_numeric("gas_ror", "Return on Capital (%)", value=config["gas"]["ror"]),
      ui.input_numeric("baseline_non_lpp_ratebase_growth", "Baseline Ratebase growth (%)", value=config["gas"]["baseline_non_lpp_ratebase_growth"]),
      ui.input_numeric("gas_default_depreciation_lifetime", "Depreciation Lifetime (years)", value=config["gas"]["default_depreciation_lifetime"]),
      ui.input_numeric("non_lpp_depreciation_lifetime", "Non-LPP Depreciation Lifetime (years)", value=config["gas"]["non_lpp_depreciation_lifetime"]),
      ui.input_numeric("gas_generation_cost_per_therm_init", "Gas Generation Cost per Therm", value=config["gas"]["gas_generation_cost_per_therm_init"]),
      ui.input_numeric("per_user_heating_need_therms", "Per User Heating Need (therms)", value=config["gas"]["per_user_heating_need_therms"]),
      ),
      ui.nav_panel("Financials", ui.h2("Inflation"),
      ui.input_numeric("cost_inflation_rate", "Cost Inflation (%)", value=config["shared"]["cost_inflation_rate"]),
      ui.input_numeric("discount_rate", "Discount Rate (%)", value=config["shared"]["discount_rate"]),
      ),
      ui.nav_panel("growth", ui.h1("Growth")
      )
    ),
  ),
  ui.layout_columns(
    ui.card(
      ui.layout_columns(
        ui.input_numeric("start_year", "Start Year", value=config["shared"]["start_year"]),
        ui.input_numeric("end_year", "End Year", value=config["shared"]["end_year"]),
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
    # Reactive configuration that updates when dropdown changes
    @reactive.calc
    def current_config():
        selected_run = input.run_name()
        return all_configs[selected_run]["config"]
    # Display the description of the selected run
    @render.text
    def selected_description():
        selected_run = input.run_name()
        return all_configs[selected_run]["description"]
    
    # Reactive configuration that updates when dropdown changes
    @reactive.calc
    def current_config():
        selected_run = input.run_name()
        return all_configs[selected_run]["config"]
    
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