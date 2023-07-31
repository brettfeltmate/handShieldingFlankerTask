from klibs.KLIndependentVariable import IndependentVariableSet

handShieldingFlankerTask_ind_vars = IndependentVariableSet()

handShieldingFlankerTask_ind_vars.add_variable("target_type", str, ['up', 'down'])

# As opposed to conventional flanker task, here the congruency of flankers are varied individually
handShieldingFlankerTask_ind_vars.add_variable("left_flanker_congruent", bool, [True, False])
handShieldingFlankerTask_ind_vars.add_variable("right_flanker_congruent", bool, [True, False])