from typing import Optional, TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages
from sqlalchemy import Boolean

def get_phq_9_question() -> List[dict]:
    return [
        {
            "index": 1,
            "question": "Trong 2 tuần qua, bạn có cảm thấy ít hứng thú hoặc không còn thấy thích thú khi làm việc gì đó không?",
            "answer_text": None
        },
        {
            "index": 2,
            "question": "Trong 2 tuần qua, bạn có cảm thấy buồn, chán nản hoặc tuyệt vọng không?",
            "answer_text": None
        },
        {
            "index": 3,
            "question": "Trong 2 tuần qua, bạn có gặp khó khăn khi ngủ hoặc ngủ quá nhiều không?",
            "answer_text": None
        },
        {
            "index": 4,
            "question": "Trong 2 tuần qua, bạn có cảm thấy mệt mỏi hoặc thiếu năng lượng không?",
            "answer_text": None
        },
        {
            "index": 5,
            "question": "Trong 2 tuần qua, bạn có cảm thấy chán ăn hoặc ăn quá nhiều không?",
            "answer_text": None
        },
        {
            "index": 6,
            "question": "Trong 2 tuần qua, bạn có cảm thấy mình là người thất bại hoặc khiến bản thân hoặc gia đình thất vọng không?",
            "answer_text": None
        },
        {
            "index": 7,
            "question": "Trong 2 tuần qua, bạn có gặp khó khăn trong việc tập trung vào những việc như đọc sách hay xem TV không?",
            "answer_text": None
        },
        {
            "index": 8,
            "question": "Trong 2 tuần qua, bạn có di chuyển hoặc nói chậm hơn bình thường đến mức người khác có thể nhận thấy không? Hoặc ngược lại – cảm thấy bồn chồn hoặc không thể ngồi yên?",
            "answer_text": None
        },
        {
            "index": 9,
            "question": "Trong 2 tuần qua, bạn có nghĩ rằng thà chết còn hơn sống hoặc nghĩ đến việc tự làm hại bản thân không?",
            "answer_text": None
        }
    ]


class ChatbotState(TypedDict):
    student_id: Optional[str]
    student_name: Optional[str]
    
    user_input: str
    messages: Annotated[list, add_messages]
    next_node: Optional[str]
    nodes_flow: List[str]
    last_question: str
    
    problem_detection: Optional[dict]
    problem_depth_analysis: Optional[dict]
    problem_analysis_start_index: Optional[int]
    
    first_phq9: Optional[bool]
    phq9_progress: List[dict]
    phq9_index: Optional[int]
    stress_level: Optional[str]
    
    student_summary: Optional[str]
    
    last_support_direction: Optional[str]
    should_last_support: Optional[str]
    analyze_emotion: Optional[str]
    analyze_bot_opinion: Optional[str]
    
    deep_support_start_index: Optional[int]
    deep_support_summary: Optional[str]
    
    gentle_phase_start_index: Optional[int]
    max_question_gentle_phase: int
    analyze_gentle_phase_opinion: Optional[str]
    suggest_next_question_gentle_phase: Optional[str]
    
def init_chatbot_state() -> ChatbotState:
    return ChatbotState(
        student_id=None,
        student_name=None,
        
        user_input="",
        messages=[],  # dùng Annotated[list, add_messages]
        next_node=None,
        nodes_flow=[],
        last_question=None,
        
        problem_detection=None,
        problem_depth_analysis=None,
        problem_analysis_start_index=None,
        
        first_phq9=True,
        phq9_progress=get_phq_9_question(),
        phq9_index=None,
        stress_level=None,

        student_summary=None,
        
        last_support_direction=None,
        should_last_support=None,
        analyze_emotion=None,
        analyze_bot_opinion=None,
        
        deep_support_start_index=None,
        deep_support_summary=None,
        
        gentle_phase_start_index=None,
        max_question_gentle_phase=3,
        analyze_gentle_phase_opinion=None,
        suggest_next_question_gentle_phase=None
    )