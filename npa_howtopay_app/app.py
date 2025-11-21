from typing import Any
import plotly.express as px
import polars as pl
from pathlib import Path
import tempfile
import io
import zipfile
from shinywidgets import output_widget, render_plotly
from shiny import App, reactive, render, ui, req
import npa_howtopay as nhp
import plotly.graph_objects as go
# Import from modules
from modules.config import load_all_configs, load_defaults, get_config_value
from modules.input_mappings import (
    PIPELINE_INPUTS, ELECTRIC_INPUTS, GAS_INPUTS, 
    FINANCIAL_INPUTS, SHARED_INPUTS, ALL_INPUT_MAPPINGS
)
from modules.plotting import plot_utility_metric, plot_total_bills_bar,  plot_total_bills_ts, switchbox_colors
from npa_howtopay.params import COMPARE_COLS
from ratelimit import debounce

css_file = Path(__file__).parent / "styles.css"
logo_file = Path(__file__).parent / "www" / "sb_logo.png"

# Load logo as base64
import base64
if logo_file.exists():
    with open(logo_file, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
        logo_src = f"data:image/png;base64,{logo_data}"
else:
    logo_src = ""

# Load configurations
all_configs = load_all_configs()
run_name_choices = {name: name for name in all_configs.keys()}
default_run_name = 'test_kiki'
config = load_defaults(default_run_name)

def coerce_input_value(value, input_id, from_ui=True):
    """
    Coerce input value to the correct type based on input_mappings.
    
    Args:
        value: The value to coerce
        input_id: The input ID from input_mappings
        from_ui: If True, value is from UI (0-100 for percentages) and will be converted to model format (0-1).
                If False, value is from config/model (0-1 for percentages) and will be converted to UI format (0-100).
    """
    if value is None:
        return None
    input_data = ALL_INPUT_MAPPINGS.get(input_id, {})
    input_type = input_data.get("type")
    is_pct = input_data.get("is_pct", False)
    
    # Handle percentage conversion
    if is_pct:
        if from_ui:
            # Convert from UI (0-100) to model (0-1)
            value = float(value) / 100.0
        else:
            # Convert from model (0-1) to UI (0-100)
            value = float(value) * 100.0
    
    if input_type is None:
        return value
    try:
        if input_type == int:
            return int(value)
        elif input_type == float:
            return float(value)
        else:
            return value
    except (ValueError, TypeError):
        return value

def create_input_with_tooltip(input_id):
    """Create numeric input with tooltip using input mappings"""
    input_data = ALL_INPUT_MAPPINGS[input_id]
    
    # Get initial value from config (config files now store percentages in 0-100 format)
    # For percentage fields, config is already in UI format (0-100), so no conversion needed
    # For non-percentage fields, just get the value as-is
    initial_value = get_config_value(config, input_data["config_path"])
    is_pct = input_data.get("is_pct", False)
    if not is_pct:
        # For non-percentage fields, apply type coercion only
        initial_value = coerce_input_value(initial_value, input_id, from_ui=True)
    else:
        # For percentage fields, config is already in 0-100 format (UI format), just coerce type
        input_type = input_data.get("type", float)
        if initial_value is not None:
            try:
                initial_value = float(initial_value) if input_type == float else int(initial_value)
            except (ValueError, TypeError):
                pass
    
    # Extract validation parameters
    min_value = input_data.get("min")
    max_value = input_data.get("max")
    input_type = input_data.get("type", float)
    
    # Set step based on type (1 for int, None/0.01 for float)
    step = 1 if input_type == int else None
    
    # Build input_numeric arguments
    input_kwargs = {
        "id": input_id,
        "label": input_data["label"],
        "value": initial_value,
        "update_on": "blur"
    }
    
    if min_value is not None:
        input_kwargs["min"] = min_value
    if max_value is not None:
        input_kwargs["max"] = max_value
    if step is not None:
        input_kwargs["step"] = step
    
    return ui.tooltip(
        ui.input_numeric(**input_kwargs),
        input_data["tooltip"]
    )

def create_styled_text(prefix_str: str, highlighted_str: str, suffix_str: str, highlight_color: str = '#FC9706'):
    """
    Create stylized text with highlighted portion colored to match #sb-carrot color.
    
    Args:
        prefix_str: Text that comes before the highlighted part
        highlighted_str: Text to be highlighted and colored
        suffix_str: Text that comes after the highlighted part
        
    Returns:
        List of UI components for inline display
    """
    from shiny import ui
    
    return ui.tags.span(
        prefix_str,
        ui.tags.span(
            highlighted_str,
            style=f"color: {highlight_color}; font-weight: bold;"
        ),
        suffix_str
    )

def app_ui(request):
    return ui.page_fluid(
ui.div(
  ui.div(
    ui.tags.a(
    ui.tags.img(src=logo_src, alt="Switchbox Logo", style="height: 40px; margin-right: 10px;"),
    href="https://www.switch.box/",
    target="_blank"
) if logo_src else None,
    ui.h1("NPA How to Pay", class_="app-title"),
    style="display: flex; align-items: center; gap: 10px;"
  ),
  ui.div(
    ui.download_button("download_data", "Download Data"),
  ),
  class_="app-header"
),
ui.page_sidebar(
  ui.sidebar(
    ui.card(
      ui.tooltip(
        ui.input_selectize("run_name", ui.h6("Select Default Settings"), choices=run_name_choices, selected=default_run_name),
        "Select a scenario to fill default parameter values for the entire simulation. You can always modify the values later. Any changes you have made will be lost when you change scenarios."
      ),
      ui.output_text("selected_description"),
      style="max-height: 20vh;"
    ),
    ui.card(
    ui.navset_tab(
      ui.nav_panel("NPA", ui.h4("NPA Projects"),
        # NPA Program inputs
        ui.output_ui("npa_year_range_slider"),
        create_input_with_tooltip("npa_install_costs_init"),
        create_input_with_tooltip("npa_projects_per_year"),
        create_input_with_tooltip("num_converts_per_project"),
        create_input_with_tooltip("npa_lifetime"),
        ui.h4("Project Energy Use Parameters"),
        create_input_with_tooltip("per_user_heating_need_therms"),
        create_input_with_tooltip("per_user_water_heating_need_therms"),
        ui.h4("Project Grid Parameters"),
        create_input_with_tooltip("peak_kw_summer_headroom"),
        create_input_with_tooltip("peak_kw_winter_headroom"),
        ui.h4("Project Appliance Parameters"),
        create_input_with_tooltip("hp_peak_kw"),
        create_input_with_tooltip("aircon_peak_kw"),
        create_input_with_tooltip("aircon_percent_adoption_pre_npa"),
        create_input_with_tooltip("hp_efficiency"),
        create_input_with_tooltip("water_heater_efficiency"),

        
      ),
      ui.nav_panel("Pipeline", ui.h4("Pipeline Economics"),
        # Pipeline Economics inputs
        create_input_with_tooltip("pipe_value_per_user"),
        # create_input_with_tooltip("pipeline_decomm_cost_per_user"),
        create_input_with_tooltip("pipeline_depreciation_lifetime"),
        create_input_with_tooltip("pipeline_maintenance_cost_pct"),
      ),
      ui.nav_panel("Electric", ui.h4("Electric Utility Financials"),
        create_input_with_tooltip("electric_num_users_init"),
        create_input_with_tooltip("per_user_electric_need_kwh"),
        create_input_with_tooltip("scattershot_electrification_users_per_year"),
        create_input_with_tooltip("electric_user_bill_fixed_charge"),
        create_input_with_tooltip("electric_ratebase_init"),
        # create_input_with_tooltip("baseline_non_npa_ratebase_growth"),
        create_input_with_tooltip("electric_ror"),
        # create_input_with_tooltip("electric_default_depreciation_lifetime"),
        create_input_with_tooltip("electric_fixed_overhead_costs"),
        create_input_with_tooltip("electric_maintenance_cost_pct"),
        # ui.h4("Electric Grid Parameters"),
        create_input_with_tooltip("electricity_generation_cost_per_kwh_init"),
        # create_input_with_tooltip("grid_upgrade_depreciation_lifetime"),
        

        create_input_with_tooltip("distribution_cost_per_peak_kw_increase_init"),
        ui.accordion(
            ui.accordion_panel(
                ui.strong("Advanced Settings"),
                create_input_with_tooltip("grid_upgrade_depreciation_lifetime"),
                create_input_with_tooltip("electric_default_depreciation_lifetime"),
                create_input_with_tooltip("baseline_non_npa_ratebase_growth"),
                value="elec_extra"
            ),
            open=False
        ),
      ),
      ui.nav_panel("Gas", ui.h4("Gas Utility Financials"),
        create_input_with_tooltip("gas_num_users_init"),
        create_input_with_tooltip("gas_user_bill_fixed_charge"),
        create_input_with_tooltip("gas_ratebase_init"),
        create_input_with_tooltip("gas_bau_lpp_costs_per_year"),
        # create_input_with_tooltip("baseline_non_lpp_ratebase_growth"),
        create_input_with_tooltip("gas_ror"),
        create_input_with_tooltip("gas_fixed_overhead_costs"),
        # create_input_with_tooltip("non_lpp_depreciation_lifetime"),
        create_input_with_tooltip("gas_generation_cost_per_therm_init"),
        ui.accordion(
            ui.accordion_panel(
                ui.strong("Advanced Settings"),
                create_input_with_tooltip("baseline_non_lpp_ratebase_growth"),
                create_input_with_tooltip("non_lpp_depreciation_lifetime"),
                value="gas_extra"
            ),
            open=False
        ),
        
      ),
      ui.nav_panel("Financials", ui.h4("Inflation"),
        # Financial inputs - you can reorder these as needed
        create_input_with_tooltip("cost_inflation_rate"),
        create_input_with_tooltip("construction_inflation_rate"),
        create_input_with_tooltip("real_dollar_discount_rate"),

      ),
      ui.nav_panel("Performance Incentive", ui.h4("Performance Incentive"),
        create_input_with_tooltip("npv_discount_rate"),
        create_input_with_tooltip("performance_incentive_pct"),
        create_input_with_tooltip("incentive_payback_period"),
      )
      ),
    style="overflow-y: auto; max-height: 65vh;"  # Move scroll styling here
    ),
  width="20%",
  # style="height: 95vh; overflow-y: auto; max-height: 100%;"
  ),
  ui.layout_columns(
    ui.card(
      ui.layout_columns(
        ui.p("Welcome to the NPA How to Pay app! This model explores the relative impact (magnitude and direction) of different NPA scenarios on utility financials and delivery bills. This is not a complete model of utility operations and we do not model supply side variables. The default view presents the results as a difference from the Business as Usual (BAU) scenario (See Scenario Descriptions below). For more information on the underlying model, see the",
        ui.tags.a(" NPA How to Pay documentation.", href="https://switchbox-data.github.io/npa-howtopay/", target="_blank"),
        ".", ui.br(),ui.br(), "Use the sidebar to select a scenario, this will populate default parameter values you can modify to fit your needs. Once you have input the values you want, click the Run Model button to run the model and plot the results."
    ),
      ),
      ui.layout_columns(
        # Start and end year inputs
        create_input_with_tooltip("start_year"),
        create_input_with_tooltip("end_year"),
        ui.tooltip(
        ui.input_switch("show_absolute", "Show Absolute Values", value=False),
        "Toggle between showing absolute values and deltas from BAU for utility metrics."# Customer bills are always shown as absolute values."
        ),
        col_widths={"sm": (5, 5, 2)}
      ),
        ui.accordion(
            ui.accordion_panel(
                ui.strong("Scenario Descriptions:"),
                ui.output_ui("scenario_definitions_table"),
                value="scenario_definitions"
            ),
            open=True
        ),

               ui.layout_columns(
        ui.input_action_button("calculate_btn", "Run Model", class_="btn-primary", width="100%", style="background-color: #023047; color: white; border-color: #023047;"),
        col_widths={"sm":(-8, 4)}
      ),
    ),
    ui.h3("Utility Metrics"),
        ui.card(
      ui.card_header("Utility Revenue Requirements"),
      ui.output_text("utility_revenue_reqs_chart_description"),
      output_widget("utility_revenue_reqs_chart"),
    ),
    ui.card(
      ui.card_header("Volumetric Tariff"),
      ui.output_text("volumetric_tariff_chart_description"),
      output_widget("volumetric_tariff_chart"),
    ),
    ui.card(
      ui.card_header("Ratebase"),
      ui.output_text("ratebase_chart_description"),
      output_widget("ratebase_chart"),
    ),
    ui.card(
      ui.card_header("Return on Ratebase as % of Revenue Requirement"),
      ui.output_text("return_component_chart_description"),
      output_widget("return_component_chart"),
    ),

    ui.h3("Average Household DeliveryBills"),
    ui.card(
      ui.card_header("Nonconverts"),
      ui.output_ui("nonconverts_bill_per_user_chart_description"),
      
      ui.layout_columns(
        ui.h6("Combined Annual Delivery Bills (Gas + Electric):"),
        ui.input_select("show_year_nonconverts", "Show bills in year:", 
        choices={}, 
        selected=None,
        ),
        col_widths={"sm": (8,4)}
        ),
      ui.layout_columns(
        output_widget("total_bills_chart_nonconverts"),
        output_widget("total_bills_chart_nonconverts_bar"),
        col_widths={"sm": (8,4)}
        ),
        ui.h6("By Utility Type:"),
        output_widget("nonconverts_bill_per_user_chart"),
        ),
        ui.card(
      ui.card_header("Converts"),
      ui.output_ui("converts_bill_per_user_chart_description"),
      
      ui.layout_columns(
        ui.h6("Combined Annual Delivery Bills (Gas + Electric):"),
        ui.input_select("show_year_converts", "Show bills in year:", 
        choices={}, 
        selected=None,
        ),
        col_widths={"sm": (8,4)}
        ),
      ui.layout_columns(
        output_widget("total_bills_chart_converts"),
        output_widget("total_bills_chart_converts_bar"),
        col_widths={"sm": (8,4)}
        ),
        ui.h6("By Utility Type:"),
        output_widget("converts_bill_per_user_chart"),
        ),

    # ui.card(
    #   ui.card_header("Converts"),
    #   ui.output_ui("converts_bill_per_user_chart_description"),
    #   output_widget("converts_bill_per_user_chart"),
    # ),

    col_widths={"sm": (12,12,6, 6, 6, 6, 12, 12, 12)},
  ),
  ui.include_css(css_file),
  # title="NPA How to Pay ",
),
)

def server(input, output, session):
    """Server function for the Shiny app."""

    # INSERT_YOUR_CODE
    @reactive.calc
    def lpp_hh():
        value = round(input.gas_bau_lpp_costs_per_year() / input.pipe_value_per_user())
        return f"{value:,}"

    @reactive.calc
    def reduced_lpp_costs_per_year():
        value = input.gas_bau_lpp_costs_per_year() - input.pipe_value_per_user()*input.npa_projects_per_year()*input.num_converts_per_project()
        return f"${int(value)/1e6:.0f}M"
    
    @reactive.calc
    def reduced_lpp_hh():
        reduced_costs = input.gas_bau_lpp_costs_per_year() - input.pipe_value_per_user()*input.npa_projects_per_year()*input.num_converts_per_project()
        value = round(reduced_costs / input.pipe_value_per_user())
        return f"{value:,}"

    @reactive.calc
    def npa_hh():
        value = input.npa_projects_per_year()*input.num_converts_per_project()
        return f"{value:,}"

    @reactive.calc
    def npa_costs_per_year():
        value = input.npa_install_costs_init()*input.npa_projects_per_year()*input.num_converts_per_project()
        return f"${int(value)/1e6:.0f}M"
    
    @reactive.calc
    def gas_bau_lpp_costs_per_year():
        value = input.gas_bau_lpp_costs_per_year()
        return f"${int(value)/1e6:.0f}M"

    @reactive.calc
    def lpp_savings_per_year():
        bau_costs = input.gas_bau_lpp_costs_per_year()
        reduced_costs = input.gas_bau_lpp_costs_per_year() - input.pipe_value_per_user()*input.npa_projects_per_year()*input.num_converts_per_project()
        value = int(bau_costs) - int(reduced_costs)
        return f"{value/1e6:.0f}M"

    @render.ui
    def scenario_definitions_table():
        """Render styled list of scenario definitions"""
        scenarios = [
            ("bau", "Business-as-usual (BAU):", f"No NPA projects, baseline utility costs and spending. Gas utility spends <strong>{gas_bau_lpp_costs_per_year()}</strong> in leak-prone pipe replacement per year, affecting <strong>{lpp_hh()}</strong> households. Investment is treated as gas capex, and added to their rate base and recovered over <strong>{input.pipeline_depreciation_lifetime()}</strong> years from the year the replacement is done. Scattershot electrification still occurs."),
            ('npa_program_desc', "Modeled NPA program:", f"Gas utility only spends <strong>{reduced_lpp_costs_per_year()}</strong> on pipeline replacement per year, for <strong>{reduced_lpp_hh()}</strong> households. The remaining <strong>{npa_hh()}</strong> get electrified instead (and their pipe is decommissioned), at a cost of <strong>{npa_costs_per_year()}</strong>. This would save <strong>${lpp_savings_per_year()}</strong> in avoided pipeline spending compared to business as usual. But who would pay for the <strong>{npa_costs_per_year()}</strong> in NPA costs? We model 6 possible scenarios, each with their own implications for ratepayers:"),
            ("gas_capex", "Gas Capex:", f"Gas utility pays for NPA projects as capital expenditures (added to gas ratebase and recovered over <strong>{input.npa_lifetime()}</strong> years from the year the project is done)."),
            ("gas_opex", "Gas Opex:", "Gas utility pays for NPA projects as operating expenses (not added to ratebase, recovered in year incurred)."),
            ("performance_incentive", "Performance Incentive:", f" Gas utilities would receive alternative compensation for engaging in NPAs: they would be allowed to treat a portion of the savings as capex, recovered over <strong>{input.incentive_payback_period()}</strong> years. Savings would be defined as the net-present-value of the difference between avoided BAU costs and NPA costs."),
            ("electric_capex", "Electric Capex:", f"Electric utility pays for NPA projects as capital expenditures (added to electric ratebase and recovered over <strong>{input.npa_lifetime()}</strong> years from the year the project is done)."),
            ("electric_opex", "Electric Opex:", "Electric utility pays for NPA projects as operating expenses (not added to ratebase, recovered in year incurred)."),

            ("taxpayer", "Taxpayer:", "All NPA costs are paid by public funds, not by utilities."),
        ]

        items = []
        for color_key, display_name, description in scenarios:
            color = switchbox_colors.get(color_key, '#000000')
            if color_key not in ['npa_program_desc', 'bau']:
                items.append(
                    ui.tags.p(
                        "     - ",
                        ui.tags.span(
                            display_name,
                            style=f"color: {color}; font-weight: bold;"
                        ),
                        " ",
                         ui.HTML(description)
                    )
                )
            else:
                items.append(
                    ui.tags.p(
                        ui.tags.span(
                            display_name,
                            style=f"color: {color}; font-weight: bold;"
                        ),
                        " ",
                        ui.HTML(description)
                    )
                )

        return ui.tags.div(*items)

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
                # Apply type coercion before updating
                # Config files now store percentages in 0-100 format (UI format), so no conversion needed
                is_pct = input_data.get("is_pct", False)
                if not is_pct:
                    value = coerce_input_value(value, input_id, from_ui=True)
                else:
                    # For percentage fields, config is already in 0-100 format, just coerce type
                    input_type = input_data.get("type", float)
                    if value is not None:
                        try:
                            value = float(value) if input_type == float else int(value)
                        except (ValueError, TypeError):
                            pass
                ui.update_numeric(input_id, value=value)
            except KeyError:
                pass  # Skip if path doesn't exist

    # Validate all inputs with min/max constraints
    @reactive.effect
    def validate_inputs():
        """Validate all inputs and reset invalid values to nearest valid value"""
        for input_id, input_data in ALL_INPUT_MAPPINGS.items():
            min_value = input_data.get("min")
            max_value = input_data.get("max")
            
            # Skip if no constraints
            if min_value is None and max_value is None:
                continue
            
            try:
                # Get current input value using getattr to safely access input
                input_attr = getattr(input, input_id, None)
                if input_attr is None:
                    continue
                    
                current_value = input_attr()
                
                # Skip if value is None
                if current_value is None:
                    continue
                
                # Check if value is out of bounds
                needs_reset = False
                new_value = current_value
                
                if min_value is not None and current_value < min_value:
                    new_value = min_value
                    needs_reset = True
                elif max_value is not None and current_value > max_value:
                    new_value = max_value
                    needs_reset = True
                
                # Reset if needed
                if needs_reset:
                    with reactive.isolate():
                        ui.update_numeric(input_id, value=new_value)
                        # Show notification using session
                        label = input_data.get("label", input_id)
                        if min_value is not None and max_value is not None:
                            session.notification.show(
                                f"'{label}' must be between {min_value} and {max_value}. Value reset to {new_value}.",
                                duration=3,
                                type="warning"
                            )
                        elif min_value is not None:
                            session.notification.show(
                                f"'{label}' must be at least {min_value}. Value reset to {min_value}.",
                                duration=3,
                                type="warning"
                            )
                        elif max_value is not None:
                            session.notification.show(
                                f"'{label}' must be at most {max_value}. Value reset to {max_value}.",
                                duration=3,
                                type="warning"
                            )
            except (AttributeError, TypeError, Exception):
                # Skip if input doesn't exist or can't be accessed
                pass
        
    # Update year dropdown choices when start_year, end_year, or config changes
    # Update year dropdown choices when start_year, end_year, or config changes
    @reactive.effect
    def update_year_choices():
        # This will trigger when current_config() changes
        config = current_config()
        start = coerce_input_value(input.start_year(), "start_year")
        end = coerce_input_value(input.end_year(), "end_year")
        if start and end:
            choices = {year: year for year in range(start, end + 1)}
            
            # Handle nonconverts dropdown independently
            current_selection_nonconverts = input.show_year_nonconverts()
            if current_selection_nonconverts is not None:
                try:
                    current_year = int(current_selection_nonconverts)
                    if start <= current_year <= end:
                        selected_nonconverts = current_year
                    else:
                        selected_nonconverts = end
                except (ValueError, TypeError):
                    selected_nonconverts = end
            else:
                selected_nonconverts = end
            
            # Handle converts dropdown independently
            current_selection_converts = input.show_year_converts()
            if current_selection_converts is not None:
                try:
                    current_year = int(current_selection_converts)
                    if start <= current_year <= end:
                        selected_converts = current_year
                    else:
                        selected_converts = end
                except (ValueError, TypeError):
                    selected_converts = end
            else:
                selected_converts = end
            
            # Update both dropdowns with same choices but independent selections
            ui.update_select("show_year_nonconverts", choices=choices, selected=selected_nonconverts)
            ui.update_select("show_year_converts", choices=choices, selected=selected_converts)

    
    
    @render.ui
    def npa_year_range_slider():
        start = coerce_input_value(input.start_year(), "start_year")
        end = coerce_input_value(input.end_year(), "end_year")
        default = [start, min(end, start + 10)]
        return ui.tooltip(
            ui.input_slider(
                "npa_year_range", 
                "NPA year range", 
                min=start, 
                max=end, 
                value=default,
                step=1,
                sep=""
            ),
            "Select the year range for the NPA projects, Default is to assume NPAs occur in the entire analysis period."
        )

    @debounce(1)  # 1000ms debounce delay
    @reactive.calc
    def debounced_npa_year_range():
        """Debounced version of npa_year_range to prevent model runs during dragging"""
        return input.npa_year_range()

    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_web_params():
        """Create the web parameters object for the model"""
        web_params = {
            "npa_num_projects": coerce_input_value(input.npa_projects_per_year(), "npa_projects_per_year"),
            "num_converts": coerce_input_value(input.num_converts_per_project(), "num_converts_per_project"),
            "pipe_value_per_user": coerce_input_value(input.pipe_value_per_user(), "pipe_value_per_user"),
            "pipe_decomm_cost_per_user": 0.0,
            "peak_kw_winter_headroom": coerce_input_value(input.peak_kw_winter_headroom(), "peak_kw_winter_headroom"),
            "peak_kw_summer_headroom": coerce_input_value(input.peak_kw_summer_headroom(), "peak_kw_summer_headroom"),
            "aircon_percent_adoption_pre_npa": coerce_input_value(input.aircon_percent_adoption_pre_npa(), "aircon_percent_adoption_pre_npa"),
            "scattershot_electrification_users_per_year": coerce_input_value(input.scattershot_electrification_users_per_year(), "scattershot_electrification_users_per_year"),
            "gas_fixed_overhead_costs": coerce_input_value(input.gas_fixed_overhead_costs(), "gas_fixed_overhead_costs"),
            "electric_fixed_overhead_costs": coerce_input_value(input.electric_fixed_overhead_costs(), "electric_fixed_overhead_costs"),
            "gas_bau_lpp_costs_per_year": coerce_input_value(input.gas_bau_lpp_costs_per_year(), "gas_bau_lpp_costs_per_year"),
            "npa_year_start": debounced_npa_year_range()[0],
            "npa_year_end": debounced_npa_year_range()[1],
            "is_scattershot": False,
        }
        return web_params
    
    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_gas_params():
        """Create the parameters object for the model"""
        gas_params = nhp.params.GasParams(
            baseline_non_lpp_ratebase_growth=coerce_input_value(input.baseline_non_lpp_ratebase_growth(), "baseline_non_lpp_ratebase_growth"),
            default_depreciation_lifetime=coerce_input_value(input.non_lpp_depreciation_lifetime(), "non_lpp_depreciation_lifetime"),
            pipeline_depreciation_lifetime=coerce_input_value(input.pipeline_depreciation_lifetime(), "pipeline_depreciation_lifetime"),
            non_lpp_depreciation_lifetime=coerce_input_value(input.non_lpp_depreciation_lifetime(), "non_lpp_depreciation_lifetime"),
            gas_generation_cost_per_therm_init=coerce_input_value(input.gas_generation_cost_per_therm_init(), "gas_generation_cost_per_therm_init"),
            num_users_init=coerce_input_value(input.gas_num_users_init(), "gas_num_users_init"),
            per_user_heating_need_therms=coerce_input_value(input.per_user_heating_need_therms(), "per_user_heating_need_therms"),
            per_user_water_heating_need_therms=coerce_input_value(input.per_user_water_heating_need_therms(), "per_user_water_heating_need_therms"),
            user_bill_fixed_charge=coerce_input_value(input.gas_user_bill_fixed_charge(), "gas_user_bill_fixed_charge"),
            pipeline_maintenance_cost_pct=coerce_input_value(input.pipeline_maintenance_cost_pct(), "pipeline_maintenance_cost_pct"),
            ratebase_init=coerce_input_value(input.gas_ratebase_init(), "gas_ratebase_init"),
            ror=coerce_input_value(input.gas_ror(), "gas_ror")
        )
        return gas_params
        
    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_electric_params():
        """Create the parameters object for the model"""
        electric_params = nhp.params.ElectricParams(
            aircon_peak_kw=coerce_input_value(input.aircon_peak_kw(), "aircon_peak_kw"),  # peak energy consumption of a household airconditioning unit
            baseline_non_npa_ratebase_growth=coerce_input_value(input.baseline_non_npa_ratebase_growth(), "baseline_non_npa_ratebase_growth"),
            default_depreciation_lifetime=coerce_input_value(input.electric_default_depreciation_lifetime(), "electric_default_depreciation_lifetime"),
            grid_upgrade_depreciation_lifetime=coerce_input_value(input.grid_upgrade_depreciation_lifetime(), "grid_upgrade_depreciation_lifetime"),
            distribution_cost_per_peak_kw_increase_init=coerce_input_value(input.distribution_cost_per_peak_kw_increase_init(), "distribution_cost_per_peak_kw_increase_init"),
            electric_maintenance_cost_pct=coerce_input_value(input.electric_maintenance_cost_pct(), "electric_maintenance_cost_pct"),
            electricity_generation_cost_per_kwh_init=coerce_input_value(input.electricity_generation_cost_per_kwh_init(), "electricity_generation_cost_per_kwh_init"),
            hp_efficiency=coerce_input_value(input.hp_efficiency(), "hp_efficiency"),
            water_heater_efficiency=coerce_input_value(input.water_heater_efficiency(), "water_heater_efficiency"),
            hp_peak_kw=coerce_input_value(input.hp_peak_kw(), "hp_peak_kw"),
            num_users_init=coerce_input_value(input.electric_num_users_init(), "electric_num_users_init"),
            per_user_electric_need_kwh=coerce_input_value(input.per_user_electric_need_kwh(), "per_user_electric_need_kwh"),
            ratebase_init=coerce_input_value(input.electric_ratebase_init(), "electric_ratebase_init"),
            user_bill_fixed_charge=coerce_input_value(input.electric_user_bill_fixed_charge(), "electric_user_bill_fixed_charge"),
            ror=coerce_input_value(input.electric_ror(), "electric_ror")
        )
        return electric_params

    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_shared_params():
        """Create the parameters object for the model"""
        shared_params = nhp.params.SharedParams(
            cost_inflation_rate=coerce_input_value(input.cost_inflation_rate(), "cost_inflation_rate"), 
            real_dollar_discount_rate=coerce_input_value(input.real_dollar_discount_rate(), "real_dollar_discount_rate"), 
            npv_discount_rate=coerce_input_value(input.npv_discount_rate(), "npv_discount_rate"),
            performance_incentive_pct=coerce_input_value(input.performance_incentive_pct(), "performance_incentive_pct"),
            incentive_payback_period=coerce_input_value(input.incentive_payback_period(), "incentive_payback_period"),
            construction_inflation_rate=coerce_input_value(input.construction_inflation_rate(), "construction_inflation_rate"),
            npa_install_costs_init=coerce_input_value(input.npa_install_costs_init(), "npa_install_costs_init"),
            npa_lifetime=coerce_input_value(input.npa_lifetime(), "npa_lifetime"), 
            start_year=coerce_input_value(input.start_year(), "start_year")
        )
        return shared_params
    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_input_params():
        """Create the parameters object for the model"""
        input_params = nhp.params.InputParams(
            gas=create_gas_params(),
            electric=create_electric_params(),
            shared=create_shared_params()
        )
        return input_params

    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_ts_inputs():
        """Create the time series inputs for the model"""
        web_params = create_web_params()
        start_year = coerce_input_value(input.start_year(), "start_year")
        end_year = coerce_input_value(input.end_year(), "end_year")
        return nhp.params.load_time_series_params_from_web_params(web_params, start_year, end_year+1)
    
    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def create_scenario_runs():
        """Create the scenario parameters for the model"""
        start_year = coerce_input_value(input.start_year(), "start_year")
        end_year = coerce_input_value(input.end_year(), "end_year")
        return nhp.model.create_scenario_runs(start_year, end_year+1, ["gas", "electric"], ["capex", "opex"])

    # MODEL FUNCTIONS

    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, ignore_none=False, ignore_init=False)
    def run_model():
        scenario_runs = create_scenario_runs()
        input_params = create_input_params()
        ts_params = create_ts_inputs()
        results_all = nhp.model.run_all_scenarios(scenario_runs, input_params, ts_params)
        
        return results_all

    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name, input.show_absolute, ignore_none=False, ignore_init=False)
    def return_delta_or_absolute_df():
        results_all = run_model()
        print("results_all type:", type(results_all))
        print("results_all keys:", results_all.keys() if isinstance(results_all, dict) else "Not a dict")
        
        # Check if input is available
        try:
            show_absolute = input.show_absolute()
            print(f"show_absolute value: {show_absolute}")
        except Exception as e:
            print(f"Error accessing show_absolute: {e}")
            show_absolute = False  # Default to False
        
        if show_absolute:
            print("Taking absolute path")

            combined_df = nhp.model.return_absolute_values_df(results_all, COMPARE_COLS)
            print("combined_df type:", type(combined_df))
            print("combined_df shape:", combined_df.shape)
            
        else:
            print("Taking delta path")
            combined_df = nhp.model.create_delta_df(results_all, COMPARE_COLS)
            print("combined_df type:", type(combined_df))
            print("combined_df shape:", combined_df.shape)
        
        return combined_df
    @reactive.calc
    @reactive.event(input.calculate_btn, input.run_name,  input.show_absolute, ignore_none=False, ignore_init=False)
    def prep_df_to_plot():
        combined_df = return_delta_or_absolute_df()
        
        plt_df = nhp.utils.transform_to_long_format(combined_df)
        print("Final plt_df type:", type(plt_df))
        print("Final plt_df shape:", plt_df.shape)
        print("Final plt_df columns:", plt_df.columns)
        return plt_df


 # PLOTTING FUNCTIONS  


    @render_plotly
    def utility_revenue_reqs_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="inflation_adjusted_revenue_requirement", 
            title="Utility Revenue Requirements",
            y_label_unit="$",
            y_label_title="Utility revenue requirement",
            show_absolute=input.show_absolute()
        )

    @render.text
    def utility_revenue_reqs_chart_description():
        if input.show_absolute():
            return f"Utility revenue requirements for gas and electric. These are the revenue requirements for the utility to cover its costs and expenses. All dollar values are inflation adjusted to {input.start_year()} dollars."
        else:
          return f"Difference in utility revenue requirements for gas and electric compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. These are the revenue requirements for the utility to cover its costs and expenses. All dollar values are inflation adjusted to {input.start_year()} dollars."

    @render_plotly
    def volumetric_tariff_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="variable_tariff",
            title="Volumetric Tariff",
            y_label_unit="$/unit",
            y_label_title="Volumetric tariff",
            show_absolute=input.show_absolute()
        )

    @render.text
    def volumetric_tariff_chart_description():
        if input.show_absolute():
            return f"Volumetric tariffs for gas (therms) and electric (kWh). All dollar values are inflation adjusted to {input.start_year()} dollars."
        else:
          return f"Difference in volumetric tariffs for gas (therms) and electric (kWh) compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. All dollar values are inflation adjusted to {input.start_year()} dollars."

    @render_plotly
    def ratebase_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="inflation_adjusted_ratebase",
            title="Ratebase",
            y_label_unit="$",
            y_label_title="Ratebase",
            show_absolute=input.show_absolute()
        )
    @render.text
    def ratebase_chart_description():
        if input.show_absolute():
            return f"Annual ratebase for gas and electric. All dollar values are inflation adjusted to {input.start_year()} dollars."
        else:
          return f"Difference in annual ratebase for gas and electric compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. All dollar values are inflation adjusted to {input.start_year()} dollars."

    @render_plotly
    def return_component_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="return_on_ratebase_pct",
            title="",
            y_label_unit="% of revenue requirement",
            y_label_title="Return component",
            show_absolute=input.show_absolute()
        )
    @render.text
    def return_component_chart_description():
        if input.show_absolute():
            return "Return on ratebase as a percentage of revenue requirement for gas and electric."
        else:
          return "Difference in return on ratebase as a percentage of revenue requirement (return component percent) for gas and electric compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. We subtract the BAU return component percent from the scenario return component percent to get the delta."

    @render_plotly
    def nonconverts_bill_per_user_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="nonconverts_bill_per_user",
            title="",
            y_label_unit="$",   
            y_label_title="Nonconverts annual delivery bill",
            show_absolute=input.show_absolute(),
            show_year=input.show_year_nonconverts()
        )
    @render.ui
    def nonconverts_bill_per_user_chart_description():
        if input.show_absolute():
            return ui.HTML(f"Nonconverts annual bills for gas and electric. All dollar values are inflation adjusted to {input.start_year()} dollars.")
        else:
          return create_styled_text(f"Difference in nonconverts annual bills for gas and electric ", f"relative to nonconverts bills in the Business as Usual (BAU) scenario", f" where no NPA projects are implemented. We do not consider changes to supply rates in any scenario so these should be considered as changes to the delivery portion of the bill. All dollar values are inflation adjusted to {input.start_year()} dollars.")

    @render_plotly
    def converts_bill_per_user_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="converts_bill_per_user",
            title="",
            y_label_unit="$",   
            y_label_title="Converts annual delivery bill",
            show_absolute=input.show_absolute(),
            show_year=2030
        )
    @render.ui
    def converts_bill_per_user_chart_description():
        if input.show_absolute():
          return ui.HTML(f"Converts annual bills for gas and electric. In the BAU scenario, converters would only be 'scattershot' electrified, meaning they electrified on their own with no NPA project. All dollar values are inflation adjusted to {input.start_year()} dollars.")
        else:
          return create_styled_text(f"Difference in average annual delivery bills (gas and electric) for converts after electrification ", f"relative to a non-converter in the same scenario",f". Because all converts have zero gas usage after the NPA project, the gas chart represents the avoided gas spending. The electric chart includes increased demand after electrification. We do not consider changes to supply rates in any scenario so these should be considered as changes to the delivery portion of the bill. All dollar values are inflation adjusted to {input.start_year()} dollars.")
    
    @render_plotly
    def total_bills_chart_nonconverts_bar():
        df = return_delta_or_absolute_df()
        req(not df.is_empty())  # Check that DataFrame is not empty
        req(input.show_year_nonconverts() is not None)  # Check that year selection is not None
        
        return plot_total_bills_bar(
            results_df=df.filter(pl.col("year") == int(input.show_year_nonconverts())), converts_nonconverts="nonconverts",           
            show_absolute=input.show_absolute(),
            y_label_title=f"Combined annual delivery bills in {input.show_year_nonconverts()}"
        )

    @render_plotly
    def total_bills_chart_nonconverts():
        df = return_delta_or_absolute_df()
        req(not df.is_empty())  # Check that DataFrame is not empty
        req(input.show_year_nonconverts() is not None)  # Check that year selection is not None
        

        return plot_total_bills_ts(
            df,converts_nonconverts="nonconverts",            
            y_label_title="Combined annual delivery bills",
            show_absolute=input.show_absolute(),
            show_year=input.show_year_nonconverts()

        )

    @render.text
    def total_bills_chart_description_nonconverts():
        if input.show_absolute():
            return f"Combined annual delivery bills (gas and electric) for converts and nonconverts. In the BAU scenario, converters would only be 'scattershot' electrified, meaning they electrified on their own with no NPA project. All dollar values are inflation adjusted to {input.start_year()} dollars."
        else:
          return f"Difference in annual combined delivery bills (gas and electric) nonconverts compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. All dollar values are inflation adjusted to {input.start_year()} dollars."
        
    @render_plotly
    def total_bills_chart_converts_bar():
        df = return_delta_or_absolute_df()
        req(not df.is_empty())  # Check that DataFrame is not empty
        req(input.show_year_converts() is not None)  # Check that year selection is not None
        
        return plot_total_bills_bar(
            results_df=df.filter(pl.col("year") == int(input.show_year_converts())), converts_nonconverts="converts",           
            show_absolute=input.show_absolute(),
            y_label_title=f"Combined annual delivery bills in {input.show_year_converts()}"
        )
    @render_plotly
    def total_bills_chart_converts():
        df = return_delta_or_absolute_df()
        req(not df.is_empty())  # Check that DataFrame is not empty
        req(input.show_year_converts() is not None)  # Check that year selection is not None
        

        return plot_total_bills_ts(
            df,converts_nonconverts="converts",            
            y_label_title="Combined annual delivery bills",
            show_absolute=input.show_absolute(),
            show_year=input.show_year_converts()
        )

    @render.text
    def total_bills_chart_description_converts():
        if input.show_absolute():
            return f"Combined annual delivery bills (gas and electric) for converts. In the BAU scenario, converters would only be 'scattershot' electrified, meaning they electrified on their own with no NPA project. All dollar values are inflation adjusted to {input.start_year()} dollars."
        else:
          return f"Difference in annual combined delivery bills (gas and electric) for converts after electrification relative to a non-converter in the same scenario. All dollar values are inflation adjusted to {input.start_year()} dollars."


    def collect_input_parameters():
        """Collect all current input parameter values into a Polars DataFrame"""
        parameters = []
        
        # Collect all inputs from ALL_INPUT_MAPPINGS
        for input_id, input_data in ALL_INPUT_MAPPINGS.items():
            try:
                # Get the input value using getattr
                input_attr = getattr(input, input_id, None)
                if input_attr is not None:
                    value = input_attr()
                    
                    # Convert None to empty string for CSV
                    if value is None:
                        value = ""
                    
                    # Get config path as string
                    config_path_str = " > ".join(input_data.get("config_path", []))
                    
                    parameters.append({
                        "parameter_name": input_id,
                        "label": input_data.get("label", input_id),
                        "value": value,
                        "type": str(input_data.get("type", "").__name__) if input_data.get("type") else "",
                        "config_path": config_path_str
                    })
            except (AttributeError, TypeError, Exception):
                # Skip if input doesn't exist or can't be accessed
                continue
        
        # Add metadata parameters
        try:
            parameters.append({
                "parameter_name": "run_name",
                "label": "Selected scenario/run name",
                "value": input.run_name(),
                "type": "str",
                "config_path": "metadata"
            })
        except Exception:
            pass
        
        try:
            npa_range = input.npa_year_range()
            if isinstance(npa_range, list):
                parameters.append({
                    "parameter_name": "npa_year_range",
                    "label": "NPA year range",
                    "value": f"{npa_range[0]}-{npa_range[1]}",
                    "type": "list",
                    "config_path": "metadata"
                })
        except Exception:
            pass
        
        # Create DataFrame
        if parameters:
            return pl.DataFrame(parameters)
        else:
            return pl.DataFrame({
                "parameter_name": [],
                "label": [],
                "value": [],
                "type": [],
                "config_path": []
            })

    @render.download(
        filename=lambda: f'{input.run_name()}_data.zip',
        media_type="application/zip"
    )
    def download_data():
        # Get results DataFrame
        df_to_download = return_delta_or_absolute_df()
        
        # Get parameters DataFrame
        params_df = collect_input_parameters()
        
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Write results CSV
            results_buffer = io.BytesIO()
            df_to_download.write_csv(results_buffer)
            results_buffer.seek(0)
            zip_file.writestr("results.csv", results_buffer.getvalue())
            
            # Write parameters CSV
            params_buffer = io.BytesIO()
            params_df.write_csv(params_buffer)
            params_buffer.seek(0)
            zip_file.writestr("parameters.csv", params_buffer.getvalue())
        
        zip_buffer.seek(0)
        
        # Yield the zip file content
        yield zip_buffer.getvalue()

    # Custom bookmark button handler
    @reactive.effect
    @reactive.event(input.custom_bookmark_btn)
    async def _():
        await session.bookmark()

    # Bookmark handler
    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)

    # User warnings
    @reactive.effect
    def check_npa_hh_warning():
        """Warn if NPA households per year exceeds initial gas users"""
        # Access inputs to establish reactive dependencies
        npa_projects = input.npa_projects_per_year()
        num_converts = input.num_converts_per_project()
        gas_users_init = input.gas_num_users_init()
        
        # Only check if all values are valid (not None)
        if (npa_projects is not None and num_converts is not None and gas_users_init is not None):
            npa_hh_per_year = npa_projects * num_converts
            
            if npa_hh_per_year > gas_users_init:
                ui.notification_show(
                    f"Warning: NPA households per year ({npa_hh_per_year:,.0f}) exceeds initial gas users ({gas_users_init:,.0f}). This may lead to unrealistic results.",
                    duration=10,
                    type="warning"
                )

app = App(app_ui, server, bookmark_store="url")