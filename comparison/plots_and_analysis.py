import aviary.api as av
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import fastoad.gui  as foad 
from openmdao.utils.units import convert_units
from plotly.subplots import make_subplots
from fastoad.io import VariableIO
from OpenConcept.read_output import get_variable_value
COLS = px.colors.qualitative.Plotly


def mass_breakdown_bar_plot_av(
    aircraft_file_path = None,
    prob=None,
    name=None,
    fig=None,
    *,
    file_formatter=None,
    input_mass_name="data:weight:aircraft:MTOW",
    oad= 'FAST-OAD',
) -> go.FigureWidget:
    """
    Returns a figure plot of the aircraft mass breakdown using bar plots.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param aircraft_file_path: path of data file
    :param name: name to give to the trace added to the figure
    :param fig: existing figure to which add the plot
    :param file_formatter: the formatter that defines the format of data file. If not provided,
                           default format will be assumed.
    :param input_mass_name: the variable name for the mass input as defined in the mission
                            definition file.
    :return: bar plot figure
    """
    if fig is None:
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Maximum Take-Off Weight Breakdown", "Overall Weight Empty Breakdown"),
        )
    # Same color for each aircraft configuration
    i = int(len(fig.data) / 2) % 10


    if oad == 'AVIARY':
        mzfw = prob.get_val(av.Aircraft.Design.ZERO_FUEL_MASS,units='kg')[0]
        mtow = prob.get_val(av.Mission.Design.GROSS_MASS,units='kg')[0]
        owe = prob.get_val(av.Aircraft.Design.OPERATING_MASS,units='kg')[0]
        payload = prob.get_val(av.Aircraft.CrewPayload.TOTAL_PAYLOAD_MASS,units='kg')[0]
        fuel_mission = prob.get_val(av.Mission.Summary.FUEL_BURNED,units='kg')[0]
    
        owe_decomp = [
            prob.get_val(av.Aircraft.Design.STRUCTURE_MASS, units="kg")[0],
            prob.get_val(av.Aircraft.CrewPayload.FLIGHT_CREW_MASS, units="kg")[0],
            prob.get_val(av.Aircraft.Furnishings.MASS ,units="kg")[0],
            prob.get_val(av.Aircraft.Propulsion.MASS, units="kg")[0],
            prob.get_val(av.Aircraft.Design.SYSTEMS_EQUIP_MASS, units="kg")[0],  
            prob.get_val(av.Aircraft.Wing.MASS, units="kg")[0]
        ]
    # pylint: disable=unbalanced-tuple-unpacking # It is balanced for the parameters provided
    elif oad == 'FAST-OAD':
        variables = VariableIO(aircraft_file_path, file_formatter).read()

        var_names_and_new_units = {
            input_mass_name: "kg",
            "data:weight:aircraft:MZFW": "kg",
            "data:weight:aircraft:OWE": "kg",
            "data:weight:aircraft:payload": "kg",
            "data:weight:aircraft:sizing_onboard_fuel_at_input_weight": "kg",
            
        }

        # pylint: disable=unbalanced-tuple-unpacking # It is balanced for the parameters provided
        mtow, mzfw, owe, payload, fuel_mission = foad._get_variable_values_with_new_units(variables, var_names_and_new_units)
        
        # Get data:weight decomposition
        owe_decomp,owe_label, _ = foad._data_weight_decomposition(variables, owe=None)
        owe_decomp.append(variables["data:weight:airframe:wing:mass"].value[0])
    elif oad == "OPENCONCEPT":
        mtow = get_variable_value(aircraft_file_path, "ac|weights|MTOW", "kg")
        mzfw = 0 #get_variable_value(aircraft_file_path, "ac|weights|MZFW", "kg")
        owe = get_variable_value(aircraft_file_path, "ac|weights|OEW", "kg")
        fuel_mission = get_variable_value(aircraft_file_path, "mission.descent.fuel_burn_integ.fuel_burn_final", "kg") ## Without reserve
        reserve_final = get_variable_value(aircraft_file_path, "mission.reserve_descent.fuel_burn_integ.fuel_burn_final", "kg")
        mlw = get_variable_value(aircraft_file_path, "ac|weights|MLW", "kg")
        mzfw = mlw - (reserve_final-fuel_mission)
        payload = get_variable_value(aircraft_file_path, "ac|weights|W_payload", "kg")
    
        owe_decomp = [
            ## Airframe
            get_variable_value(aircraft_file_path, "empty_weight.W_structure", "kg"),
            0,# crew 
            ## Furniture
            get_variable_value(aircraft_file_path, "empty_weight.W_furnishings", "kg"),
            ## Propulsion
            get_variable_value(aircraft_file_path, "empty_weight.W_engines", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_thrust_rev", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_fuelsystem", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_eng_start", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_eng_control", "kg"), 
            ## Systems
            get_variable_value(aircraft_file_path,"empty_weight.equipment.W_flight_controls","kg")\
            + get_variable_value(aircraft_file_path,"empty_weight.equipment.W_avionics","kg")\
            + get_variable_value(aircraft_file_path,"empty_weight.equipment.W_electrical","kg")\
            + get_variable_value(aircraft_file_path,"empty_weight.equipment.W_ac_pressurize_antiice","kg")\
            + get_variable_value(aircraft_file_path,"empty_weight.equipment.W_oxygen ","kg")\
            + get_variable_value(aircraft_file_path,"empty_weight.equipment.W_APU","kg"),
            get_variable_value(aircraft_file_path, "empty_weight.W_wing", "kg")
        ]
    weight_labels = ["MTOW" , "MZFW" , "OWE", "Fuel - Mission", "Payload"]
    weight_values =  [mtow , mzfw , owe, fuel_mission, payload]
    fig.add_trace(
        go.Bar(name="", x=weight_labels, y=weight_values, marker_color=COLS[i], showlegend=False),
        row=1,
        col=1,
    )

     # Get data:weight decomposition
    owe_label = ["airframe", "crew","furniture","propulsion","systems","wing"]
    fig.add_trace(
        go.Bar(name=name, x=owe_label, y=owe_decomp, marker_color=COLS[i]),
        row=1,
        col=2,
    )
    if oad == 'OPENCONCEPT':
        fig.add_shape(
            type="line",
            x0=0.1,
            y0=owe_decomp[0]/1.2,
            x1=0.45,
            y1=owe_decomp[0]/1.2,
            line=dict(color="black", width=2),
            row=1,
            col=2,
        )
        fig.add_annotation(
            x=1.0,
            y=owe_decomp[0]/1.2+500,
            text="without correction factor",
            showarrow=False,
            font=dict(size=12),
            row=1,
            col=2,
        )
  

    fig.update_layout(yaxis_title="[kg]")
    print(owe_decomp)
    return fig

