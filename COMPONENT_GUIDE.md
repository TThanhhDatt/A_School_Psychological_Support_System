# Component Guide - AnVie Chatbot

## Overview

The AnVie chatbot interface consists of a single main component (`ChatWindow.js`) that manages the complete user flow with three distinct screens. This guide explains each component and its functionality.

## Main Component: ChatWindow.js

### Component Tree
```
ChatWindow (main state container)
├── Privacy Disclaimer Screen
│   ├── Header (Logo + Title)
│   ├── Security Notice Card
│   ├── Important Disclaimer
│   └── Action Button
├── Registration Screen
│   ├── Logo & Welcome Message
│   ├── Form Inputs
│   │   ├── Student ID Input
│   │   └── Student Name Input
│   └── Submit Button
└── Chat Screen
    ├── Header
    │   ├── Title & Subtitle
    │   ├── Panic Button (🆘)
    │   └── Reset Button
    ├── Messages Container
    │   ├── Empty State (when no messages)
    │   ├── Message List
    │   │   ├── Bot Message (with avatar)
    │   │   ├── Student Message
    │   │   └── Typing Indicator
    │   └── Auto-scroll ref
    ├── Input Section
    │   ├── Message Input Field
    │   └── Send Button
    └── Emergency Banner (fixed bottom)
```

## Screen States

### 1. Privacy Disclaimer Screen

**Purpose**: First impression - establish trust and privacy assurance

**State Variables**:
- `showPrivacy`: boolean (true initially)

**Key Features**:
- Non-dismissible without acknowledgment
- Clear security guarantees with checkmarks
- Emergency hotline visibility
- Welcoming tone with emoji

**Layout**:
```
[Background gradient: sky-50 to emerald-50]
┌─────────────────────────────┐
│                             │
│     [Logo - Heart Emoji]    │
│     AnVie                   │
│     Trợ lý Tâm Lý Học Đường│
│                             │
│  ┌─────────────────────┐   │
│  │ 🔒 Thông Báo Bảo Mật│   │
│  │ ✓ Bảo mật tuyệt đối │   │
│  │ ✓ Không lưu trữ     │   │
│  │ ✓ Yên tâm chia sẻ   │   │
│  │ ✓ Không ai thấy     │   │
│  └─────────────────────┘   │
│                             │
│  [⚠️ Important Notice]       │
│                             │
│  [Button: Tôi hiểu, Bắt...]│
│                             │
└─────────────────────────────┘
```

### 2. Registration Screen

**Purpose**: Collect student identification for session management

**State Variables**:
- `studentId`: string
- `studentName`: string
- `registered`: boolean (false initially)
- `isLoading`: boolean (during API call)

**Key Features**:
- Form validation (required fields)
- Loading state on submit
- Clear labeling and placeholders
- Privacy reassurance below submit

**Components Used**:
- Form element
- Two text inputs with error handling
- Submit button with loading state

**Styling Classes**:
- `text-center`: Center alignment
- `bg-white rounded-3xl shadow-lg`: Card styling
- `animate-fadeIn`: Smooth entrance
- `p-8 md:p-10`: Responsive padding

### 3. Chat Screen

**Purpose**: Main interaction space for student-bot conversation

**State Variables**:
- `messages`: array of {text, isBot} objects
- `input`: string (current user input)
- `threadId`: string (from API)
- `isTyping`: boolean (bot response state)

#### 3a. Header Section

**Elements**:
- Title: "AnVie" (bold, primary text)
- Subtitle: "Trợ lý Tâm Lý Học Đường" (secondary text)
- Panic Button (🆘): Emergency hotline trigger
- Reset Button: Clear conversation

**Styling**:
```javascript
className="flex justify-between items-center mb-6 pt-2"
```

**Key Interactions**:
- Panic button: Opens phone dialer (tel: link)
- Reset button: Calls `handleReset()` function

#### 3b. Message Container

**Features**:
- Auto-scrolling to latest message
- Typing indicator during bot response
- Empty state when conversation starts
- Message differentiation by sender

**Message Structure**:
```javascript
{
  text: "Message content",
  isBot: true/false
}
```

