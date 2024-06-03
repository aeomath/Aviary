import aviary.api as av

## Reset and delete variables and metadata
from openmdao.core.problem import _clear_problem_names
_clear_problem_names()  # need to reset these to simulate separate runs
from openmdao.utils.reports_system import clear_reports
clear_reports()


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
            "duration_bounds": ((0, 1000.0), "min"),
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
        "initial_guesses": {"time": ([54, 311], "min")},
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
}

from aviary.api import Aircraft, Mission,Verbosity
import aviary.api as av

# inputs that run_aviary() requires
aircraft_filename = "aviary/models/test_aircraft/CERAS.csv"
#aircraft_filename = "aviary/models/test_aircraft/aircraft_for_bench_GwGm.csv"
mission_method = "2DOF"
mass_method = "GASP"
optimizer = "IPOPT" ## Available options: "SLSQP", "IPOPT", for IPOPT, you need to install it separately using pyoptsparse, SNOP, 
analysis_scheme = av.AnalysisScheme.COLLOCATION ## collocation or shooting cf dymos documentation
objective_type = None #None is fuel burn 
record_filename = 'history.db'
restart_filename = None



# Build problem
prob = av.AviaryProblem(analysis_scheme)

# Load aircraft and options data from user
# Allow for user overrides here

prob.load_inputs(aircraft_filename,phase_info=phase_info,verbosity=Verbosity.DEBUG)

# Preprocess inputs
prob.check_and_preprocess_inputs() ## Check inputs and preprocess them to see if everything is ok

prob.add_pre_mission_systems() ##  includes pre-mission propulsion, geometry, pre-mission aerodynamics, and mass subsystems , dont change during the mission

prob.add_phases() ## Add phases to the problem

prob.add_post_mission_systems() ## Add post-mission systems (landing, etc) stuff that does not change during the mission

# Link phases and variables
prob.link_phases()

prob.add_driver(optimizer,max_iter=100,verbosity=Verbosity.DEBUG) ## Add optimizer if you want an alnaysis run only, set max_iter=0



## add designe variables manually , otherwise it will add the default ones
prob.add_design_variables()
##øprob.model.add_design_var(av.Aircraft.Wing.ASPECT_RATIO, lower=0., upper=50., ref=12.)
##prob.model.add_constraint(av.Aircraft.Wing.SPAN,upper=196.8)

# Load optimization problem formulation
# Detail which variables the optimizer can control
prob.add_objective('fuel_burned') ## Add objective function  

prob.setup()

prob.set_initial_guesses()
## set initial guesses for the problem

prob.run_aviary_problem(record_filename,suppress_solver_print=True) ## Run the problem

fixed_mission_optimized_wing_fuel_burn = prob.get_val(av.Mission.Summary.FUEL_BURNED, units='kg')[0]
fixed_mission_optimized_wing_aspect_ratio = prob.get_val(av.Aircraft.Wing.ASPECT_RATIO)[0]


span = prob.get_val(av.Aircraft.Wing.SPAN, units='ft')[0]
area = prob.get_val(av.Aircraft.Wing.AREA, units='ft**2')[0]

# speed= prob.get(av.Dynamic.Mission.VELOCITY, units='m/s')

print('Mission fuel burn, kg:', fixed_mission_optimized_wing_fuel_burn)
print('Aspect ratio_fixed:', fixed_mission_optimized_wing_aspect_ratio)
print('Wing area:', prob.get_val(av.Aircraft.Wing.AREA,units='m**2'))

