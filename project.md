Phân tích Dự án: Hệ thống Hỗ trợ Tâm lý Học đường bằng AI
1. Phần Backend (Hệ thống xử lý máy chủ)
Phần Backend được chia làm 2 thành phần (service) chính: Bot Service (Quản lý logic Chatbot) và Model API Service (Xử lý dự đoán bằng Machine Learning). Cả hai đều được viết bằng Python và được cấu hình sẵn để triển khai lên cloud (có chứa tệp Procfile).

1.1. Bot Service (Chatbot_Backend/Bot/)
Đây là trái tim của hệ thống giao tiếp, chịu trách nhiệm quản lý luồng trò chuyện với học sinh, truy xuất cơ sở dữ liệu và định tuyến (routing) bằng AI Agent.

Kiến trúc LLM Agents (Core Routing & Graph):

Hệ thống sử dụng các framework quản lý luồng State/Graph tiên tiến (như LangGraph hoặc thư viện tương tự), thể hiện qua các file: graph.py, nodes.py, router.py, state.py.

Thay vì chat tự do thiếu kiểm soát, chatbot có các "node" (nút) công việc cụ thể và "router" để điều hướng trạng thái tâm lý của học sinh một cách an toàn.

Luồng Trị liệu / Tư vấn (Therapy Chain):
Được định nghĩa trong therapy_chain.py và điều khiển qua một loạt các Prompt (mẫu lệnh) rất chi tiết. Luồng tư vấn được thiết kế theo các bước bài bản của tâm lý học:

Khởi đầu: greeting_prompt.txt (Chào hỏi) -> ask_emotion_check_prompt.txt (Hỏi thăm cảm xúc).

Phát hiện vấn đề: proplem_detect_prompt.txt, followup_problem_detect_prompt.txt, analyze_user_input_prompt.txt.

Đánh giá tâm lý chuẩn Y khoa (PHQ-9): Hệ thống có tích hợp bài test PHQ-9 (Patient Health Questionnaire) - thang đo mức độ trầm cảm chuẩn quốc tế (phq9_questions.txt, ask_PHQ9_prompt.txt, analyze_PHQ9_prompt.txt).

Hỗ trợ chuyên sâu: Nếu phát hiện vấn đề nặng, bot sẽ chuyển sang các bước hỗ trợ sâu hơn (deep_support_prompt.txt, emotion_support_prompt.txt) và có cơ chế xác nhận lưu trữ thông tin nhạy cảm (ask_for_save_deep_support_prompt.txt).

Tổng kết: problem_summary_prompt.txt và finish_prompt.txt.

Cơ sở dữ liệu (Database) & Controllers:

Sử dụng MongoDB làm cơ sở dữ liệu (app/database/mongo.py).

Quản lý thông tin và lịch sử của học sinh qua mô hình MVC thu gọn: students_model.py và students_controller.py.

API Framework:

Quản lý các điểm cuối (endpoints) qua chatbot_router.py. Rất có thể dự án dùng FastAPI hoặc Flask để build RESTful API giao tiếp với Frontend.

1.2. Model API Service (Chatbot_Backend/model_api/)
Service này được tách riêng độc lập hoàn toàn khỏi luồng Chatbot để đảm bảo hiệu suất.

Chức năng: Nhận dữ liệu văn bản từ Bot Service, chạy mô hình AI đã được huấn luyện sẵn và trả về kết quả dự đoán (ví dụ: xác suất mắc trầm cảm, phân loại cảm xúc).

Cấu trúc xử lý:

Core Logic: Hàm dự đoán chính nằm ở app/core/predict_function.py (load mô hình, xử lý text đầu vào và infer kết quả).

Services & Routes: API endpoint được định nghĩa tại routes.py, gọi logic xử lý thông qua services.py.

2. Phần Huấn luyện Mô hình (Model Training)
Toàn bộ quá trình huấn luyện và nghiên cứu (Research) được đặt trong thư mục Model_DepressionClassification. Trọng tâm là tệp Notebook DepressionClassification_o3.ipynb.

Dựa vào mục đích của hệ thống học đường, quy trình huấn luyện mô hình phân loại trầm cảm (Depression Classification) diễn ra với các đặc điểm kỹ thuật cụ thể sau:

Mục tiêu bài toán: Text Classification (Phân loại văn bản/ngôn ngữ tự nhiên). Mô hình sẽ đọc các dòng tâm sự, câu trả lời của học sinh (hoặc kết quả từ bộ test PHQ-9) để phân loại mức độ trầm cảm (VD: Bình thường, Nhẹ, Vừa, Nặng, Rất nặng).

Quy trình chuẩn trong Notebook (.ipynb):

Data Preprocessing (Tiền xử lý dữ liệu): Làm sạch văn bản, loại bỏ ký tự đặc biệt, chuẩn hóa chữ viết (lowercase), tokenization (tách từ), và loại bỏ stop-words (từ dừng).

Feature Extraction / Word Embedding (Trích xuất đặc trưng): Biến đổi văn bản thành vector toán học. Có thể sử dụng các kỹ thuật như TF-IDF, Word2Vec, hoặc các mô hình mạnh mẽ hơn như PhoBERT/BERT để hiểu ngữ cảnh câu.

Model Training (Huấn luyện): Đưa vector dữ liệu vào các thuật toán Machine Learning hoặc Deep Learning. Vì đây là bài toán phân loại văn bản liên quan đến sức khỏe tâm thần, mô hình thường là SVM, Random Forest, hoặc LSTM/Transformer.

Evaluation (Đánh giá): Kiểm tra độ chính xác của mô hình thông qua các ma trận nhầm lẫn (Confusion Matrix) và các chỉ số đo lường như Accuracy, Precision, Recall và F1-Score (Đặc biệt quan tâm đến Recall để không bỏ sót các trường hợp học sinh có dấu hiệu trầm cảm nặng).

Xuất mô hình: Sau khi huấn luyện thành công ở Notebook này, mô hình (model weights / .pkl hoặc .h5) sẽ được lưu lại và import vào tệp predict_function.py bên trong phần Model API phía trên để phục vụ thực tế (Production).

💡 Đánh giá tổng quan về kiến trúc dự án:
Thiết kế chuyên nghiệp: Việc tách biệt giữa Chatbot Logic (LLM) và Machine Learning API là một best-practice (tiêu chuẩn tốt) trong thiết kế hệ thống AI, giúp hệ thống không bị "thắt cổ chai" khi tải nặng.

Tính khoa học & Y tế: Dự án không chỉ dùng AI để chat phiếm mà có sự kết hợp của kiến thức chuyên ngành tâm lý học (Tích hợp đánh giá PHQ-9, chia Phase phân tích sâu).

Bảo mật thông tin: Có các flow yêu cầu sự cho phép lưu trữ dữ liệu nhạy cảm (check_save_deep_confirm_prompt.txt), chứng tỏ dự án rất quan tâm đến quyền riêng tư của học sinh.