def geometry_mass_bar(name=None, aircraft_file_path = None , oad="AVIARY",prob = None ,file_formatter = None,fig = None)-> go.FigureWidget:
    if fig is None:
        fig = make_subplots(
            rows=1,
            cols=1,
            subplot_titles=("Geometry Mass Breakdown"),
        )
    # Same color for each aircraft configuration
    i = int(len(fig.data) / 1) % 10
    if oad == 'AVIARY':
        wing_mass = prob.get_val(av.Aircraft.Wing.MASS,units='kg')[0]
        fuselage_mass = prob.get_val(av.Aircraft.Fuselage.MASS,units='kg')[0]
        htail_mass = prob.get_val(av.Aircraft.HorizontalTail.MASS,units='kg')[0]
        vtail_mass = prob.get_val(av.Aircraft.VerticalTail.MASS,units='kg')[0]
        engine_mass = prob.get_val(av.Aircraft.Propulsion.TOTAL_ENGINE_MASS,units='kg')[0]
    
    # pylint: disable=unbalanced-tuple-unpacking # It is balanced for the parameters provided
    elif oad == 'FAST-OAD':
        variables = VariableIO(aircraft_file_path, file_formatter).read()

        var_names_and_new_units = {
            "data:weight:airframe:wing:mass": "kg",
            "data:weight:airframe:fuselage:mass": "kg",
            "data:weight:airframe:horizontal_tail:mass": "kg",
            "data:weight:airframe:vertical_tail:mass": "kg",
            "data:weight:propulsion:engine:mass": "kg"
            
        }

        # pylint: disable=unbalanced-tuple-unpacking # It is balanced for the parameters provided
        wing_mass,fuselage_mass,htail_mass,vtail_mass,engine_mass = foad._get_variable_values_with_new_units(variables, var_names_and_new_units)
    elif oad == "OPENCONCEPT":
        wing_mass = get_variable_value(aircraft_file_path, "empty_weight.W_wing", "kg")
        fuselage_mass = get_variable_value(aircraft_file_path, "empty_weight.W_fuselage", "kg")
        htail_mass = get_variable_value(aircraft_file_path, "empty_weight.W_hstab"  , "kg")
        vtail_mass = get_variable_value(aircraft_file_path, "empty_weight.W_vstab", "kg")
        engine_mass = get_variable_value(aircraft_file_path, "empty_weight.W_engines", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_thrust_rev", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_fuelsystem", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_eng_start", "kg")\
            + get_variable_value(aircraft_file_path, "empty_weight.W_eng_control", "kg")                
        
    weight_labels = ["Wing" , "Fuselage" , "Horizontal Tail", "Vertical Tail", "Engine"]
    weight_values =  [wing_mass , fuselage_mass , htail_mass, vtail_mass,engine_mass]
    fig.add_trace(
        go.Bar(name=name, x=weight_labels, y=weight_values, marker_color=COLS[i], showlegend=True),
        row=1,
        col=1,
    )
    fig.update_layout(yaxis_title="[kg]")
    return fig