from copy import deepcopy
import aviary_problems as ap
import aviary.api as av
import plots_and_analysis as pla
import fastoad.gui as foad
from variable_wing import PositionWing
from variable_wing import Aircraft
import post_process_geo as ppg
import OpenConcept.read_output as op
phase_info = {
    "pre_mission": {"include_takeoff": False, "optimize_mass": False},
    "climb_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "num_segments": 2,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.2, "unitless"),
            "final_mach": (0.72, "unitless"),
            "mach_bounds": ((0.18, 0.74), "unitless"),
            "initial_altitude": (0.0, "ft"),
            "final_altitude": (35000.0, "ft"),
            "altitude_bounds": ((0.0, 35500.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": True,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((0.0, 0.0), "min"),
            "duration_bounds": ((0, 500.0), "min"),
        },
        "initial_guesses": {"time": ([0, 67], "min")},
    },
    "cruise": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "num_segments": 2,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.72, "unitless"),
            "final_mach": (0.72, "unitless"),
            "mach_bounds": ((0.7, 0.74), "unitless"),
            "initial_altitude": (35000.0, "ft"),
            "final_altitude": (35000.0, "ft"),
            "altitude_bounds": ((35000.0, 35500.0), "ft"),
            "throttle_enforcement": "boundary_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((0, 1000.0), "min"),
            "duration_bounds": ((0, 1000.5), "min"),
        },
        "initial_guesses": {"time": ([5, 1000], "min")},
    },
    "descent_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "num_segments": 2,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.72, "unitless"),
            "final_mach": (0.2, "unitless"),
            "mach_bounds": ((0.18, 0.74), "unitless"),
            "initial_altitude": (35000.0, "ft"),
            "final_altitude": (500.0, "ft"),
            "altitude_bounds": ((0.0, 35500.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": False,
            "constrain_final": True,
            "fix_duration": False,
            "initial_bounds": ((0, 1000.5), "min"),
            "duration_bounds": ((0, 1000.5), "min"),
        },
        "initial_guesses": {"time": ([0, 121], "min")},
    },
    "post_mission": {
        "include_landing": False,
        "constrain_range": False,
        "target_range": (2500, "nmi"),
    },
    "reserve_climb": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "reserve": True,
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "num_segments": 2,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.2, "unitless"),
            "final_mach": (0.72, "unitless"),
            "mach_bounds": ((0.18, 0.74), "unitless"),
            "initial_altitude": (0.0, "ft"),
            "final_altitude": (22000.0, "ft"),
            "altitude_bounds": ((0.0, 22500.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": True,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((0.0, 0.0), "min"),
            "duration_bounds": ((0, 500.0), "min"),
        },
        "initial_guesses": {"time": ([0, 67], "min")},
    },
    "reserve_cruise": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "reserve": True,
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "target_distance": (200, "km"),
            "num_segments": 2,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.72, "unitless"),
            "final_mach": (0.72, "unitless"),
            "mach_bounds": ((0.7, 0.74), "unitless"),
            "initial_altitude": (22000.0, "ft"),
            "final_altitude": (22000.0, "ft"),
            "altitude_bounds": ((15000.0, 35500.0), "ft"),
            "throttle_enforcement": "boundary_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((0, 1000.0), "min"),
            "duration_bounds": ((0, 1000.5), "min"),
        },
        "initial_guesses": {"time": ([5, 990], "min")},
},
    "reserve_descent": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "reserve": True,
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "num_segments": 2,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.72, "unitless"),
            "final_mach": (0.2, "unitless"),
            "mach_bounds": ((0.18, 0.74), "unitless"),
            "initial_altitude": (22000.0, "ft"),
            "final_altitude": (500.0, "ft"),
            "altitude_bounds": ((0.0, 22500.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": False,
            "constrain_final": True,
            "fix_duration": False,
            "initial_bounds": ((0, 1000.5), "min"),
            "duration_bounds": ((0, 1000.5), "min"),
        },
        "initial_guesses": {"time": ([0, 600], "min")},
    },
}



#Clear the problem names and reports
from openmdao.core.problem import _clear_problem_names
_clear_problem_names()  # need to reset these to simulate separate runs
from openmdao.utils.reports_system import clear_reports
clear_reports()
# phase_info['pre_mission']['external_subsystems'] = [PositionWing()]

#run aviary problem
AVIARY_FILE = "aviary/models/test_aircraft/CERAS.csv"
prob = ap.aviary_run_problem(AVIARY_FILE,
                             phase_info = phase_info,
                             debug=False,
                             optimizer="IPOPT",
                             record_filename="history.db",
                             Analysis_scheme=av.AnalysisScheme.COLLOCATION,
                             max_iter=100
                             )


#post process the results with fast oad files and aviary
FAST_OUTPUT = "oad_sizing_out.xml"
OPEN_OUTPUT = "/home/aeomath/Bureau/ADAM/SUPAERO/DCAS/openconcept/output_list.txt"

print(prob.get_val(av.Aircraft.Wing.ASPECT_RATIO)[0])
fig = ppg.wing_geometry_plot(prob,name="AVIARY")
fig = foad.wing_geometry_plot(FAST_OUTPUT, name="FAST-OAD", fig=fig)
fig2 = pla.mass_breakdown_bar_plot_av(prob=prob,name = "AVIARY Ceras",oad='AVIARY')
fig2 = pla.mass_breakdown_bar_plot_av(FAST_OUTPUT, name="FAST-OAD_ceras",oad='FAST-OAD',fig=fig2)
fig2 = pla.mass_breakdown_bar_plot_av(OPEN_OUTPUT, name="OPENCONCEPT",oad='OPENCONCEPT',fig=fig2)
fig3 = ppg.aircraft_geometry_plot(prob,name="AVIARY")
fig3 = foad.aircraft_geometry_plot(FAST_OUTPUT, name="FAST-OAD", fig=fig3)
fig4 = pla.geometry_mass_bar(prob=prob,name="AVIARY",oad='AVIARY')
fig4 = pla.geometry_mass_bar(aircraft_file_path=FAST_OUTPUT, name="FAST-OAD", fig=fig4,oad='FAST-OAD')
fig4 = pla.geometry_mass_bar(aircraft_file_path=OPEN_OUTPUT, name="OPENCONCEPT", fig=fig4,oad='OPENCONCEPT')
fig.show()
fig2.show()
fig3.show()
fig4.show()