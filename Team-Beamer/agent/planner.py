from blockchain.logger import log_to_chain

def planner(state):

    if "financial" not in state["tool_results"]:
        state["next_step"] = "financial"
    elif "risk" not in state["tool_results"]:
        state["next_step"] = "risk"
    else:
        state["next_step"] = "finalize"

    state = log_to_chain(
        state,
        "Planner Decision",
        output_data={"next_step": state["next_step"]}
    )

    return state