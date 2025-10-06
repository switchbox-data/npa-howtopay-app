import plotly.express as px
import polars as pl
from pathlib import Path
import tempfile
import io
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
from modules.plotting import plot_utility_metric,  plot_total_bills
from npa_howtopay.params import COMPARE_COLS

css_file = Path(__file__).parent / "styles.css"
# Load configurations
all_configs = load_all_configs()
run_name_choices = {name: name for name in all_configs.keys()}
default_run_name = 'test_kiki'
config = load_defaults(default_run_name)

def create_input_with_tooltip(input_id):
    """Create numeric input with tooltip using input mappings"""
    input_data = ALL_INPUT_MAPPINGS[input_id]
    return ui.tooltip(
        ui.input_numeric(input_id, input_data["label"], value=get_config_value(config, input_data["config_path"])),
        input_data["tooltip"]
    )

def app_ui(request):
    return ui.page_fluid(
ui.div(
  ui.h1("NPA How to Pay", class_="app-title"),
  ui.div(
    ui.download_button("download_data", "Download Data"),
    ui.input_bookmark_button("Bookmark Current Scenario", icon=None,  id="custom_bookmark_btn"),
    class_="button-group"
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
        create_input_with_tooltip("npa_install_costs_init"),
        create_input_with_tooltip("npa_projects_per_year"),
        create_input_with_tooltip("num_converts_per_project"),
        create_input_with_tooltip("npa_lifetime"),
        ui.h4("Project Grid Parameters"),
        create_input_with_tooltip("peak_kw_summer_headroom"),
        create_input_with_tooltip("peak_kw_winter_headroom"),
        ui.h4("Project Appliance Parameters"),
        create_input_with_tooltip("hp_peak_kw"),
        create_input_with_tooltip("aircon_peak_kw"),
        create_input_with_tooltip("aircon_percent_adoption_pre_npa"),
        create_input_with_tooltip("hp_efficiency"),
        create_input_with_tooltip("water_heater_efficiency"),
        ui.h4("Project Energy Use Parameters"),
        create_input_with_tooltip("per_user_heating_need_therms"),
        create_input_with_tooltip("per_user_water_heating_need_therms"),
      ),
      ui.nav_panel("Pipeline", ui.h4("Pipeline Economics"),
        # Pipeline Economics inputs
        create_input_with_tooltip("pipe_value_per_user"),
        # create_input_with_tooltip("pipeline_decomm_cost_per_user"),
        create_input_with_tooltip("pipeline_depreciation_lifetime"),
        create_input_with_tooltip("pipeline_maintenance_cost_pct"),
        create_input_with_tooltip("gas_bau_lpp_costs_per_year"),
      ),
      ui.nav_panel("Electric", ui.h4("Electric Utility Financials"),
        create_input_with_tooltip("electric_num_users_init"),
        create_input_with_tooltip("scattershot_electrification_users_per_year"),
        create_input_with_tooltip("electric_user_bill_fixed_charge"),
        create_input_with_tooltip("electric_ratebase_init"),
        create_input_with_tooltip("baseline_non_npa_ratebase_growth"),
        create_input_with_tooltip("electric_ror"),
        create_input_with_tooltip("electric_default_depreciation_lifetime"),
        create_input_with_tooltip("electric_fixed_overhead_costs"),
        create_input_with_tooltip("electric_maintenance_cost_pct"),
        ui.h4("Electric Grid Parameters"),
        create_input_with_tooltip("electricity_generation_cost_per_kwh_init"),
        create_input_with_tooltip("grid_upgrade_depreciation_lifetime"),
        create_input_with_tooltip("per_user_electric_need_kwh"),

        create_input_with_tooltip("distribution_cost_per_peak_kw_increase_init"),
      ),
      ui.nav_panel("Gas", ui.h4("Gas Utility Financials"),
        create_input_with_tooltip("gas_num_users_init"),
        create_input_with_tooltip("gas_user_bill_fixed_charge"),
        create_input_with_tooltip("gas_ratebase_init"),
        create_input_with_tooltip("baseline_non_lpp_ratebase_growth"),
        create_input_with_tooltip("gas_ror"),
        create_input_with_tooltip("gas_fixed_overhead_costs"),
        create_input_with_tooltip("non_lpp_depreciation_lifetime"),
        create_input_with_tooltip("gas_generation_cost_per_therm_init"),
        
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
        ui.p("Welcome to the NPA How to Pay app! Use the sidebar to select a scenario, this will populate default parameter values you can modify to fit your needs. The app will then run the model and plot the results. For more information on the underlying model, see the",
        ui.tags.a(" NPA How to Pay documentation.", href="https://switchbox-data.github.io/npa-howtopay/", target="_blank"),
        "."
    ),
      ),
      ui.layout_columns(
        # Start and end year inputs
        create_input_with_tooltip("start_year"),
        create_input_with_tooltip("end_year"),
        ui.tooltip(
        ui.input_switch("show_absolute", "Show Absolute Values", value=False),
        "Toggle between showing absolute values and deltas from BAU."
        ),
        col_widths={"sm": (5, 5, 2)}
      ),
    #   ui.layout_columns(
    #     ui.download_button("download_data", "Download Data", width="25%"),
    #     col_widths={"sm": (-7, 5)}
    # ),
    ),
    ui.card(
      ui.card_header("Combined Delivery Bills"),
      ui.output_text("total_bills_chart_description"),
      output_widget("total_bills_chart"),
    ),
    ui.card(
      ui.card_header("Average Household Delivery Bills"),
      ui.h6("Nonconverts"),
      ui.output_text("nonconverts_bill_per_user_chart_description"),
      output_widget("nonconverts_bill_per_user_chart"),
      ui.h6("Converts"),
      ui.output_text("converts_bill_per_user_chart_description"),
      output_widget("converts_bill_per_user_chart"),
    ),

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
    col_widths={"sm": (12, 12,12, 6, 6, 6, 6)},
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
    
    @reactive.calc
    def create_web_params():
        """Create the web parameters object for the model"""
        web_params = {
            "npa_num_projects": input.npa_projects_per_year(),
            "num_converts": input.num_converts_per_project(),
            "pipe_value_per_user": float(input.pipe_value_per_user()),
            "pipe_decomm_cost_per_user": 0.0,
            "peak_kw_winter_headroom": float(input.peak_kw_winter_headroom()),
            "peak_kw_summer_headroom": float(input.peak_kw_summer_headroom()),
            "aircon_percent_adoption_pre_npa": input.aircon_percent_adoption_pre_npa(),
            "scattershot_electrification_users_per_year": input.scattershot_electrification_users_per_year(),
            "gas_fixed_overhead_costs": input.gas_fixed_overhead_costs(),
            "electric_fixed_overhead_costs": input.electric_fixed_overhead_costs(),
            "gas_bau_lpp_costs_per_year": input.gas_bau_lpp_costs_per_year(),
            "is_scattershot": False,
        }


        return web_params
    
    @reactive.calc
    def create_gas_params():
        """Create the parameters object for the model"""
        gas_params = nhp.params.GasParams(
            baseline_non_lpp_ratebase_growth=input.baseline_non_lpp_ratebase_growth(),
            default_depreciation_lifetime=input.non_lpp_depreciation_lifetime(),
            pipeline_depreciation_lifetime=input.pipeline_depreciation_lifetime(),
            non_lpp_depreciation_lifetime=input.non_lpp_depreciation_lifetime(),
            gas_generation_cost_per_therm_init=input.gas_generation_cost_per_therm_init(),
            num_users_init=input.gas_num_users_init(),
            per_user_heating_need_therms=input.per_user_heating_need_therms(),
            per_user_water_heating_need_therms=input.per_user_water_heating_need_therms(),
            user_bill_fixed_charge=input.gas_user_bill_fixed_charge(),
            pipeline_maintenance_cost_pct=input.pipeline_maintenance_cost_pct(),
            ratebase_init=input.gas_ratebase_init(),
            ror=input.gas_ror()
        )
        return gas_params
        
    @reactive.calc
    def create_electric_params():
        """Create the parameters object for the model"""
        electric_params = nhp.params.ElectricParams(
            aircon_peak_kw=input.aircon_peak_kw(),  # peak energy consumption of a household airconditioning unit
            baseline_non_npa_ratebase_growth=input.baseline_non_npa_ratebase_growth(),
            default_depreciation_lifetime=input.electric_default_depreciation_lifetime(),
            grid_upgrade_depreciation_lifetime=input.grid_upgrade_depreciation_lifetime(),
            distribution_cost_per_peak_kw_increase_init=input.distribution_cost_per_peak_kw_increase_init(),
            electric_maintenance_cost_pct=input.electric_maintenance_cost_pct(),
            electricity_generation_cost_per_kwh_init=input.electricity_generation_cost_per_kwh_init(),
            hp_efficiency=input.hp_efficiency(),
            water_heater_efficiency=input.water_heater_efficiency(),
            hp_peak_kw=input.hp_peak_kw(),
            num_users_init=input.electric_num_users_init(),
            per_user_electric_need_kwh=input.per_user_electric_need_kwh(),
            ratebase_init=input.electric_ratebase_init(),
            user_bill_fixed_charge=input.electric_user_bill_fixed_charge(),
            ror=input.electric_ror()
        )
        return electric_params

    @reactive.calc
    def create_shared_params():
        """Create the parameters object for the model"""
        shared_params = nhp.params.SharedParams(
          cost_inflation_rate=input.cost_inflation_rate(), 
          real_dollar_discount_rate=input.real_dollar_discount_rate(), 
          npv_discount_rate=input.npv_discount_rate(),
          performance_incentive_pct=input.performance_incentive_pct(),
          incentive_payback_period=input.incentive_payback_period(),
          construction_inflation_rate=input.construction_inflation_rate(),
          npa_install_costs_init=input.npa_install_costs_init(),
          npa_lifetime=input.npa_lifetime(), 
          start_year=input.start_year())

        
        return shared_params
    @reactive.calc
    def create_input_params():
        """Create the parameters object for the model"""
        input_params = nhp.params.InputParams(
            gas=create_gas_params(),
            electric=create_electric_params(),
            shared=create_shared_params()
        )
        return input_params

    @reactive.calc
    def create_ts_inputs():
        """Create the time series inputs for the model"""
        web_params = create_web_params()
        return nhp.params.load_time_series_params_from_web_params(web_params, input.start_year(), input.end_year())
    
    @reactive.calc
    def create_scenario_runs():
        """Create the scenario parameters for the model"""
        return nhp.model.create_scenario_runs(input.start_year(), input.end_year(), ["gas", "electric"], ["capex", "opex"])

    # MODEL FUNCTIONS

    @reactive.calc
    def run_model():
        scenario_runs = create_scenario_runs()
        input_params = create_input_params()
        ts_params = create_ts_inputs()
        results_all = nhp.model.run_all_scenarios(scenario_runs, input_params, ts_params)
        
        return results_all

    @reactive.calc
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

            combined_df = nhp.model.return_absolute_values_df(results_all)
            print("combined_df type:", type(combined_df))
            print("combined_df shape:", combined_df.shape)
            
        else:
            print("Taking delta path")
            combined_df = nhp.model.create_delta_df(results_all, COMPARE_COLS)
            print("combined_df type:", type(combined_df))
            print("combined_df shape:", combined_df.shape)
        
        return combined_df
    @reactive.calc
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
            show_absolute=input.show_absolute()
        )

    @render.text
    def utility_revenue_reqs_chart_description():
        if input.show_absolute():
            return "Utility revenue requirements for gas and electric. These are the revenue requirements for the utility to cover its costs and expenses."
        else:
          return "Difference in utility revenue requirements for gas and electric compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. These are the revenue requirements for the utility to cover its costs and expenses."

    @render_plotly
    def volumetric_tariff_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="variable_tariff",
            title="Volumetric Tariff",
            y_label_unit="$/unit",
            show_absolute=input.show_absolute()
        )

    @render.text
    def volumetric_tariff_chart_description():
        if input.show_absolute():
            return "Volumetric tariffs for gas (therms) and electric (kWh)."
        else:
          return "Difference in volumetric tariffs for gas (therms) and electric (kWh) compared to the Business as Usual (BAU) scenario where no NPA projects are implemented."

    @render_plotly
    def ratebase_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="ratebase",
            title="Ratebase",
            y_label_unit="$",
            show_absolute=input.show_absolute()
        )
    @render.text
    def ratebase_chart_description():
        if input.show_absolute():
            return "Annual ratebase for gas and electric."
        else:
          return "Difference in annual ratebase for gas and electric compared to the Business as Usual (BAU) scenario where no NPA projects are implemented."

    @render_plotly
    def return_component_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="return_on_ratebase_pct",
            title="",
            y_label_unit="% of revenue requirement",
            show_absolute=input.show_absolute()
        )
    @render.text
    def return_component_chart_description():
        if input.show_absolute():
            return "Return on ratebase as a percentage of revenue requirement for gas and electric."
        else:
          return "Difference in return on ratebase as a percentage of revenue requirement for gas and electric compared to the Business as Usual (BAU) scenario where no NPA projects are implemented."

    @render_plotly
    def nonconverts_bill_per_user_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="nonconverts_bill_per_user",
            title="",
            y_label_unit="$",   
            show_absolute=input.show_absolute()
        )
    @render.text
    def nonconverts_bill_per_user_chart_description():
        if input.show_absolute():
            return "Nonconverts annual bills for gas and electric."
        else:
          return "Difference in nonconverts annual bills for gas and electric compared to nonconverts bills in the Business as Usual (BAU) scenario where no NPA projects are implemented. We do not consider changes to supply rates in any scenario so these should be considered as changes to the delivery portion of the bill."

    @render_plotly
    def converts_bill_per_user_chart():
        df = prep_df_to_plot()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_utility_metric(
            plt_df=df,
            column="converts_bill_per_user",
            title="",
            y_label_unit="$",   
            show_absolute=input.show_absolute()
        )
    @render.text
    def converts_bill_per_user_chart_description():
        if input.show_absolute():
          return "Converts annual bills for gas and electric. In the BAU scenario, converters would only be 'scattershot' electrified, meaning they electrified on their own with no NPA project."
        else:
          return "Difference in converts annual bills for gas and electric compared to nonconverts bills in the Business as Usual (BAU) scenario where no NPA projects are implemented. Because all converts have zero gas usage after the NPA project, the gas chart represents the avoided gas spending. The electric chart includes increased demand after electrification. We do not consider changes to supply rates in any scenario so these should be considered as changes to the delivery portion of the bill."
    
    @render_plotly
    def total_bills_chart():
        df = return_delta_or_absolute_df()
        req(not df.is_empty())  # Check that DataFrame is not empty
        
        return plot_total_bills(
            delta_bau_df=df,
        )

    @render.text
    def total_bills_chart_description():
        if input.show_absolute():
            return "Combined delivery bills (gas and electric) for converts and nonconverts. In the BAU scenario, converters would only be 'scattershot' electrified, meaning they electrified on their own with no NPA project."
        else:
          return "Difference in combined delivery bills (gas and electric) for converts and nonconverts compared to the Business as Usual (BAU) scenario where no NPA projects are implemented. The converts chart (left)  shows the total bill per user for converts compared to the BAU scenario for non-converters. The nonconverts chart (right) shows the total bill per user for nonconverts compared to the BAU scenario."


    @render.download(
        filename=lambda: f'{input.run_name()}_data.csv',
        media_type="text/csv"
    )
    def download_data():
        df_to_download = return_delta_or_absolute_df()

        # Use BytesIO buffer to capture CSV output

        buffer = io.BytesIO()
        df_to_download.write_csv(buffer)
        buffer.seek(0)
        
        # Yield the buffer content
        yield buffer.getvalue()

    # Custom bookmark button handler
    @reactive.effect
    @reactive.event(input.custom_bookmark_btn)
    async def _():
        await session.bookmark()

    # Bookmark handler
    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)

app = App(app_ui, server, bookmark_store="url")