**Empty State Display**:
```
    💭
Bắt đầu cuộc trò chuyện
Chia sẻ bất kỳ điều gì bạn muốn...
```

**Message Styling**:

Bot Message:
- Avatar: Heart emoji in gradient circle
- Background: `bg-emerald-100` (soft green)
- Text: `text-slate-800` (dark text)
- Alignment: Left-aligned with avatar

Student Message:
- Background: `bg-sky-400` (calming blue)
- Text: `text-white` (white for contrast)
- Alignment: Right-aligned

Typing Indicator:
- Three animated dots
- Pulse animation (1.5s duration)
- Staggered delays (0s, 0.2s, 0.4s)

**Component**: `TypingIndicator()`
```javascript
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1">
      <div className="w-2 h-2 rounded-full bg-sage-400 animate-pulse"></div>
      // ... (staggered delays for each dot)
    </div>
  );
}
```

#### 3c. Input Section

**Elements**:
- Text input field
- Send button

**Input Styling**:
- Rounded full (rounded-full) for friendly appearance
- Focus ring: `focus:ring-2 focus:ring-emerald-400`
- Full width with padding
- Placeholder: "Gõ tin nhắn..."
- Disabled state when `isTyping` is true

**Send Button**:
- Gradient background (sky-400 to emerald-400)
- Airplane emoji (✈️)
- Scale animation on hover (105%)
- Disabled when input is empty or typing

**Keyboard Support**:
- Enter key: Submit message (except Shift+Enter)
- Input tracking via `onChange` handler

#### 3d. Emergency Banner

**Location**: Fixed at bottom of screen

**Content**:
```
⚠️ Cần giúp đỡ ngay? Gọi 1800-1234 | Nhắn tin
```

**Styling**:
- Red accent: `bg-red-50 border-red-200`
- Always visible for safety
- Responsive font sizing

**Links**:
- Phone: `tel:1800-1234`
- SMS: `sms:0987654321`

## API Integration

### Endpoints

**1. Initialize Chatbot**
```
POST /api/v1/init_chatbot
Body: { student_id, student_name }
Response: Stream of messages with thread_id
```

**2. Send Message**
```
POST /api/v1/interact
Body: { thread_id, message }
Response: Stream of bot responses
```

**3. Restart Conversation**
```
POST /api/v1/restart
Body: { student_id, student_name }
Response: Stream with new thread_id and greeting
```

### Stream Handling

All endpoints return Server-Sent Events (SSE) streams:

```javascript
// Parse SSE format
const events = buffer.split('\n\n');
for (let event of events) {
  if (event.startsWith('data:')) {
    const msg = JSON.parse(event.replace('data: ', ''));
    if (msg.thread_id) setThreadId(msg.thread_id);
    if (msg.content) setMessages(prev => [...prev, msg.content]);
  }
}
```

## Styling System

### Tailwind Classes Used

**Colors**:
- `bg-sky-50, bg-sky-100, bg-sky-400, bg-sky-500`
- `bg-emerald-50, bg-emerald-100, bg-emerald-400, bg-emerald-500`
- `bg-red-50, bg-red-100, bg-red-200, bg-red-600`
- `text-slate-600, text-slate-700, text-slate-800`
- `text-white, text-red-600, text-red-700`

**Spacing**:
- Padding: `p-3, p-4, p-6, p-8, p-10`
- Margins: `m-2, m-3, m-4, m-6`
- Gap: `gap-2, gap-3, gap-4, gap-6`

**Layout**:
- Flexbox: `flex, flex-col, items-center, justify-center, justify-between`
- Grid: `grid-cols-3` (for typing indicator)
- Width: `w-full, w-24, w-8, w-2, w-20`
- Height: `h-screen, h-96, h-24, h-8, h-2, h-20`

**Effects**:
- Shadows: `shadow-sm, shadow-md, shadow-lg`
- Rounded: `rounded-full, rounded-2xl, rounded-3xl, rounded-xl, rounded-lg`
- Opacity: `opacity-50`
- Animations: `animate-fadeIn, animate-pulse`

**Responsive**:
- `md:p-6, md:p-10` (medium screens)
- `md:text-3xl, md:text-base` (font sizing)
- `md:gap-3` (responsive gaps)

### Custom CSS Animations

