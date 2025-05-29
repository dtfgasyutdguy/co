from typing import List
from integuru.graph_builder import build_graph
from integuru.util.LLM import llm

agent = None

async def call_agent(
    model: str,
    prompt: str,
    har_file_path: str,
    cookie_path: str,
    input_variables: dict = None,
    max_steps: int = 15,
    to_generate_code: bool = False,
):  
    
    llm.set_default_model(model)

    global agent
    graph, agent = build_graph(prompt, har_file_path, cookie_path, to_generate_code)
    event_stream = graph.astream(
        {
            "master_node": None,
            "in_process_node": None,
            "to_be_processed_nodes": [],
            "in_process_node_dynamic_parts": [],
            "action_url": "",
            "input_variables": input_variables or {},  
        },
        {
            "recursion_limit": max_steps,
        },
    )
    async for event in event_stream:
        # print("+++", event)
        pass
