from . import os, Path

general_output = Path("data_output")
# general_output.mkdir(exist_ok=True)

mfpt_results_output = Path("data_output/mfpt-results")

heatmap_output = Path("data_output/heatmaps")
# heatmap_output.mkdir(exist_ok=True)

phi_v_theta_output = Path("data_output/phi-v-theta")
# phi_v_theta_output.mkdir(exist_ok=True)

# Density results output directories

angular_dependence_phi = Path("data_output/density-results/angular-dependence/phi")
angular_dependence_rho = Path("data_output/density-results/angular-dependence/rho")

radial_dependence_phi = Path("data_output/density-results/radial-dependence/phi")
radial_dependence_rho = Path("data_output/density-results/radial-dependence/rho")



