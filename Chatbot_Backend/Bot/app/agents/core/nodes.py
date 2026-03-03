import requests
from httpx import request
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

from app.controllers.students_controller import create_student
from app.models.students_model import Student

load_dotenv(override=True)

MODEL_NAME = os.getenv("MODEL_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHATBOT_NAME = os.getenv("CHATBOT_NAME")
MODEL_URI = os.getenv("MODEL_URI")

class AgentNodes:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GOOGLE_API_KEY
        )
        self.chain = TherapyChain()
        
    def greeting_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: greeting_node")
        result = self.chain.greeting().invoke(CHATBOT_NAME).content

        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        state["nodes_flow"].append("greeting_node")
        state["last_question"] = result
        return state
    
    def get_user_problem_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_user_problem_node")
        
        user_input = interrupt(None)
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        state["user_input"] = user_input
        state["nodes_flow"].append("get_user_problem_node")
        return state
        
    def get_problem_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: problem_detection")
        
        user_input = state["user_input"]
        last_question = state["last_question"]
        messages = state["messages"]
        previous_message = [{
            "role": mess.type,
            "message": mess.content
        } for mess in messages]
        
        result = self.chain.proplem_detect().invoke({
            "chatbot_name": CHATBOT_NAME,
            "previous_message": previous_message,
            "user_input": user_input,
            "last_question": last_question
        })
        
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
        data = json.loads(data)
        state["problem_detection"] = data
        state["nodes_flow"].append("problem_detection")
        return state
    
    def followup_problem_detect_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: followup_problem_detect_node")
        
        problem_detection = state["problem_detection"]
        user_input = state["user_input"]
        messages = state["messages"]
        previous_message = [{
            "role": mess.type,
            "message": mess.content
        } for mess in messages]
        
        result = self.chain.followup_problem_detect().invoke({
            "chatbot_name": CHATBOT_NAME,
            "previous_message": previous_message,
            "bot_input": problem_detection,
            "user_input": user_input,
        }).content
        
        state["last_question"] = result
        state["nodes_flow"].append("followup_problem_detect_node")
        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        return state
    
    def emotion_support_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: emotion_support_node")
        
        problem_detection = state["problem_detection"]
        user_input = state["user_input"]
        
        result = self.chain.emotion_support().invoke({
            "chatbot_name": CHATBOT_NAME,
            "problem_detection": problem_detection,
            "user_input": user_input,
        }).content
        
        state["last_question"] = result
        state["nodes_flow"].append("emotion_support_node")
        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        return state
    
    def get_user_emotion_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_user_emotion_node")
        
        user_input = interrupt(None)
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        state["user_input"] = user_input
        state["nodes_flow"].append("get_user_emotion_node")
        return state
    
    def problem_depth_analysis_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: problem_depth_analysis_node")
        
        user_input = state["user_input"]
        last_question = state["last_question"]
        problem_detection = state["problem_detection"]
        messages = state["messages"][-5:]
        last_5_chat_history = [{
            "role": mess.type,
            "message": mess.content
        } for mess in messages]
        
        result = self.chain.problem_depth_analysis().invoke({
            "chatbot_name": CHATBOT_NAME,
            "user_input": user_input,
            "last_question": last_question,
            "last_5_chat_history": last_5_chat_history,
            "problem_detection": problem_detection,
        })
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
        data = json.loads(data)
        
        print(f"> Promblem depth analysis: {data}")
        
        state["nodes_flow"].append("problem_depth_analysis_node")
        state["problem_depth_analysis"] = data
        state["problem_analysis_start_index"] = len(state["messages"]) - 1
        return state
    
    def ask_emotion_check_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: ask_emotion_check_node")
        
        user_input = state["user_input"]
        reason = state["problem_depth_analysis"].get("reason", None)
        messages = state["messages"][-5:]
        last_5_chat_history = [{
            "role": mess.type,
            "message": mess.content
        } for mess in messages]
        
        result = self.chain.ask_emotion_check().invoke({
            "chatbot_name": CHATBOT_NAME,
            "user_input": user_input,
            "last_5_chat_history": last_5_chat_history,
            "reason": reason
        })
        
        question = result.content
        
        print(f"> Ask emotion check question: {question}")
        
        state["nodes_flow"].append("ask_emotion_check_node")
        state["last_question"] = question
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question)])
        return state

    def ask_other_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: ask_other_node")
        
        user_input = state["user_input"]
        reason = state["problem_depth_analysis"].get("reason", None)
        messages = state["messages"][-5:]
        last_5_chat_history = [{
            "role": mess.type,
            "message": mess.content
        } for mess in messages]
        
        result = self.chain.ask_other().invoke({
            "chatbot_name": CHATBOT_NAME,
            "user_input": user_input, 
            "last_5_chat_history": last_5_chat_history,
            "reason": reason
        })
        
        question = result.content
        
        print(f"> Ask emotion check question: {question}")
        
        state["nodes_flow"].append("ask_other_node")
        state["last_question"] = question
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question)])
        return state
    
    def _get_phq_9_question(self, state: ChatbotState) -> dict:
        phq9_progress = state["phq9_progress"]
        question = ""
        index = 0
        
        for data in phq9_progress:
            if data["answer_text"] is None:
                question = data["question"]
                index = data["index"]
                break
            
        return {
            "index": index,
            "question": question
        }
    
    def ask_phq_9_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: ask_phq_9_node")
        
        user_input = state["user_input"]
        reason = state["problem_depth_analysis"].get("reason", None)
        first_phq9 = state["first_phq9"]
        messages = state["messages"][-10:]
        last_10_chat_history = [{
            "role": mess.type,
            "message": mess.content
        } for mess in messages]
        phq9_question = self._get_phq_9_question(state=state)
        
        
        result = self.chain.ask_PHQ9().invoke({
            "chatbot_name": CHATBOT_NAME,
            "first_phq9": first_phq9,
            "user_input": user_input, 
            "last_10_chat_history": last_10_chat_history,
            "reason": reason,
            "phq9_question": phq9_question["question"]
        })
        
        question = result.content
        
        print(f"> Origin PHQ9 question: {phq9_question["question"]}")
        print(f"> Ask PHQ-9 question: {question}")
        
        state["nodes_flow"].append("ask_phq_9_node")
        state["phq9_index"] = phq9_question["index"]
        state["first_phq9"] = False
        state["last_question"] = question
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question)])
        return state
        
    def get_user_answer_phq9_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_user_answer_phq9_node")
        
        user_input = interrupt(None)
        
        index = state["phq9_index"]
        state["phq9_progress"][index - 1]["answer_text"] = user_input
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        state["nodes_flow"].append("get_user_answer_phq9_node")
        return state
    
    def get_level_of_depression_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_level_of_depression_node")
        
        phq9_progress = state["phq9_progress"]
        user_answer = ""
        for item in phq9_progress:
            user_answer += f"{item["answer_text"]}\n"
        
        stress_level = self._call_model_api(user_answer)
        print(f">>>>> Stress level: {stress_level}")
        
        state["stress_level"] = stress_level
        state["nodes_flow"].append("get_level_of_depression_node")
        return state
    
    def _call_model_api(self, text: str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }
        
        response = requests.post(MODEL_URI, json=payload, headers=headers)
        
        return response.json()

    
    def problem_summary_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: problem_summary_node")
        
        start_index = state["problem_analysis_start_index"]
        dialogues = state["messages"][start_index:]
        stress_level = state["stress_level"] if state["stress_level"] else "Không có"
        
        data = [
            {
                "type": dialogue.type,
                "content": dialogue.content
            }
            for dialogue in dialogues
        ]
        
        result = self.chain.problem_summary().invoke({
            "dialogue": data,
            "stress_level": stress_level
        })
        
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
        data = json.loads(data)
        
        state["deep_support_start_index"] = len(state["messages"]) - 1
        state["student_summary"] = data
        state["nodes_flow"].append("problem_summary_node")
        return state
    
    def deep_support_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: deep_support_node")
        
        student_summary = state["student_summary"]
        stress_level = state["stress_level"]
        chat_history = state["messages"][-10:]
        last_support_direction = state["last_support_direction"] if state["last_support_direction"] else "Không có"
        analyze_emotion = state["analyze_emotion"] if state["analyze_emotion"] else "Không có"
        analyze_bot_opinion = state["analyze_bot_opinion"] if state["analyze_bot_opinion"] else "Không có"
        
        result = self.chain.deep_support().invoke({
            "chatbot_name": CHATBOT_NAME,
            "student_summary": student_summary,
            "stress_level": stress_level,
            "chat_history": chat_history,
            "last_support_direction": last_support_direction,
            "analyze_emotion": analyze_emotion,
            "analyze_bot_opinion": analyze_bot_opinion
        })
        
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
        data = json.loads(data)
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=data["support"])])
        state["last_support_direction"] = data["last_support_direction"]
        state["should_last_support"] = data["should_last_support"]
        state["nodes_flow"].append("deep_support_node")
        return state
    
    def get_user_deep_support_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_user_deep_support_node")
        
        user_input = interrupt(None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        state["nodes_flow"].append("get_user_deep_support_node")
        return state
    
    def deep_support_summary_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: deep_support_summary_node")
        
        start_index = state["deep_support_start_index"]
        dialogues = state["messages"][start_index:]
        stress_level = state["stress_level"] if state["stress_level"] else "Không có"
        student_summary = state["student_summary"]
        
        chat_data = [
            {
                "type": dialogue.type,
                "content": dialogue.content
            }
            for dialogue in dialogues
        ]
        
        result = self.chain.deep_support_summary().invoke({
            "chatbot_name": CHATBOT_NAME,
            "dialogue": chat_data,
            "stress_level": stress_level,
            "student_summary": student_summary
        })
        
        data = result.content.replace("```json", "").replace("```", "").replace("\n", "").strip()
        data = json.loads(data)
        
        state["deep_support_start_index"] = len(state["messages"]) - 1
        state["deep_support_summary"] = data
        state["nodes_flow"].append("deep_support_summary_node")
        return state
    
    def ask_save_deep_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: ask_save_deep_node")
        
        result = self.chain.ask_for_save_deep_support().invoke({
            "chatbot_name": CHATBOT_NAME,
        }).content
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        state["nodes_flow"].append("ask_save_deep_node")
        return state
    
    def get_confirm_save_deep_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_confirm_save_deep_node")
        
        user_input = interrupt(None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        state["nodes_flow"].append("get_confirm_save_deep_node")
        return state
    
    def save_deep_support_info_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: save_deep_support_info_node")
        msg = (
            "Có một chút lỗi khi lưu thông tin rồi, nhưng không sao đâu, mình sẽ thử lại sau nha.\n"
            "Điều quan trọng là mình và bạn vẫn có thể tiếp tục hành trình cùng nhau 💪"
        )
        
        student = Student(
            student_name=state["student_name"],
            student_id = state["student_id"],
            phq_progress = state["phq9_progress"],
            stress_level = state["stress_level"],
            problem_detection = state["problem_detection"],
            student_summary = state["student_summary"],
            deep_support_summary = state["deep_support_summary"]
        )
        
        return_student = create_student(student)
        if return_student.get("id", None):
            msg = (
                "Mình vừa lưu xong thông tin rồi đó 📝 "
                "Cảm ơn bạn đã chờ mình nhé!\n"
                "Giờ thì cùng nhau tiếp tục nào~"
            )
        
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=msg)])
        state["nodes_flow"].append("save_deep_support_info_node")
        return state
    
    def announce_move_to_step_6(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: announce_move_to_step_6")
        
        student_summary = state["student_summary"]
        deep_support_summary = state["deep_support_summary"]
        stress_level = state["stress_level"]
        
        result = self.chain.announce_move_to_step_6().invoke({
            "chatbot_name": CHATBOT_NAME,
            "student_summary": student_summary,
            "deep_support_summary": deep_support_summary,
            "stress_level": stress_level
        }).content
        
        state["gentle_phase_start_index"] = len(state["messages"]) - 1
        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        state["nodes_flow"].append("announce_move_to_step_6")
        return state
    
    def gentle_info_phase_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: gentle_info_phase_node")
        
        max_question_gentle_phase = state["max_question_gentle_phase"]
        student_summary = state["student_summary"]
        deep_support_summary = state["deep_support_summary"]
        stress_level = state["stress_level"] if state["stress_level"] else "Không có"
        chat_histories = state["messages"]
        analyze_gentle_phase_opinion = state["analyze_gentle_phase_opinion"] if state["analyze_gentle_phase_opinion"] else "Không có"
        suggest_next_question_gentle_phase = state["suggest_next_question_gentle_phase"] if state["suggest_next_question_gentle_phase"] else "Không có"
        
        result = self.chain.gentle_info_phase().invoke({
            "chatbot_name": CHATBOT_NAME,
            "max_question_gentle_phase": max_question_gentle_phase,
            "student_summary": student_summary,
            "deep_support_summary": deep_support_summary,
            "stress_level": stress_level,
            "chat_histories": chat_histories,
            "analyze_gentle_phase_opinion": analyze_gentle_phase_opinion,
            "suggest_next_question_gentle_phase": suggest_next_question_gentle_phase
        }).content
        
        state["max_question_gentle_phase"] -= 1
        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        state["nodes_flow"].append("gentle_info_phase_node")
        return state
    
    def get_user_gentle_phase_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: get_user_gentle_phase_node")
        
        user_input = interrupt(None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        state["nodes_flow"].append("get_user_gentle_phase_node")
        return state
    
    def finish_node(self, state: ChatbotState) -> ChatbotState:
        print(f"> Node: finish_node")
        
        student_summary = state["student_summary"]
        deep_support_summary = state["deep_support_summary"]
        stress_level = state["stress_level"] if state["stress_level"] else "Không có"
        chat_histories = state["messages"]
        
        result = self.chain.finish().invoke({
            "chatbot_name": CHATBOT_NAME,
            "student_summary": student_summary,
            "deep_support_summary": deep_support_summary,
            "stress_level": stress_level,
            "chat_histories": chat_histories,
        }).content
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=result)])
        state["nodes_flow"].append("finish_node")
        return state
    