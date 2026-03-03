import React, { useState, useRef, useEffect } from 'react';

function ChatWindow() {
  const [studentId, setStudentId] = useState('');
  const [studentName, setStudentName] = useState('');
  const [threadId, setThreadId] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [registered, setRegistered] = useState(false);
  const chatEndRef = useRef(null);

  // Tự động cuộn xuống khi có tin nhắn mới
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  // Đăng ký và lấy câu chào
  const handleRegister = async (e) => {
    e.preventDefault();
    const res = await fetch('https://schoolpsychologist-anvie-9572403057.asia-southeast1.run.app/api/v1/init_chatbot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, student_name: studentName }),
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let threadIdTemp = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop();
      for (let event of events) {
        if (event.startsWith('data:')) {
          const jsonStr = event.replace('data: ', '').trim();
          try {
            const msg = JSON.parse(jsonStr);
            if (msg.thread_id) threadIdTemp = msg.thread_id;
            if (msg.content) setMessages([{ text: msg.content, isBot: true }]);
          } catch (e) {}
        }
      }
    }
    setThreadId(threadIdTemp);
    setRegistered(true);
  };

  // Gửi tin nhắn
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { text: input, isBot: false }]);
    const res = await fetch('https://schoolpsychologist-anvie-9572403057.asia-southeast1.run.app/api/v1/interact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ thread_id: threadId, message: input })
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      // Mỗi event kết thúc bằng \n\n
      const events = buffer.split('\n\n');
      buffer = events.pop(); // giữ lại phần chưa hoàn chỉnh
      for (let event of events) {
        if (event.startsWith('data:')) {
          const jsonStr = event.replace('data: ', '').trim();
          try {
            const msg = JSON.parse(jsonStr);
            if (msg.content) {
              setMessages((prev) => [...prev, { text: msg.content, isBot: true }]);
            }
          } catch (e) {}
        }
      }
    }
    setInput('');
  };

  // Reset hội thoại
  const handleReset = async () => {
    const res = await fetch('https://schoolpsychologist-anvie-9572403057.asia-southeast1.run.app/api/v1/restart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, student_name: studentName }),
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let threadIdTemp = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop();
      for (let event of events) {
        if (event.startsWith('data:')) {
          const jsonStr = event.replace('data: ', '').trim();
          try {
            const msg = JSON.parse(jsonStr);
            if (msg.thread_id) threadIdTemp = msg.thread_id;
            if (msg.content) setMessages([{ text: msg.content, isBot: true }]);
          } catch (e) {}
        }
      }
    }
    setThreadId(threadIdTemp);
  };

  // UI
  if (!registered) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-indigo-400 to-cyan-300">
        <form
          onSubmit={handleRegister}
          className="bg-white p-8 rounded-2xl shadow-2xl flex flex-col items-center w-full max-w-sm"
        >
          <img
            src="/assets/images/image.jpg"
            alt="Bot Icon"
            className="w-24 h-24 mb-4 rounded-full shadow-lg border-4 border-indigo-200 bg-white"
          />
          <span className="text-2xl font-bold text-indigo-700 mb-2">AnVie Chatbot</span>
          <h2 className="mb-4 text-lg font-semibold text-gray-700 text-center">
            Chào mừng bạn đến với AnVie!<br />
            Vui lòng nhập MSSV và họ tên để bắt đầu trò chuyện nhé 😊
          </h2>
          <input
            type="text"
            placeholder="Mã số sinh viên (MSSV)"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            className="mb-3 p-3 border border-indigo-200 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
            required
          />
          <input
            type="text"
            placeholder="Họ và tên"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
            className="mb-5 p-3 border border-indigo-200 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
            required
          />
          <button
            type="submit"
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold w-full transition"
          >
            Bắt đầu trò chuyện
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-cyan-500 text-black">
      <div className="container mx-auto p-6 max-w-2xl">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold">AnVie - Trợ lý Tâm Lý Học Đường</h1>
          <button onClick={handleReset} className="px-4 py-2 bg-red-500 text-white rounded-full hover:bg-red-600">
            Reset
          </button>
        </div>
        <div className="border rounded-2xl shadow-xl p-6 bg-white transition-colors duration-300">
          <div className="h-96 overflow-y-auto mb-4 p-4 rounded-xl bg-opacity-50 backdrop-blur-sm">
            {messages.map((msg, idx) => (
              <div key={idx} className={`mb-4 flex ${msg.isBot ? 'justify-start' : 'justify-end'}`}>
                {msg.isBot && (
                  <img
                    src="/assets/images/image.jpg"
                    alt="Bot Icon"
                    className="w-8 h-8 rounded-full mr-2 shadow border border-indigo-200 bg-white"
                  />
                )}
                <div className={`inline-block p-3 rounded-xl max-w-xs ${msg.isBot ? 'bg-indigo-100 text-black' : 'bg-purple-200 text-black'}`}>
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Gõ tin nhắn nhé! 😊"
              className="flex-1 p-3 border rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-black border-gray-300"
            />
            <button
              onClick={handleSendMessage}
              className="p-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition"
            >
              ➤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
