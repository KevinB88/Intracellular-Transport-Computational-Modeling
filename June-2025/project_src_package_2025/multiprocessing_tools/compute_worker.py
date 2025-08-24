
def compute_and_send(computation_name, param_dict):
    from project_src_package_2025.multiprocessing_tools import computation_router
    import json
    try:
        result = computation_router.run_selected_computation(computation_name, param_dict)
        output = {"status": "ok", "result": result}
    except Exception as e:
        output = {"status": "error", "message": str(e)}
    with open(f"result_{computation_name}.json", "w") as f:
        json.dump(output, f)




