from itertools import chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain.prompts import PromptTemplate
from langgraph.types import interrupt
from app.agents.core.state import ChatbotState
from app.agents.chain.therapy_chain import TherapyChain

import os
from dotenv import load_dotenv
import json

load_dotenv(override=True)

MODEL_NAME = os.getenv("MODEL_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHATBOT_NAME = os.getenv("CHATBOT_NAME")

class RouterNode:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GOOGLE_API_KEY
        )
        self.chain = TherapyChain()
        
    def check_problem_detected_router(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: check_problem_detected_router")
        
        # next_node_list = ["detected", "insufficient_info"]
        problem_detection = state["problem_detection"]
        status = problem_detection.get("status", "insufficient_info")
        next_node = "insufficient_info"
        
        if status in "detected":
            next_node = status
            print(f"> Problem found: {problem_detection}")
        else:
            next_node = status
            print(f"> Problem not found: {problem_detection}")
        
        state["nodes_flow"].append("check_problem_detected_router")
        state["next_node"] = next_node
        return state
    
    def check_problem_depth_analysis_router(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: check_problem_depth_analysis_router")
        
        next_node_list = ["move_to_step_5", "ask_PHQ9", "ask_other", "ask_emotion_check"]
        reason = state["problem_depth_analysis"].get("reason", None)
        next_step = state["problem_depth_analysis"].get("next_step", None)
        next_node = "ask_emotion_check"
        
        if reason is not None:
            if next_step in next_node_list:
                next_node = next_step
            else:
                print(f"> next_step not found: {next_step}")
        else:
            print(f"> Cannot find reason in problem_depth_analysis")
        
        state["nodes_flow"].append("check_problem_depth_analysis_router")
        state["next_node"] = next_node
        return state
    
    def check_full_phq9_answer_router(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_full_answer_router")
        next_node = "yes"
        
        phq9_progress = state["phq9_progress"]
        # Check if all of answers are collected
        for data in phq9_progress:
            if data["answer_text"] is None:
                next_node = "no"
                
        print(f"> Full phq9 answer or not: {next_node}")
        
        state["nodes_flow"].append("get_full_answer_router")
        state["next_node"] = next_node
        return state
    
    def analyze_user_input_router(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: analyze_user_input_router")
        next_node = "move_to_step_6"
        
        user_input = state["user_input"]
        student_summary = state["student_summary"]
        stress_level = state["stress_level"]
        last_support_direction = state["last_support_direction"] if state["last_support_direction"] else "Không có"
        chat_history = state["messages"][-10:]
        should_last_support = state["should_last_support"] if state["should_last_support"] else "Không có"
        
        result = self.chain.analyze_user_input().invoke({
            "chatbot_name": CHATBOT_NAME,
            "user_input": user_input,
            "student_summary": student_summary,
            "stress_level": stress_level,
            "last_support_direction": last_support_direction,
            "chat_history": chat_history,
            "should_last_support": should_last_support
        })
        
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "")
        print(f">>>>> data: {data}")
        data = json.loads(data)
        
        should_continue = data["should_continue"]
        if should_continue:
            next_node = "continue_deep_support"
        
        state["nodes_flow"].append("analyze_user_input_router")
        state["analyze_emotion"] = data["analyze_emotion"]
        state["analyze_bot_opinion"] = data["analyze_bot_opinion"]
        state["next_node"] = next_node
        return state
    
    def check_save_deep_confirm_router(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: check_save_deep_confirm_router")
        
        user_input = state["user_input"]
        last_question = state["messages"][-2].content
        next_node = "yes"
        
        result = self.chain.check_save_deep_confirm().invoke({
            "chatbot_name": CHATBOT_NAME,
            "user_input": user_input,
            "last_question": last_question
        })
        
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
        data = json.loads(data)
        
        if data["message"] is not None:
            state["messages"] = add_messages(state["messages"], [AIMessage(content=data["message"])])

        next_node = data["intent"]
        
        state["next_node"] = next_node
        state["nodes_flow"].append("check_save_deep_confirm_router")
        return state
    
    def analyze_gentle_info_phase_router(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: analyze_gentle_info_phase_router")
        next_node = "yes"
        
        max_question_gentle_phase = state["max_question_gentle_phase"]
        
        if max_question_gentle_phase > 0:
            user_input = state["user_input"]
            last_question = state["messages"][-2].content
            student_summary = state["student_summary"]
            deep_support_summary = state["deep_support_summary"]
            next_node = "no"
            
            result = self.chain.analyze_gentle_info_phase().invoke({
                "chatbot_name": CHATBOT_NAME,
                "max_question_gentle_phase": max_question_gentle_phase,
                "user_input": user_input,
                "last_question": last_question,
                "student_summary": student_summary,
                "deep_support_summary": deep_support_summary
            })

            data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
            data = json.loads(data)
            
            state["analyze_gentle_phase_opinion"] = data.get("analyze_answer", None)
            state["suggest_next_question_gentle_phase"] = data.get("suggest_next_question", None)
            
        
        state["next_node"] = next_node
        state["nodes_flow"].append("analyze_gentle_info_phase_router")
        return state