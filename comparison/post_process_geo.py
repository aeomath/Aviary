import aviary.api as av 
import numpy as np
import openmdao.api as om
import math
from aviary.utils.aviary_values import AviaryValues
import openmdao.api as om

from aviary.subsystems.subsystem_builder_base import SubsystemBuilderBase
from aviary.variable_info.variables import Aircraft



##doc


wing_kink_span_ratio = 0.375
sweep_100 = 0
def compute_Wing_y_pos(prob,wing_kink_span_ratio):
    lambda_wing = prob.get_val(Aircraft.Wing.ASPECT_RATIO)[0]
    wing_area = prob.get_val(Aircraft.Wing.AREA,units="m**2")[0]
    wing_break = wing_kink_span_ratio
    width_max = prob.get_val(Aircraft.Fuselage.MAX_WIDTH,units="m")[0]
    
  
    span = math.sqrt(lambda_wing * wing_area)
    y4_wing = 0.5 * span
    y2_wing = width_max / 2
    y3_wing = np.maximum(y2_wing,y4_wing * wing_break)
    return y2_wing,y3_wing,y4_wing

def computeL1L4(prob,sweep_100,y2_wing,y3_wing):
    wing_area = prob.get_val(Aircraft.Wing.AREA,units="m**2")[0]
    span = prob.get_val(Aircraft.Wing.SPAN,units="m")[0]
    virtual_taper_ratio = prob.get_val(Aircraft.Wing.TAPER_RATIO)[0]
    sweep_25 = prob.get_val(Aircraft.Wing.SWEEP,units= "rad")[0]
    l1_wing = (
            wing_area
            - (y3_wing - y2_wing) * (y3_wing + y2_wing) * (math.tan(sweep_25) - math.tan(sweep_100))
        ) / (
            (1.0 + virtual_taper_ratio) / 2.0 * (span - 2 * y2_wing)
            + 2 * y2_wing
            - (3.0 * (1.0 - virtual_taper_ratio) * (y3_wing - y2_wing) * (y3_wing + y2_wing))
            / (2.0 * (span - 2 * y2_wing))
        )

    l4_wing = l1_wing * virtual_taper_ratio
    
    return l1_wing,l4_wing

def computel2l3(prob,y2_wing,y3_wing,y4_wing,l1_wing,l4_wing):
    sweep_25 = prob.get_val(Aircraft.Wing.SWEEP,units = "rad")[0]
    span = prob.get_val(Aircraft.Wing.SPAN,units = "m")[0]
    width_max = prob.get_val(Aircraft.Fuselage.MAX_WIDTH,units="m")[0]
    virtual_taper_ratio = prob.get_val(Aircraft.Wing.TAPER_RATIO)[0]
    if y3_wing <= y2_wing :
        l2_wing = l3_wing = l1_wing
    else:
        l2_wing = l1_wing + (y3_wing - y2_wing) * (
            math.tan(sweep_25)
            - math.tan(sweep_100)
            - 3.0 / 2.0 * (1.0 - virtual_taper_ratio) / (span - width_max) * l1_wing
        )
    l3_wing = l4_wing + (l1_wing - l4_wing) * (y4_wing - y3_wing) / (y4_wing - y2_wing)
    return l2_wing,l3_wing

    
    
def computeXWing(prob,y2_wing,y3_wing,y4_wing,l1_wing,l3_wing,l4_wing):
    sweep_25 = prob.get_val(Aircraft.Wing.SWEEP,units = "deg")[0]
    x3_wing = (
        1.0 / 4.0 * l1_wing
        + (y3_wing - y2_wing) * math.tan(sweep_25 / 180.0 * math.pi)
        - 1.0 / 4.0 * l3_wing
    )
    x4_wing = (
        1.0 / 4.0 * l1_wing
        + (y4_wing - y2_wing) * math.tan(sweep_25 / 180.0 * math.pi)
        - 1.0 / 4.0 * l4_wing
    )
    return x3_wing,x4_wing

def computeMAC(prob,y2_wing,y3_wing,y4_wing,l2_wing,l3_wing,l4_wing,x3_wing,x4_wing):
    wing_area = prob.get_val(Aircraft.Wing.AREA,units="m**2")[0]
    l0_wing = (
            3 * y2_wing * l2_wing**2
            + (y3_wing - y2_wing) * (l2_wing**2 + l3_wing**2 + l2_wing * l3_wing)
            + (y4_wing - y3_wing) * (l3_wing**2 + l4_wing**2 + l3_wing * l4_wing)
        ) * (2 / (3 * wing_area))

    x0_wing = (
        x3_wing
        * (
            (y3_wing - y2_wing) * (2 * l3_wing + l2_wing)
            + (y4_wing - y3_wing) * (2 * l3_wing + l4_wing)
        )
        + x4_wing * (y4_wing - y3_wing) * (2 * l4_wing + l3_wing)
    ) / (3 * wing_area)

    y0_wing = (
        3 * y2_wing**2 * l2_wing
        + (y3_wing - y2_wing)
        * (l3_wing * (y2_wing + 2 * y3_wing) + l2_wing * (y3_wing + 2 * y2_wing))
        + (y4_wing - y3_wing)
        * (l4_wing * (y3_wing + 2 * y4_wing) + l3_wing * (y4_wing + 2 * y3_wing))
    ) / (3 * wing_area)
    return l0_wing,x0_wing,y0_wing

