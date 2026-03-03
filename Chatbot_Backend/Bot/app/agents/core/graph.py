from langgraph.graph import StateGraph, END, START
from app.agents.core.state import ChatbotState
from langgraph.checkpoint.memory import MemorySaver
from app.agents.core.nodes import AgentNodes
from app.agents.core.router import RouterNode


def build_graph() -> StateGraph:
    builder = StateGraph(ChatbotState)
    node = AgentNodes()
    router = RouterNode()
    
    # Nodes
    builder.add_node("greeting_node", node.greeting_node)
    builder.add_node("get_user_problem_node", node.get_user_problem_node)
    builder.add_node("get_problem_node", node.get_problem_node)
    builder.add_node("followup_problem_detect_node", node.followup_problem_detect_node)
    builder.add_node("emotion_support_node", node.emotion_support_node)
    builder.add_node("get_user_emotion_node", node.get_user_emotion_node)
    builder.add_node("problem_depth_analysis_node", node.problem_depth_analysis_node)
    builder.add_node("ask_emotion_check_node", node.ask_emotion_check_node)
    builder.add_node("ask_other_node", node.ask_other_node)
    builder.add_node("ask_phq_9_node", node.ask_phq_9_node)
    builder.add_node("get_user_answer_phq9_node", node.get_user_answer_phq9_node)
    builder.add_node("get_level_of_depression_node", node.get_level_of_depression_node)
    builder.add_node("problem_summary_node", node.problem_summary_node)
    builder.add_node("deep_support_node", node.deep_support_node)
    builder.add_node("get_user_deep_support_node", node.get_user_deep_support_node)
    builder.add_node("deep_support_summary_node", node.deep_support_summary_node)
    builder.add_node("ask_save_deep_node", node.ask_save_deep_node)
    builder.add_node("get_confirm_save_deep_node", node.get_confirm_save_deep_node)
    builder.add_node("save_deep_support_info_node", node.save_deep_support_info_node)
    builder.add_node("announce_move_to_step_6", node.announce_move_to_step_6)
    builder.add_node("gentle_info_phase_node", node.gentle_info_phase_node)
    builder.add_node("get_user_gentle_phase_node", node.get_user_gentle_phase_node)
    builder.add_node("finish_node", node.finish_node)
    
    # Routers
    builder.add_node("check_problem_detected_router", router.check_problem_detected_router)
    builder.add_node("check_problem_depth_analysis_router", router.check_problem_depth_analysis_router)
    builder.add_node("check_full_phq9_answer_router", router.check_full_phq9_answer_router)
    builder.add_node("analyze_user_input_router", router.analyze_user_input_router)
    builder.add_node("check_save_deep_confirm_router", router.check_save_deep_confirm_router)
    builder.add_node("analyze_gentle_info_phase_router", router.analyze_gentle_info_phase_router)
    
    builder.add_edge(START, "greeting_node")
    builder.add_edge("greeting_node", "get_user_problem_node")
    builder.add_edge("get_user_problem_node", "get_problem_node")
    builder.add_edge("get_problem_node", "check_problem_detected_router")
    builder.add_conditional_edges(
        "check_problem_detected_router",
        lambda state: state["next_node"],
        {
            "detected": "emotion_support_node",
            "insufficient_info": "followup_problem_detect_node"
        }
    )
    
    builder.add_edge("followup_problem_detect_node", "get_user_problem_node")
    builder.add_edge("emotion_support_node", "get_user_emotion_node")
    builder.add_edge("get_user_emotion_node", "problem_depth_analysis_node")
    builder.add_edge("problem_depth_analysis_node", "check_problem_depth_analysis_router")
    
    builder.add_conditional_edges(
        "check_problem_depth_analysis_router",
        lambda state: state["next_node"],
        {
            "move_to_step_5": "problem_summary_node",
            "ask_PHQ9": "ask_phq_9_node",
            "ask_other": "ask_other_node",
            "ask_emotion_check": "ask_emotion_check_node",
        }
    )
    
    builder.add_edge("ask_emotion_check_node", "get_user_emotion_node")
    builder.add_edge("ask_other_node", "get_user_emotion_node")
    
    builder.add_edge("ask_phq_9_node", "get_user_answer_phq9_node")
    builder.add_edge("get_user_answer_phq9_node", "check_full_phq9_answer_router")
    builder.add_conditional_edges(
        "check_full_phq9_answer_router",
        lambda state: state["next_node"],
        { 
            "yes": "get_level_of_depression_node",
            "no": "ask_phq_9_node"
        }
    )
    builder.add_edge("get_level_of_depression_node", "problem_summary_node")

    builder.add_edge("problem_summary_node", "deep_support_node")
    builder.add_edge("deep_support_node", "get_user_deep_support_node")
    builder.add_edge("get_user_deep_support_node", "analyze_user_input_router")
    builder.add_conditional_edges(
        "analyze_user_input_router",
        lambda state: state["next_node"],
        { 
            "continue_deep_support": "deep_support_node",
            "move_to_step_6": "deep_support_summary_node"
        }
    )
    builder.add_edge("deep_support_summary_node", "ask_save_deep_node")
    builder.add_edge("ask_save_deep_node", "get_confirm_save_deep_node")
    builder.add_edge("get_confirm_save_deep_node", "check_save_deep_confirm_router")
    builder.add_conditional_edges(
        "check_save_deep_confirm_router",
        lambda state: state["next_node"],
        { 
            "yes": "save_deep_support_info_node",
            "no": "announce_move_to_step_6",
            "unrelevant": "ask_save_deep_node"
        }
    )
    builder.add_edge("save_deep_support_info_node", "announce_move_to_step_6")
    builder.add_edge("announce_move_to_step_6", "gentle_info_phase_node")
    builder.add_edge("gentle_info_phase_node", "get_user_gentle_phase_node")
    builder.add_edge("get_user_gentle_phase_node", "analyze_gentle_info_phase_router")
    builder.add_conditional_edges(
        "analyze_gentle_info_phase_router",
        lambda state: state["next_node"],
        { 
            "yes": "finish_node",
            "no": "gentle_info_phase_node",
        }
    )
    builder.add_edge("finish_node", END)
    
    memory = MemorySaver()
    
    graph = builder.compile(checkpointer=memory)

    return graph


