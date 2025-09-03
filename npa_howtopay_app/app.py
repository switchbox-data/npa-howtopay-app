import plotly.express as px
import polars as pl
from pathlib import Path
from shinywidgets import output_widget, render_plotly
from shiny import App, reactive, render, ui

# Import from modules
from modules.config import load_all_configs, load_defaults, get_config_value
from modules.input_mappings import (
    PIPELINE_INPUTS, ELECTRIC_INPUTS, GAS_INPUTS, 
    FINANCIAL_INPUTS, SHARED_INPUTS, ALL_INPUT_MAPPINGS
)
from modules.plotting import plot_ratebase, plot_grid


css_file = Path(__file__).parent / "styles.css"
# Load configurations
all_configs = load_all_configs()
run_name_choices = {name: name for name in all_configs.keys()}
config = load_defaults()

def create_input_with_tooltip(input_id):
    """Create numeric input with tooltip using input mappings"""
    input_data = ALL_INPUT_MAPPINGS[input_id]
    return ui.tooltip(
        ui.input_numeric(input_id, input_data["label"], value=get_config_value(config, input_data["config_path"])),
        input_data["tooltip"]
    )

app_ui = app_ui = ui.page_fluid(
  ui.div(
    ui.h1("NPA How to Pay", class_="app-title"),
    class_="app-header"
  ),
ui.page_sidebar(
  ui.sidebar(
    ui.card(
      ui.tooltip(
        ui.input_selectize("run_name", ui.h6("Select Default Settings"), choices=run_name_choices, selected='sample'),
        "Select a scenario to fill default parameter values for the entire simulation. You can always modify the values later. Any changes you have made will be lost when you change scenarios."
      ),
      ui.output_text("selected_description"),
      style="max-height: 20vh;"
    ),
    ui.card(
    ui.navset_tab(
      ui.nav_panel("Pipeline", ui.h4("Pipeline Economics"),
        # Pipeline Economics inputs
        create_input_with_tooltip("lpp_cost"),
        create_input_with_tooltip("pipeline_depreciation_lifetime"),
        create_input_with_tooltip("pipeline_maintenance_cost_pct"),
        ui.h4("NPA Program"),
        # NPA Program inputs
        create_input_with_tooltip("npa_install_costs_init"),
        create_input_with_tooltip("npa_projects_per_year"),
        create_input_with_tooltip("num_converts_per_project"),
        create_input_with_tooltip("npa_lifetime"),
        create_input_with_tooltip("hp_efficiency"),
        create_input_with_tooltip("hp_peak_kw"),
      ),
      ui.nav_panel("Electric", ui.h4("Electric Utility Financials"),
        create_input_with_tooltip("electric_num_users_init"),
        create_input_with_tooltip("electric_ratebase_init"),
        create_input_with_tooltip("baseline_non_npa_ratebase_growth"),
        create_input_with_tooltip("ror"),
        create_input_with_tooltip("electric_default_depreciation_lifetime"),
        create_input_with_tooltip("user_bill_fixed_cost_pct"),
        create_input_with_tooltip("electric_maintenance_cost_pct"),
        ui.h4("Electric Grid Parameters"),
        create_input_with_tooltip("electricity_generation_cost_per_kwh_init"),
        create_input_with_tooltip("grid_upgrade_depreciation_lifetime"),
        create_input_with_tooltip("per_user_electric_need_kwh"),
        create_input_with_tooltip("distribution_cost_per_peak_kw_increase_init"),
      ),
      ui.nav_panel("Gas", ui.h4("Gas Utility Financials"),
        create_input_with_tooltip("gas_num_users_init"),
        create_input_with_tooltip("gas_ratebase_init"),
        create_input_with_tooltip("baseline_non_lpp_ratebase_growth"),
        create_input_with_tooltip("gas_ror"),
        create_input_with_tooltip("non_lpp_depreciation_lifetime"),
        create_input_with_tooltip("gas_generation_cost_per_therm_init"),
        create_input_with_tooltip("per_user_heating_need_therms"),
      ),
      ui.nav_panel("Financials", ui.h4("Inflation"),
        # Financial inputs - you can reorder these as needed
        create_input_with_tooltip("cost_inflation_rate"),
        create_input_with_tooltip("discount_rate"),
      ),
        ui.nav_panel("Growth", ui.h4("Growth"))
      ),
    style="overflow-y: auto; max-height: 65vh;"  # Move scroll styling here
    ),
  width="20%",
  # style="height: 95vh; overflow-y: auto; max-height: 100%;"
  ),
  ui.layout_columns(
    ui.card(
      ui.layout_columns(
        # Start and end year inputs
        create_input_with_tooltip("start_year"),
        create_input_with_tooltip("end_year"),
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
    col_widths={"sm": (12, 12, 6, 6, 6, 6)},
  ),
  ui.include_css(css_file),
  # title="NPA How to Pay ",
),
)

def server(input, output, session):
    """Server function for the Shiny app."""
    # REACTIVE INPUT HANDLING
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

    # REACTIVE DATA HANDLING
        # Reactive data preparation
    @reactive.calc
    def prepare_data():
        """Prepare the main DataFrame used across all charts"""
        start = input.start_year()
        end = input.end_year()
        years = list(range(start, end))

        # Electric utility
        electric_ratebase = float(input.electric_ratebase_init())
        electric_growth = float(input.baseline_non_npa_ratebase_growth())
        electric_list = [electric_ratebase]
        for year in range(start, end-1):
            electric_ratebase = electric_ratebase * (1 + electric_growth)
            electric_list.append(electric_ratebase)

        # Gas utility  
        gas_ratebase = float(input.gas_ratebase_init())
        gas_growth = float(input.baseline_non_lpp_ratebase_growth())
        gas_list = [gas_ratebase]
        for year in range(start, end-1):
            gas_ratebase = gas_ratebase * (1 + gas_growth)
            gas_list.append(gas_ratebase)

        # Create comprehensive DataFrame
        df = pl.DataFrame({
            'Year': pl.Series(years, dtype=pl.Int32),
            'Electric': pl.Series(electric_list, dtype=pl.Float64),
            'Gas': pl.Series(gas_list, dtype=pl.Float64),
        })
        
        return df
    
    @reactive.calc
    def prepare_data_grid():
        """Prepare the main DataFrame used across all charts"""
        start = input.start_year()
        end = input.end_year()
        years = list(range(start, end))


        # Create comprehensive DataFrame
        # Create comprehensive DataFrame
        df = pl.DataFrame({
            'year': pl.Series(years * 20, dtype=pl.Int32),
            'utility': pl.Series(['Gas'] * len(years) * 10 + ['Electric'] * len(years) * 10, dtype=pl.Utf8),
            'npa_status': pl.Series(['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years) + ['No NPA'] * len(years) + ['Converted'] * len(years), dtype=pl.Utf8),
            'delivery_charges': pl.Series([5] * len(years) + [8] * len(years) + [3] * len(years) + [6] * len(years) + [1] * len(years) + [4] * len(years) + [7] * len(years) + [10] * len(years) + [2] * len(years) + [9] * len(years) + [11] * len(years) + [14] * len(years) + [12] * len(years) + [15] * len(years) + [13] * len(years) + [16] * len(years) + [0] * len(years) + [17] * len(years) + [18] * len(years) + [21] * len(years), dtype=pl.Float64),
            'scenario': pl.Series(['Gas Opex'] * len(years) * 2 + ['Gas Capex'] * len(years) * 2 + ['Electric Opex'] * len(years) * 2 + ['Electric Capex'] * len(years) * 2 + ['Taxpayer'] * len(years) * 2 + ['Gas Opex'] * len(years) * 2 + ['Gas Capex'] * len(years) * 2 + ['Electric Opex'] * len(years) * 2 + ['Electric Capex'] * len(years) * 2 + ['Taxpayer'] * len(years) * 2, dtype=pl.Utf8),
        })
        
        return df

    @render_plotly
    def changes_to_hh_delivery_charges_chart():
        df = prepare_data_grid()
        return plot_grid(df)


    @render_plotly
    def utility_revenue_reqs_chart():

        df = prepare_data()
        
        return plot_ratebase(df)

    @render_plotly
    def volumetric_tariff_chart():
        df = prepare_data()
        
        return plot_ratebase(df)

    @render_plotly
    def ratebase_chart():
        df = prepare_data()
        
        return plot_ratebase(df)

    @render_plotly
    def depreciation_accruals_chart():
        df = prepare_data()
        
        return plot_ratebase(df)


app = App(app_ui, server)