import aviary.api as av

from aviary.variable_info.enums import Verbosity


def aviary_run_problem(
    aircraft_file, 
    phase_info,
    debug=False ,
    max_iter= 50, optimizer = "SLSQP",
    objective_type = None, 
    record_filename = 'history.db',
    restart_filename = None,
    Analysis_scheme = av.AnalysisScheme.COLLOCATION,
    ):
    # Build problem
    prob = av.AviaryProblem(analysis_scheme= Analysis_scheme)

    # Load aircraft and options data from user
    # Allow for user overrides here
    if debug:
        prob.load_inputs(aircraft_file,phase_info=phase_info,verbosity=Verbosity.DEBUG)
    else:
        prob.load_inputs(aircraft_file,phase_info=phase_info,verbosity=Verbosity.BRIEF)

    # Preprocess inputs
    prob.check_and_preprocess_inputs() ## Check inputs and preprocess them to see if everything is ok

    prob.add_pre_mission_systems() ##  includes pre-mission propulsion, geometry, pre-mission aerodynamics, and mass subsystems , dont change during the mission

    prob.add_phases() ## Add phases to the problem

    prob.add_post_mission_systems() ## Add post-mission systems (landing, etc) stuff that does not change during the mission

    # Link phases and variables
    prob.link_phases()
    if debug:
        prob.add_driver(optimizer,max_iter=max_iter,verbosity=Verbosity.DEBUG) ## Add optimizer if you want an alnaysis run only, set max_iter=0
    else:
        prob.add_driver(optimizer,max_iter=max_iter,verbosity=Verbosity.BRIEF)


    ## add designe variables manually , otherwise it will add the default ones
    prob.add_design_variables()
    # prob.model.add_design_var(av.Aircraft.Wing.ASPECT_RATIO, lower=1., upper=17., ref=12.)
    ##prob.model.add_constraint(av.Aircraft.Wing.SPAN,upper=196.8)

    # Load optimization problem formulation
    # Detail which variables the optimizer can control
    prob.add_objective(objective_type=objective_type) ## Add objective function  

    prob.setup()

    prob.set_initial_guesses()
    ## set initial guesses for the problem

    prob.run_aviary_problem(record_filename,suppress_solver_print=True) ## Run the problem
    return prob