def build_custom_graph() -> StateGraph:
    builder = StateGraph(ChatbotState)
    node = AgentNodes()
    router = RouterNode()
    
    builder.add_node("ask_save_deep_node", node.ask_save_deep_node)
    builder.add_node("save_deep_support_info_node", node.save_deep_support_info_node)
    builder.add_node("announce_move_to_step_6", node.announce_move_to_step_6)
    builder.add_node("gentle_info_phase_node", node.gentle_info_phase_node)
    builder.add_node("get_user_gentle_phase_node", node.get_user_gentle_phase_node)
    builder.add_node("finish_node", node.finish_node)
    
    builder.add_node("check_save_deep_confirm_router", router.check_save_deep_confirm_router)
    builder.add_node("analyze_gentle_info_phase_router", router.analyze_gentle_info_phase_router)
    
    builder.set_entry_point("check_save_deep_confirm_router")
    builder.add_conditional_edges(
        "check_save_deep_confirm_router",
        lambda state: state["next_node"],
        { 
            "yes": "save_deep_support_info_node",
            "no": "announce_move_to_step_6",
            "unrelevant": "ask_save_deep_node"
        }
    )
    builder.add_edge("save_deep_support_info_node", "announce_move_to_step_6")
    builder.add_edge("announce_move_to_step_6", "gentle_info_phase_node")
    builder.add_edge("gentle_info_phase_node", "get_user_gentle_phase_node")
    builder.add_edge("get_user_gentle_phase_node", "analyze_gentle_info_phase_router")
    builder.add_conditional_edges(
        "analyze_gentle_info_phase_router",
        lambda state: state["next_node"],
        { 
            "yes": "finish_node",
            "no": "gentle_info_phase_node",
        }
    )
    builder.add_edge("finish_node", END)
    
    memory = MemorySaver()
    
    graph = builder.compile(checkpointer=memory)

    return graph