def geo_variable_for_plots(prob,wing_kink_span_ratio = 0.375 , sweep_100 = 0.0):
    y2_wing,y3_wing,y4_wing = compute_Wing_y_pos(prob,wing_kink_span_ratio)
    l1_wing,l4_wing = computeL1L4(prob,sweep_100,y2_wing,y3_wing)
    l2_wing,l3_wing = computel2l3(prob,y2_wing,y3_wing,y4_wing,l1_wing,l4_wing)
    x3_wing,x4_wing = computeXWing(prob,y2_wing,y3_wing,y4_wing,l1_wing,l3_wing,l4_wing)
    l0_wing,x0_wing,y0_wing = computeMAC(prob,y2_wing,y3_wing,y4_wing,l2_wing,l3_wing,l4_wing,x3_wing,x4_wing)
    
    wing_kink_leading_edge_x = x3_wing
    wing_tip_leading_edge_x = x4_wing
    wing_root_y = y2_wing
    wing_kink_y = y3_wing
    wing_tip_y = y4_wing
    wing_root_chord =  l2_wing
    wing_kink_chord = l3_wing
    wing_tip_chord = l4_wing
    mean_aerodynamic_chord = l0_wing
    mac25_x_position= 16.0
    distance_root_mac_chords = x0_wing
    return wing_kink_leading_edge_x,wing_tip_leading_edge_x,wing_root_y,wing_kink_y,wing_tip_y,wing_root_chord,wing_kink_chord,wing_tip_chord,mean_aerodynamic_chord,mac25_x_position,distance_root_mac_chords

from typing import Dict

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from openmdao.utils.units import convert_units
from plotly.subplots import make_subplots

from fastoad.io import VariableIO
from fastoad.openmdao.variables import VariableList

COLS = px.colors.qualitative.Plotly


# pylint: disable-msg=too-many-locals
def wing_geometry_plot(prob,
    aircraft_file_path=None, name=None, fig=None, *, file_formatter=None
) -> go.FigureWidget:
    """
    Returns a figure plot of the top view of the wing.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param aircraft_file_path: path of data file
    :param name: name to give to the trace added to the figure
    :param fig: existing figure to which add the plot
    :param file_formatter: the formatter that defines the format of data file. If not provided,
                           default format will be assumed.
    :return: wing plot figure
    """
    

    wing_kink_leading_edge_x,wing_tip_leading_edge_x,wing_root_y,wing_kink_y,wing_tip_y,wing_root_chord,wing_kink_chord,wing_tip_chord,mean_aerodynamic_chord,mac25_x_position,distance_root_mac_chords = geo_variable_for_plots(prob)
    
    # pylint: disable=invalid-name # that's a common naming
    y = np.array(
        [0, wing_root_y, wing_kink_y, wing_tip_y, wing_tip_y, wing_kink_y, wing_root_y, 0, 0]
    )
    # pylint: disable=invalid-name # that's a common naming
    y = np.concatenate((-y, y))

    # pylint: disable=invalid-name # that's a common naming
    x = np.array(
        [
            0,
            0,
            wing_kink_leading_edge_x,
            wing_tip_leading_edge_x,
            wing_tip_leading_edge_x + wing_tip_chord,
            wing_kink_leading_edge_x + wing_kink_chord,
            wing_root_chord,
            wing_root_chord,
            0,
        ]
    )

    x = x + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x, x))

    if fig is None:
        fig = go.Figure()

    scatter = go.Scatter(x=y, y=x, mode="lines+markers", name=name)

    fig.add_trace(scatter)

    fig.layout = go.Layout(yaxis=dict(scaleanchor="x", scaleratio=1))

    fig = go.FigureWidget(fig)

    fig.update_layout(title_text="Wing Geometry", title_x=0.5, xaxis_title="y", yaxis_title="x")

    return fig


