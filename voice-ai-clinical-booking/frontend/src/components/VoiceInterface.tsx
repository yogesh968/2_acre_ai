'use client';

import { useEffect, useRef, useState } from 'react';
import { useVoiceStore } from '@/hooks/useVoiceStore';
import { Language } from '@/types';
import { Mic, MicOff, Phone, PhoneOff, VolumeX, Activity, HeartPulse, Globe2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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

  // Auto-scroll chat smoothly
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTo({
        top: chatRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [conversationHistory]);

  const handleConnect = async () => {
    try {
      setError('');
      await connect(sessionId);
    } catch {
      setError('Connection failed. Please ensure the clinical backend is online.');
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
        setError('Microphone access denied. Please grant permissions in your browser.');
      }
    }
  };

  const LANGUAGES = [
    { value: Language.ENGLISH, label: 'English', short: 'EN' },
    { value: Language.HINDI,   label: 'हिंदी', short: 'HI' },
    { value: Language.TAMIL,   label: 'தமிழ்', short: 'TA' },
  ];

  return (
    <div className="min-h-screen bg-[#050B14] text-slate-200 font-sans selection:bg-blue-500/30 flex items-center justify-center p-4 sm:p-6 overflow-hidden relative">
      
      {/* Dynamic Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px]" />
        
        {/* Subtle grid pattern for clinical feel */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTAgMGg0MHY0MEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0wIDM5LjVoNDBNMzkuNSAwdi00MCIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIiBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiLz48L3N2Zz4=')] opacity-50" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-[1000px] grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10"
      >
        
        {/* Left Column: Controls & Metrics */}
        <div className="lg:col-span-4 space-y-6 flex flex-col h-full">
          
          {/* Header Card */}
          <div className="bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl rounded-3xl p-6 shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500 opacity-80" />
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 flex items-center justify-center border border-blue-500/30">
                <HeartPulse className="text-blue-400" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 tracking-tight">
                  Nova Clinic AI
                </h1>
                <p className="text-sm text-slate-500 font-medium">Voice Intelligent Booking</p>
              </div>
            </div>
          </div>

          {/* Main Controls Card */}
          <div className="bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl rounded-3xl p-8 shadow-2xl flex-1 flex flex-col items-center justify-center relative inner-glow">
            
            {/* Connection Status Indicator */}
            <div className="absolute top-6 left-0 right-0 flex justify-center">
              <motion.div 
                animate={{ 
                  backgroundColor: isConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(148, 163, 184, 0.05)',
                  borderColor: isConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(148, 163, 184, 0.1)'
                }}
                className="flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-white/5 backdrop-blur-md"
              >
                <span className="relative flex h-2.5 w-2.5">
                  {isConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                  <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isConnected ? 'bg-emerald-500' : 'bg-slate-600'}`}></span>
                </span>
                <span className={`text-xs font-medium tracking-wide ${isConnected ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {isConnected ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
                </span>
              </motion.div>
            </div>

            <div className="mt-8 mb-4 min-h-[160px] flex items-center justify-center relative w-full">
              
              {/* Central Mic Button */}
              {isConnected ? (
                <div className="relative">
                  {/* Ripple Effect when recording */}
                  {isRecording && (
                    <>
                      <motion.div animate={{ scale: [1, 1.5, 2], opacity: [0.5, 0.2, 0] }} transition={{ repeat: Infinity, duration: 2, ease: "easeOut" }} className="absolute inset-0 bg-blue-500 rounded-full z-0" />
                      <motion.div animate={{ scale: [1, 1.2, 1.5], opacity: [0.5, 0.3, 0] }} transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut", delay: 0.2 }} className="absolute inset-0 bg-blue-400 rounded-full z-0" />
                    </>
                  )}
                  
                  {/* AI Speaking Visualizer */}
                  {isPlaying && (
                     <div className="absolute -inset-8 flex items-center justify-center gap-1 z-0">
                        {[...Array(9)].map((_, i) => (
                           <motion.div 
                             key={i}
                             animate={{ height: [12, Math.random() * 40 + 20, 12] }}
                             transition={{ repeat: Infinity, duration: 0.6 + Math.random() * 0.4, ease: "easeInOut" }}
                             className="w-1.5 bg-gradient-to-t from-indigo-500 to-purple-400 rounded-full"
                           />
                        ))}
                     </div>
                  )}

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleMic}
                    disabled={isPlaying}
                    className={`relative z-10 w-28 h-28 rounded-full flex items-center justify-center shadow-[0_0_40px_rgba(0,0,0,0.3)] border border-white/10 transition-colors ${
                      isRecording 
                        ? 'bg-gradient-to-b from-blue-500 to-blue-600 text-white' 
                        : isPlaying
                          ? 'bg-[#0f172a] text-indigo-400 cursor-not-allowed border-indigo-500/30'
                          : 'bg-[#0f172a] hover:bg-[#1e293b] text-blue-400'
                    }`}
                  >
                    {isRecording ? <MicOff size={36} /> : <Mic size={36} className={isPlaying ? 'opacity-50' : ''} />}
                  </motion.button>
                </div>
              ) : (
                <motion.button
                    whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(16, 185, 129, 0.2)" }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleConnect}
                    className="w-28 h-28 rounded-full bg-[#0f172a] border border-white/10 flex items-center justify-center text-emerald-400 transition-all shadow-xl group"
                >
                  <Phone size={36} className="group-hover:animate-pulse" />
                </motion.button>
              )}
            </div>

            {/* Contextual Action / Status Text */}
            <div className="h-12 flex items-center justify-center text-center w-full mt-4">
              <AnimatePresence mode="wait">
                <motion.p 
                  key={isConnected ? (isRecording ? 'rec' : isPlaying ? 'play' : 'ready') : 'off'}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="text-sm font-medium tracking-wide text-slate-400"
                >
                  {!isConnected && 'Initialize terminal to begin'}
                  {isConnected && !isRecording && !isPlaying && 'Awaiting voice input...'}
                  {isConnected && isRecording && <span className="text-blue-400">Recording... Tap to transmit</span>}
                  {isConnected && isPlaying && <span className="text-indigo-400">Synthesizing vocal response...</span>}
                </motion.p>
              </AnimatePresence>
            </div>

            {/* Bottom Controls Row */}
            <div className="w-full flex justify-between items-center mt-6 pt-6 border-t border-white/5">
                <button
                  onClick={isConnected ? disconnect : handleConnect}
                  className={`p-3 rounded-xl border transition-all ${
                    isConnected 
                      ? 'bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20' 
                      : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20'
                  }`}
                  title={isConnected ? "Disconnect" : "Connect"}
                >
                  <PhoneOff size={20} />
                </button>

                {/* Micro Language Selector */}
                <div className="flex bg-[#0f172a] border border-white/5 rounded-xl p-1">
                  {LANGUAGES.map(l => (
                    <button
                      key={l.value}
                      onClick={() => setLanguage(l.value)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        language === l.value 
                          ? 'bg-blue-500/20 text-blue-400 shadow-sm' 
                          : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                      }`}
                    >
                      {l.short}
                    </button>
                  ))}
                </div>

                <button
                  onClick={interrupt}
                  disabled={!isPlaying}
                  className={`p-3 rounded-xl border transition-all ${
                    isPlaying 
                      ? 'bg-orange-500/10 border-orange-500/20 text-orange-400 hover:bg-orange-500/20 cursor-pointer' 
                      : 'bg-white/5 border-white/5 text-slate-600 cursor-not-allowed'
                  }`}
                  title="Interrupt AI"
                >
                  <VolumeX size={20} />
                </button>
            </div>
            
          </div>

        </div>

        {/* Right Column: Chat & Analysis */}
        <div className="lg:col-span-8 flex flex-col h-[700px] gap-6">
          
          {/* Main Chat Interface */}
          <div className="bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl rounded-3xl flex flex-col h-full shadow-2xl overflow-hidden relative">
            
            {/* Header */}
            <div className="px-6 py-5 border-b border-white/[0.05] flex justify-between items-center bg-black/20">
              <div className="flex items-center gap-3">
                <Activity size={18} className="text-blue-500" />
                <h2 className="text-sm font-semibold tracking-widest text-slate-300 uppercase">Live Session</h2>
              </div>
              
              {/* Minimal Latency Pill (Shows only when active) */}
              <AnimatePresence>
                {latency && isConnected && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-3 text-[10px] font-mono tracking-wider bg-black/40 px-3 py-1.5 rounded-full border border-white/5"
                  >
                    <span className="text-slate-500">RES: <span className="text-emerald-400">{latency.total_latency.toFixed(0)}MS</span></span>
                    <span className="w-px h-3 bg-white/10" />
                    <span className="text-slate-500">LLM: <span className="text-blue-400">{latency.llm_latency.toFixed(0)}MS</span></span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Messages Area */}
            <div 
              ref={chatRef} 
              className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
            >
              {conversationHistory.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
                  <Globe2 size={48} className="opacity-20" />
                  <p className="text-sm font-medium tracking-wide">Awaiting secure connection sequence...</p>
                </div>
              ) : (
                <AnimatePresence initial={false}>
                  {conversationHistory.map((msg, i) => {
                    const isUser = msg.role === 'user';
                    return (
                      <motion.div 
                        key={`${i}-${msg.timestamp}`}
                        initial={{ opacity: 0, y: 10, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.3 }}
                        className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`flex max-w-[85%] gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                          
                          {/* Avatar */}
                          <div className={`flex-shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center border shadow-sm ${
                            isUser 
                              ? 'bg-slate-800 border-slate-700/50' 
                              : 'bg-gradient-to-br from-blue-600 to-indigo-600 border-blue-500/30'
                          }`}>
                            {isUser ? <div className="w-2 h-2 rounded-full bg-slate-400" /> : <HeartPulse size={20} className="text-white" />}
                          </div>

                          {/* Message Bubble */}
                          <div className={`relative px-6 py-4 rounded-3xl text-[15px] leading-relaxed shadow-md ${
                            isUser
                              ? 'bg-slate-800 border-slate-700/50 text-slate-200 rounded-tr-sm border'
                              : 'bg-gradient-to-br from-blue-900/40 to-indigo-900/40 border border-blue-500/20 text-blue-50 rounded-tl-sm'
                          }`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                            
                            {/* Timestamp */}
                            <div className={`mt-2 text-[10px] font-mono opacity-40 ${isUser ? 'text-right' : 'text-left'}`}>
                              {new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </div>
                          </div>
                          
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              )}
            </div>

            {/* Error Banner overlay */}
            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 50 }}
                  className="absolute bottom-6 left-6 right-6 bg-red-950/80 backdrop-blur-md border border-red-500/50 text-red-200 px-5 py-3 rounded-2xl text-sm shadow-2xl flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <p>{error}</p>
                  </div>
                  <button onClick={() => setError('')} className="text-red-400 hover:text-white px-2">✕</button>
                </motion.div>
              )}
            </AnimatePresence>
            
          </div>
        </div>

      </motion.div>
    </div>
  );
}
