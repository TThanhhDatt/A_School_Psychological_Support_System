import React, { useState, useRef, useEffect } from 'react';

// Typing indicator animation component
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1">
      <div className="w-2 h-2 rounded-full bg-sage-400 animate-pulse"></div>
      <div className="w-2 h-2 rounded-full bg-sage-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
      <div className="w-2 h-2 rounded-full bg-sage-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
    </div>
  );
}

function ChatWindow() {
  const [studentId, setStudentId] = useState('');
  const [studentName, setStudentName] = useState('');
  const [threadId, setThreadId] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [registered, setRegistered] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  // Register and get greeting
  const handleRegister = async (e) => {
    e.preventDefault();
    if (!studentId.trim() || !studentName.trim()) return;
    
    setIsLoading(true);
    try {
      const res = await fetch('https://schoolpsychologist-anvie-9572403057.asia-southeast1.run.app/api/v1/init_chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId, student_name: studentName }),
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let threadIdTemp = '';
      
      setIsTyping(true);
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
      setIsTyping(false);
    } catch (error) {
      console.error('Registration error:', error);
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  // Send message
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    setMessages((prev) => [...prev, { text: input, isBot: false }]);
    setInput('');
    setIsTyping(true);
    
    try {
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
        const events = buffer.split('\n\n');
        buffer = events.pop();
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
      setIsTyping(false);
    } catch (error) {
      console.error('Send message error:', error);
      setIsTyping(false);
    }
  };

  // Reset conversation
  const handleReset = async () => {
    try {
      const res = await fetch('https://schoolpsychologist-anvie-9572403057.asia-southeast1.run.app/api/v1/restart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId, student_name: studentName }),
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let threadIdTemp = '';
      
      setMessages([]);
      setIsTyping(true);
      
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
      setIsTyping(false);
    } catch (error) {
      console.error('Reset error:', error);
      setIsTyping(false);
    }
  };

  // Privacy & Disclaimer Screen
  if (showPrivacy) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-sky-50 to-emerald-50 px-4 md:px-6">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-3xl shadow-lg p-8 md:p-10 animate-fadeIn">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-sky-100 to-emerald-100 flex items-center justify-center text-4xl">
                💚
              </div>
              <h1 className="text-3xl font-bold text-slate-800 mb-2">AnVie</h1>
              <p className="text-slate-600 text-sm">Trợ lý Tâm Lý Học Đường</p>
            </div>

            {/* Privacy Notice */}
            <div className="bg-sky-50 border border-sky-200 rounded-2xl p-6 mb-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
                <span>🔒</span> Thông Báo Bảo Mật
              </h2>
              <ul className="space-y-3 text-sm text-slate-700">
                <li className="flex gap-3">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span>Tất cả cuộc trò chuyện của bạn được <strong>bảo mật tuyệt đối</strong></span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span>Chúng tôi <strong>không lưu trữ thông tin cá nhân</strong> của bạn</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span>Bạn có thể <strong>yên tâm chia sẻ</strong> mọi cảm xúc</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-emerald-500 font-bold">✓</span>
                  <span><strong>Không có ai</strong> có thể nhìn thấy cuộc trò chuyện này</span>
                </li>
              </ul>
            </div>

            {/* Important Notice */}
            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6">
              <p className="text-xs text-slate-700 leading-relaxed">
                ⚠️ <strong>Lưu ý:</strong> AnVie là một trợ lý hỗ trợ tâm lý, không phải một bác sĩ. Nếu bạn gặp tình trạng khẩn cấp, vui lòng liên hệ ngay với bác sĩ hoặc đường dây hỗ trợ tâm lý.
              </p>
            </div>

            {/* Action Button */}
            <button
              onClick={() => setShowPrivacy(false)}
              className="w-full bg-gradient-to-r from-sky-400 to-emerald-400 hover:from-sky-500 hover:to-emerald-500 text-white font-semibold py-3 px-6 rounded-full transition duration-300 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              Tôi hiểu, Bắt đầu nào 💙
            </button>

            {/* Emergency Resources */}
            <p className="text-xs text-slate-500 text-center mt-6">
              Cần giúp đỡ ngay? Gọi <strong>1800-1234</strong> hoặc nhắn tin cho Tâm lý viên
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Registration Screen
  if (!registered) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-sky-50 to-emerald-50 px-4 md:px-6 animate-fadeIn">
        <form
          onSubmit={handleRegister}
          className="bg-white p-8 md:p-10 rounded-3xl shadow-lg flex flex-col items-center w-full max-w-sm"
        >
          <div className="w-24 h-24 mb-6 rounded-full bg-gradient-to-br from-sky-100 to-emerald-100 flex items-center justify-center text-5xl shadow-md">
            💚
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2 text-center">AnVie</h1>
          <p className="text-sm text-slate-600 mb-6 text-center">Trợ lý Tâm Lý Học Đường</p>
          
          <h2 className="mb-6 text-base font-medium text-slate-700 text-center leading-relaxed">
            Chào mừng bạn! 👋<br />
            <span className="text-slate-600">Vui lòng nhập thông tin để bắt đầu</span>
          </h2>

          <input
            type="text"
            placeholder="Mã số sinh viên (MSSV)"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            className="mb-4 p-3 border border-slate-200 rounded-xl w-full focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent transition bg-slate-50 text-slate-800 placeholder-slate-400"
            required
          />
          <input
            type="text"
            placeholder="Họ và tên"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
            className="mb-6 p-3 border border-slate-200 rounded-xl w-full focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent transition bg-slate-50 text-slate-800 placeholder-slate-400"
            required
          />

          <button
            type="submit"
            disabled={isLoading}
            className="bg-gradient-to-r from-sky-400 to-emerald-400 hover:from-sky-500 hover:to-emerald-500 disabled:opacity-50 text-white px-6 py-3 rounded-full font-semibold w-full transition duration-300 shadow-md hover:shadow-lg transform hover:scale-105"
          >
            {isLoading ? 'Đang tải...' : 'Bắt đầu trò chuyện'}
          </button>

          <p className="text-xs text-slate-500 text-center mt-6">
            Thông tin của bạn được bảo mật hoàn toàn
          </p>
        </form>
      </div>
    );
  }

  // Main Chat Screen
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-emerald-50">
      <div className="container mx-auto p-4 md:p-6 max-w-3xl h-screen flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center mb-6 pt-2">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-800">AnVie</h1>
            <p className="text-sm text-slate-600">Trợ lý Tâm Lý Học Đường</p>
          </div>
          <div className="flex gap-2">
            {/* Panic Button */}
            <button
              onClick={() => {
                window.open('tel:1800-1234');
              }}
              className="p-3 bg-red-100 hover:bg-red-200 text-red-600 rounded-full transition duration-300 flex items-center justify-center text-xl shadow-sm hover:shadow-md"
              title="Emergency Support"
            >
              🆘
            </button>
            {/* Reset Button */}
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-full font-medium transition duration-300 shadow-sm hover:shadow-md text-sm md:text-base"
            >
              Làm mới
            </button>
          </div>
        </div>

        {/* Chat Messages Container */}
        <div className="flex-1 bg-white rounded-3xl shadow-sm p-4 md:p-6 mb-4 overflow-y-auto flex flex-col">
          {messages.length === 0 && !isTyping && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-5xl mb-4">💭</div>
              <p className="text-slate-700 font-medium mb-2">Bắt đầu cuộc trò chuyện</p>
              <p className="text-slate-500 text-sm max-w-xs">Chia sẻ bất kỳ điều gì bạn muốn, AnVie đây để lắng nghe 💚</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-4 flex ${msg.isBot ? 'justify-start' : 'justify-end'} animate-fadeIn`}>
              {msg.isBot && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-200 to-emerald-200 flex items-center justify-center text-lg mr-2 flex-shrink-0">
                  💚
                </div>
              )}
              <div className={`inline-block max-w-xs px-4 py-3 rounded-2xl ${
                msg.isBot 
                  ? 'bg-emerald-100 text-slate-800' 
                  : 'bg-sky-400 text-white'
              }`}>
                <p className="text-sm md:text-base leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="mb-4 flex justify-start animate-fadeIn">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-200 to-emerald-200 flex items-center justify-center text-lg mr-2 flex-shrink-0">
                💚
              </div>
              <div className="bg-emerald-100 text-slate-800 px-4 py-3 rounded-2xl">
                <TypingIndicator />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex items-center gap-2 md:gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
            placeholder="Gõ tin nhắn..."
            className="flex-1 p-3 md:p-4 border border-slate-200 rounded-full focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent transition bg-white text-slate-800 placeholder-slate-400 text-sm md:text-base"
            disabled={isTyping}
          />
          <button
            onClick={handleSendMessage}
            disabled={isTyping || !input.trim()}
            className="p-3 md:p-4 bg-gradient-to-r from-sky-400 to-emerald-400 hover:from-sky-500 hover:to-emerald-500 disabled:opacity-50 text-white rounded-full transition duration-300 shadow-md hover:shadow-lg transform hover:scale-110 flex-shrink-0 flex items-center justify-center"
          >
            ✈️
          </button>
        </div>
      </div>

      {/* Emergency Resources Banner */}
      <div className="fixed bottom-0 left-0 right-0 bg-red-50 border-t border-red-200 px-4 py-2 text-center">
        <p className="text-xs md:text-sm text-red-700">
          <span className="font-semibold">Cần giúp đỡ ngay?</span> Gọi <span className="font-bold">1800-1234</span> | <a href="sms:0987654321" className="underline hover:no-underline">Nhắn tin</a>
        </p>
      </div>
    </div>
  );
}

export default ChatWindow;