def compute_horizontal_tail(prob):
    lambda_ht = prob.get_val(Aircraft.HorizontalTail.ASPECT_RATIO,units="unitless")[0]
    s_h = prob.get_val(Aircraft.HorizontalTail.AREA,units="m**2")[0]
    taper_ht = prob.get_val(Aircraft.HorizontalTail.TAPER_RATIO,units="unitless")[0]
    
    b_h = np.sqrt(max(lambda_ht * s_h, 0.1))
    root_chord = s_h * 2 / (1 + taper_ht) / b_h
    tip_chord = root_chord * taper_ht
    return b_h,root_chord,tip_chord


def aircraft_geometry_plot(prob,
    aircraft_file_path=None, name=None, fig=None, *, file_formatter=None
) -> go.FigureWidget:
    """
    Returns a figure plot of the top view of the wing.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param aircraft_file_path: path of data file
    :param name: name to give to the trace added to the figure
    :param fig: existing figure to which add the plot
    :param file_formatter: the formatter that defines the format of data file. If not provided,
                           default format will be assumed.
    :return: wing plot figure
    """

    # Wing parameters
    
    wing_kink_leading_edge_x = geo_variable_for_plots(prob)[0]
    wing_tip_leading_edge_x = geo_variable_for_plots(prob)[1]
    wing_root_y = geo_variable_for_plots(prob)[2]
    wing_kink_y = geo_variable_for_plots(prob)[3]
    wing_tip_y = geo_variable_for_plots(prob)[4]
    wing_root_chord =   geo_variable_for_plots(prob)[5]
    wing_kink_chord = geo_variable_for_plots(prob)[6]
    wing_tip_chord = geo_variable_for_plots(prob)[7]

    y_wing = np.array(
        [0, wing_root_y, wing_kink_y, wing_tip_y, wing_tip_y, wing_kink_y, wing_root_y, 0, 0]
    )

    x_wing = np.array(
        [
            0,
            0,
            wing_kink_leading_edge_x,
            wing_tip_leading_edge_x,
            wing_tip_leading_edge_x + wing_tip_chord,
            wing_kink_leading_edge_x + wing_kink_chord,
            wing_root_chord,
            wing_root_chord,
            0,
        ]
    )

    # Horizontal Tail parameters
    ht_root_chord = compute_horizontal_tail(prob)[1]
    ht_tip_chord = compute_horizontal_tail(prob)[2]
    ht_span = compute_horizontal_tail(prob)[0]
    ht_sweep_0 = 33.31651496553977

    ht_tip_leading_edge_x = ht_span / 2.0 * np.tan(ht_sweep_0 * np.pi / 180.0)

    y_ht = np.array([0, ht_span / 2.0, ht_span / 2.0, 0.0, 0.0])

    x_ht = np.array(
        [0, ht_tip_leading_edge_x, ht_tip_leading_edge_x + ht_tip_chord, ht_root_chord, 0]
    )

    # Fuselage parameters
    fuselage_max_width = prob.get_val(Aircraft.Fuselage.MAX_WIDTH,units="m")[0]
    fuselage_length = prob.get_val(Aircraft.Fuselage.LENGTH,units="m")[0]
    fuselage_front_length =0
    fuselage_rear_length = 0

    x_fuselage = np.array(
        [
            0.0,
            0.0,
            fuselage_front_length,
            fuselage_length - fuselage_rear_length,
            fuselage_length,
            fuselage_length,
        ]
    )

    y_fuselage = np.array(
        [
            0.0,
            fuselage_max_width / 4.0,
            fuselage_max_width / 2.0,
            fuselage_max_width / 2.0,
            fuselage_max_width / 4.0,
            0.0,
        ]
    )

    # CGs
    wing_25mac_x = geo_variable_for_plots(prob)[9]
    wing_mac_length = geo_variable_for_plots(prob)[8]
    local_wing_mac_le_x = geo_variable_for_plots(prob)[10]
    local_ht_25mac_x = 1.615988599481118
    ht_distance_from_wing = 18.131701240000005

    x_wing = x_wing + wing_25mac_x - 0.25 * wing_mac_length - local_wing_mac_le_x
    x_ht = x_ht + wing_25mac_x + ht_distance_from_wing - local_ht_25mac_x

    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x_fuselage, x_wing, x_ht))
    # pylint: disable=invalid-name # that's a common naming
    y = np.concatenate((y_fuselage, y_wing, y_ht))

    # pylint: disable=invalid-name # that's a common naming
    y = np.concatenate((-y, y))
    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x, x))

    if fig is None:
        fig = go.Figure()

    scatter = go.Scatter(x=y, y=x, mode="lines+markers", name=name)

    fig.add_trace(scatter)

    fig.layout = go.Layout(yaxis=dict(scaleanchor="x", scaleratio=1))

    fig = go.FigureWidget(fig)

    fig.update_layout(title_text="Aircraft Geometry", title_x=0.5, xaxis_title="y", yaxis_title="x")

    return fig