**fadeIn** (400ms):
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**pulse** (1500ms - for typing indicator):
```css
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
```

## Function Reference

### Handlers

**`handleRegister(e)`**
- Prevents form submission default
- Validates input fields
- Makes API call to `/init_chatbot`
- Parses SSE stream
- Sets thread ID and messages
- Transitions to chat screen

**`handleSendMessage()`**
- Validates input is not empty
- Adds user message to state
- Clears input field
- Sets loading indicator
- Makes API call to `/interact`
- Parses response stream
- Clears loading indicator

**`handleReset()`**
- Calls `/restart` endpoint
- Clears message history
- Gets new greeting message
- Updates thread ID

### Hooks Used

**`useState`**
- Form inputs: `studentId`, `studentName`
- Session: `threadId`, `messages`
- UI State: `registered`, `showPrivacy`, `isLoading`, `isTyping`

**`useRef`**
- `chatEndRef`: Auto-scroll target

**`useEffect`**
- Auto-scroll on new messages
- Dependencies: `[messages, isTyping]`

## Responsive Behavior

### Mobile (< 640px)
- Full-width containers
- Padding: `p-4` instead of `p-6`
- Font sizes reduced slightly
- Button padding: `p-3` instead of `p-4`
- Message area: Adjusted height

### Tablet (640px - 1024px)
- Medium container max-width
- Standard padding
- Optimized spacing

### Desktop (> 1024px)
- Max-width: 1280px (3xl)
- Centered layout
- Full feature set

## Accessibility Features

### Semantic HTML
- `<form>` element for registration
- `<button>` elements with clear labels
- Heading hierarchy: h1 (AnVie), h2 (section titles)
- List markup for security notices

### ARIA Labels (Implicit)
- Form fields have associated labels
- Buttons have descriptive text
- Role attributes automatic from semantic HTML

### Keyboard Navigation
- Tab order: Natural flow through form
- Enter key: Submit forms and send messages
- Focus indicators: Visible on all interactive elements

### Color Contrast
- All text meets WCAG AA (4.5:1)
- Not reliant on color alone for meaning
- Clear button states

## Common Customizations

### Changing Emergency Hotline
```javascript
// In panic button click handler
window.open('tel:NEW_NUMBER');

// In emergency banner
"Gọi NEW_NUMBER"
```

### Updating API Endpoints
```javascript
// Change base URL in fetch calls
const apiBase = 'https://your-api-domain.com/api/v1/';
```

### Modifying Colors
```javascript
// Update Tailwind classes in JSX
bg-custom-500  // Instead of bg-emerald-400
text-custom-700 // Instead of text-slate-800
```

### Adding Messages to Security Notice
```javascript
// In privacy screen section
<li className="flex gap-3">
  <span className="text-emerald-500 font-bold">✓</span>
  <span>Your new message here</span>
</li>
```

## Testing Considerations

### Key User Flows to Test
1. Privacy → Registration → Chat → Message Send
2. Typing indicator appears while bot responds
3. Reset clears conversation and shows new greeting
4. Panic button opens phone dialer
5. Mobile responsiveness at different viewport sizes

### Common Issues
- Messages not appearing: Check API stream parsing
- Styling not applying: Verify Tailwind CSS loaded
- Auto-scroll not working: Check ref attachment
- Typing indicator stalled: Check API response completion

### Browser DevTools Tips
- Use Network tab to inspect SSE streams
- Check Console for parsing errors
- Inspect Element for Tailwind class verification
- Use Device Emulation for mobile testing

## Performance Notes

- Component re-renders optimized with state structure
- Auto-scroll uses `scrollIntoView()` for smooth behavior
- Animations use CSS for GPU acceleration
- No unnecessary state updates in loops

## Future Component Additions

Planned enhancements for modularization:

1. **MessageBubble.js** - Extracted message component
2. **TypingIndicator.js** - Separate animation component
3. **EmergencyBanner.js** - Fixed emergency contact
4. **PrivacyScreen.js** - Separate privacy component
5. **ChatInput.js** - Input field with validation
6. **Header.js** - Chat screen header with actions

These extractions will improve:
- Code reusability
- Easier testing
- Better separation of concerns
- Simpler state management
