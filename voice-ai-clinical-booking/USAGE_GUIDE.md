# 🎤 How to Use the Voice AI System

## ✅ FIXED: AI Now Listens Once, Speaks Once

The system has been updated to prevent repeated responses!

---

## 📱 Step-by-Step Usage

### 1. Open the Application
```
http://localhost:3000
```

### 2. Connect to Voice AI
- Click the **blue phone icon** (large round button)
- Status will change from "Disconnected" to "Connected"
- You'll see a green indicator

### 3. Select Your Language (Optional)
- Choose: **English**, **हिंदी (Hindi)**, or **தமிழ் (Tamil)**
- The AI will respond in your selected language

### 4. Start Recording
- Click the **microphone icon**
- The button will turn **RED** and pulse
- Status shows: "Recording... Speak now"
- **Speak your message clearly**

### 5. Stop Recording & Send
- Click the **microphone icon again** to stop
- Your audio is sent to the AI
- You'll see your transcribed message appear

### 6. AI Responds
- The AI processes your request (1-2 seconds)
- You'll see the AI's text response
- **The AI will speak the response aloud** 🔊
- Only speaks **ONCE** per message

### 7. Continue Conversation
- Click microphone again to ask another question
- The AI remembers your conversation context

---

## 🎯 Example Conversation

**Step 1**: Click phone icon → Connect  
**Step 2**: Click microphone → Start recording  
**Step 3**: Say: *"I want to book an appointment with Dr. Sarah Johnson"*  
**Step 4**: Click microphone again → Stop & send  
**Step 5**: AI responds (text + voice): *"I'd be happy to help you book with Dr. Sarah Johnson. What date and time work best for you?"*  
**Step 6**: Click microphone → Record  
**Step 7**: Say: *"Tomorrow at 10 AM"*  
**Step 8**: Click microphone → Send  
**Step 9**: AI responds: *"Perfect! I'll book your appointment..."*

---

## 🔧 How It Works Now

### Recording Flow:
```
1. Click Mic → Start Recording
2. Speak your message
3. Click Mic Again → Stop & Send
4. AI processes (once)
5. AI responds (once)
6. Audio plays (once)
```

### Key Changes:
✅ Audio sent only when you stop recording  
✅ Backend processes each message only once  
✅ No duplicate responses  
✅ Clear UI feedback  

---

## 🎨 UI Indicators

### Connection Status:
- 🔴 **Red dot** = Disconnected
- 🟢 **Green dot** = Connected

### Recording Status:
- 🔵 **Blue button** = Ready to record
- 🔴 **Red pulsing button** = Recording now
- 📝 **"Recording... Speak now"** = Active

### AI Status:
- 💬 Text appears in conversation
- 🔊 Audio plays automatically
- ⏱️ Latency metrics shown

---

## 💡 Tips for Best Results

### 1. Speak Clearly
- Speak at normal pace
- Avoid background noise
- Use a good microphone

### 2. Complete Sentences
- Say full requests
- Example: "I want to book an appointment with Dr. Sarah Johnson for tomorrow at 10 AM"
- Not: "Book... uh... doctor... tomorrow"

### 3. Wait for Response
- Let the AI finish speaking
- Then record your next message
- Don't interrupt mid-response

### 4. Use Natural Language
- Talk naturally, like to a person
- The AI understands context
- You can say "yes", "no", "change that", etc.

---

## 🩺 Available Doctors

The AI can book with:

1. **Dr. Sarah Johnson**
   - General Physician
   - Mon-Fri, 9 AM - 5 PM

2. **Dr. Raj Kumar**
   - Cardiologist
   - Mon-Wed, 10 AM - 4 PM

3. **Dr. Priya Sharma**
   - Pediatrician
   - Tue-Sat, 9 AM - 3 PM

---

## 🗣️ Sample Requests

### Booking:
- "I want to book an appointment with Dr. Sarah Johnson"
- "Schedule me with the cardiologist"
- "I need to see Dr. Priya Sharma tomorrow"

### Rescheduling:
- "Can I change my appointment to next week?"
- "Reschedule my appointment to Friday"

### Canceling:
- "Cancel my appointment"
- "I need to cancel my booking"

### Checking:
- "What appointments do I have?"
- "Show my appointment history"

---

## 🌐 Multilingual Support

### English:
- Default language
- Full support

### Hindi (हिंदी):
- Select from language buttons
- AI responds in Hindi
- Voice output in Hindi

### Tamil (தமிழ்):
- Select from language buttons
- AI responds in Tamil
- Voice output in Tamil

---

## 🔊 Audio Features

### Voice Input:
- ✅ Microphone capture
- ✅ WebM/Opus format
- ✅ Noise suppression
- ✅ Echo cancellation

### Voice Output:
- ✅ Google Text-to-Speech (gTTS)
- ✅ MP3 format
- ✅ Automatic playback
- ✅ Natural pronunciation

---

## ⚠️ Troubleshooting

### No Audio Output?
- Check browser audio permissions
- Unmute your speakers/headphones
- Check volume levels

### Microphone Not Working?
- Allow microphone access in browser
- Check system microphone settings
- Try refreshing the page

### AI Not Responding?
- Check OpenAI API quota (see STATUS.md)
- View backend logs: `tail -f logs/backend.log`
- Ensure services are running

### Repeated Responses? (FIXED)
- This issue has been fixed!
- If it still happens, restart services:
  ```bash
  bash stop.sh && bash start_voice.sh
  ```

---

## 📊 Performance Metrics

You'll see real-time metrics:

- **STT Latency**: Speech-to-text processing
- **LLM Latency**: AI thinking time
- **TTS Latency**: Text-to-speech generation
- **Total Latency**: End-to-end time

Target: < 450ms total

---

## 🎉 Enjoy Your Voice AI!

The system is now working correctly:
- ✅ Listen once
- ✅ Speak once
- ✅ Natural conversation
- ✅ Multilingual support

**Open http://localhost:3000 and start talking!** 🎤
