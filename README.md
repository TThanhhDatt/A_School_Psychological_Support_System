# A School Psychological Support System

Hệ thống hỗ trợ tâm lý học đường là một nền tảng ứng dụng Chatbot AI hiện đại, được thiết kế để hỗ trợ sinh viên trong việc tư vấn tâm lý, đánh giá mức độ trầm cảm và cung cấp các giải pháp hỗ trợ tinh thần kịp thời.

## 🌟 Tính năng chính

- **Tư vấn tự động:** Sử dụng AI để lắng nghe và phản hồi các vấn đề tâm lý của sinh viên.
- **Đánh giá PHQ-9:** Tích hợp quy trình thực hiện bài kiểm tra trầm cảm tiêu chuẩn (Patient Health Questionnaire-9).
- **Phân tích chuyên sâu:** Khả năng nhận diện vấn đề và phân tích sâu sắc trạng thái cảm xúc để đưa ra lời khuyên phù hợp.
- **Quản lý hội thoại:** Hệ thống có khả năng ghi nhớ ngữ cảnh và điều phối luồng hội thoại linh hoạt dựa trên phản hồi của người dùng.

## 🏗 Kiến trúc dự án

Dự án được xây dựng theo mô hình Microservices phân tách rõ ràng:

### 1. Chatbot Backend (`Chatbot_Backend/Bot`)
- **Framework:** FastAPI.
- **Logic AI:** Sử dụng **LangGraph** để xây dựng biểu đồ trạng thái hội thoại (State Machine).
- **Cấu trúc Graph:**
  - `Greeting`: Chào hỏi.
  - `Problem Detect`: Nhận diện vấn đề ban đầu.
  - `PHQ-9 Assessment`: Quy trình kiểm tra trầm cảm.
  - `Deep Support`: Hỗ trợ chuyên sâu và đưa ra giải pháp.

### 2. Model API (`Chatbot_Backend/model_api`)
- Dịch vụ API riêng biệt chuyên xử lý các mô hình học máy và phân loại dữ liệu tâm lý, giúp tối ưu hóa hiệu suất xử lý cho Chatbot.

### 3. Chatbot Frontend (`Chatbot_Frontend`)
- **Framework:** React.js.
- **UI Component:** Sử dụng `react-chatbotify` để tạo giao diện trò chuyện mượt mà và thân thiện.

## 🛠 Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.12+, JavaScript.
- **Thư viện AI:** LangChain, LangGraph, OpenAI/Gemini API (tùy cấu hình).
- **Database:** MongoDB (lưu trữ thông tin sinh viên và lịch sử hỗ trợ).
- **API:** FastAPI (Backend), RESTful API.
- **Frontend:** React, CSS3, HTML5.

## 🚀 Hướng dẫn cài đặt

### Yêu cầu hệ thống
- Python 3.12 trở lên.
- Node.js & npm.
- MongoDB.

### Bước 1: Cài đặt Bot Backend
```bash
cd Chatbot_Backend/Bot
pip install -r requirements.txt
uvicorn main:app --reload --port 8000