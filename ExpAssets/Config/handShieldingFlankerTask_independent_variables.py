from klibs.KLIndependentVariable import IndependentVariableSet

handShieldingFlankerTask_ind_vars = IndependentVariableSet()

handShieldingFlankerTask_ind_vars.add_variable("target_letter", str, ['H', 'S'])

# As opposed to conventional flanker task, here the congruency of flankers are varied individually
handShieldingFlankerTask_ind_vars.add_variable(
    "left_flanker", str, ['congruent', 'incongruent', 'neutral']
    )

handShieldingFlankerTask_ind_vars.add_variable(
    "right_flanker", str, ['congruent', 'incongruent', 'neutral']
    )
