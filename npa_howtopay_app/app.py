import plotly.express as px
from shinywidgets import output_widget, render_plotly
from shiny import App, reactive, render, ui

# Import from modules
from modules.config import load_all_configs, load_defaults, get_config_value
from modules.input_mappings import (
    PIPELINE_INPUTS, ELECTRIC_INPUTS, GAS_INPUTS, 
    FINANCIAL_INPUTS, SHARED_INPUTS, ALL_INPUT_MAPPINGS
)

# Load configurations
all_configs = load_all_configs()
run_name_choices = {name: name for name in all_configs.keys()}
config = load_defaults()

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
      ui.nav_panel("growth", ui.h1("Growth"))
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