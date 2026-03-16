'use client';

import { useEffect, useRef, useState } from 'react';
import { useVoiceStore } from '@/hooks/useVoiceStore';
import { Language } from '@/types';
import { Mic, MicOff, Phone, PhoneOff, Volume2, VolumeX } from 'lucide-react';

export default function VoiceInterface() {
  const {
    isConnected, isRecording, isPlaying,
    language, latency, conversationHistory,
    connect, disconnect, startRecording, stopRecording,
    interrupt, setLanguage,
  } = useVoiceStore();

  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [error, setError] = useState('');
  const chatRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [conversationHistory]);

  const handleConnect = async () => {
    try {
      setError('');
      await connect(sessionId);
    } catch {
      setError('Failed to connect. Make sure the backend is running on port 8000.');
    }
  };

  const handleMic = async () => {
    if (isRecording) {
      stopRecording();
    } else {
      try {
        setError('');
        await startRecording();
      } catch {
        setError('Microphone access denied. Please allow microphone in browser settings.');
      }
    }
  };

  const LANGUAGES = [
    { value: Language.ENGLISH, label: 'English' },
    { value: Language.HINDI,   label: 'हिंदी' },
    { value: Language.TAMIL,   label: 'தமிழ்' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-blue-950 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl space-y-4">

        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">🏥 Clinical Voice AI</h1>
          <p className="text-blue-300 mt-1">Book appointments by speaking naturally</p>
        </div>

        {/* Language Selector */}
        <div className="bg-white/10 rounded-2xl p-4 flex gap-3 justify-center">
          {LANGUAGES.map((l) => (
            <button
              key={l.value}
              onClick={() => setLanguage(l.value)}
              className={`px-5 py-2 rounded-xl font-medium transition-all ${
                language === l.value
                  ? 'bg-blue-500 text-white shadow-lg scale-105'
                  : 'bg-white/10 text-white hover:bg-white/20'
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>

        {/* Voice Controls */}
        <div className="bg-white/10 rounded-2xl p-8 flex flex-col items-center gap-6">

          {/* Status Badge */}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
            isConnected ? 'bg-green-500/20 text-green-300' : 'bg-gray-500/20 text-gray-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>

          {/* Main Buttons */}
          <div className="flex gap-8 items-center">

            {/* Connect / Disconnect */}
            <button
              onClick={isConnected ? disconnect : handleConnect}
              className={`w-20 h-20 rounded-full flex items-center justify-center shadow-2xl transition-all hover:scale-110 ${
                isConnected
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              {isConnected ? <PhoneOff size={32} className="text-white" /> : <Phone size={32} className="text-white" />}
            </button>

            {/* Mic Button */}
            {isConnected && (
              <button
                onClick={handleMic}
                disabled={isPlaying}
                className={`w-28 h-28 rounded-full flex items-center justify-center shadow-2xl transition-all hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse ring-4 ring-red-400'
                    : 'bg-blue-500 hover:bg-blue-600'
                }`}
              >
                {isRecording
                  ? <MicOff size={40} className="text-white" />
                  : <Mic size={40} className="text-white" />
                }
              </button>
            )}

            {/* Interrupt Button */}
            {isPlaying && (
              <button
                onClick={interrupt}
                className="w-20 h-20 rounded-full bg-orange-500 hover:bg-orange-600 flex items-center justify-center shadow-2xl transition-all hover:scale-110"
              >
                <VolumeX size={32} className="text-white" />
              </button>
            )}
          </div>

          {/* Status Text */}
          <p className="text-white/70 text-center text-sm">
            {!isConnected && 'Click the green button to connect'}
            {isConnected && !isRecording && !isPlaying && 'Click the microphone and speak'}
            {isRecording && '🔴 Recording... Click mic again to send'}
            {isPlaying && '🔊 AI is speaking... Click orange to interrupt'}
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-3 text-red-300 text-sm text-center">
            {error}
          </div>
        )}

        {/* Latency Metrics */}
        {latency && (
          <div className="bg-white/10 rounded-2xl p-4 grid grid-cols-5 gap-2 text-center">
            {[
              { label: 'STT', value: latency.stt_latency },
              { label: 'LLM', value: latency.llm_latency },
              { label: 'Tool', value: latency.tool_latency },
              { label: 'TTS', value: latency.tts_latency },
              { label: 'Total', value: latency.total_latency },
            ].map((m) => (
              <div key={m.label}>
                <p className={`text-lg font-bold ${m.label === 'Total' ? 'text-yellow-400' : 'text-blue-300'}`}>
                  {m.value.toFixed(0)}ms
                </p>
                <p className="text-white/50 text-xs">{m.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Conversation */}
        <div className="bg-white/10 rounded-2xl p-4">
          <p className="text-white/50 text-xs mb-3 uppercase tracking-wider">Conversation</p>
          <div ref={chatRef} className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {conversationHistory.length === 0 ? (
              <p className="text-white/30 text-center py-6 text-sm">
                Connect and speak to start the conversation
              </p>
            ) : (
              conversationHistory.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs px-4 py-2 rounded-2xl text-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-sm'
                      : 'bg-white/20 text-white rounded-bl-sm'
                  }`}>
                    <p className="font-semibold text-xs opacity-70 mb-1">
                      {msg.role === 'user' ? 'You' : '🤖 AI'}
                    </p>
                    {msg.content}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-white/5 rounded-2xl p-4 text-white/40 text-xs text-center space-y-1">
          <p>1. Click <strong className="text-white/60">green phone</strong> to connect</p>
          <p>2. Click <strong className="text-white/60">blue mic</strong> → speak → click mic again to send</p>
          <p>3. AI will respond with voice automatically</p>
        </div>

      </div>
    </div>
  );
}
