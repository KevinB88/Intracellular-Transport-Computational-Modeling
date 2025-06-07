from . import os, Path

general_output = Path("data_output")
# general_output.mkdir(exist_ok=True)

mfpt_results_output = Path("data_output/mfpt-results")

heatmap_output = Path("data_output/heatmaps")
# heatmap_output.mkdir(exist_ok=True)

phi_v_theta_output = Path("data_output/diffusive-v-theta")
# phi_v_theta_output.mkdir(exist_ok=True)

# Density results output directories

angular_dependence_phi = Path("data_output/density-results/angular-dependence/diffusive")
angular_dependence_rho = Path("data_output/density-results/angular-dependence/rho")

radial_dependence_phi = Path("data_output/density-results/radial-dependence/diffusive")
radial_dependence_rho = Path("data_output/density-results/radial-dependence/rho")

# Mass analysis results

mass_analysis_advective = Path("data_output/mass_analysis_results/advective")
mass_analysis_diffusive = Path("data_output/mass_analysis_results/diffusive")
mass_analysis_advective_over_total = Path("data_output/mass_analysis_results/advective_over_total")
mass_analysis_total = Path("data_output/mass_analysis_results/total")
mass_analysis_advective_over_initial = Path("data_output/mass_analysis_results/advective_over_initial")

rect_logs = Path("data_output/output_logs")

