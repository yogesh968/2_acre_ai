import { create } from 'zustand';
import { Language, LatencyMetrics, ConversationMessage } from '@/types';
import { VoiceWebSocketService } from '@/services/websocket';

interface VoiceStore {
  wsService: VoiceWebSocketService | null;
  isConnected: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  language: Language;
  latency?: LatencyMetrics;
  conversationHistory: ConversationMessage[];

  connect: (sessionId: string) => Promise<void>;
  disconnect: () => void;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  interrupt: () => void;
  setLanguage: (lang: Language) => void;
}

export const useVoiceStore = create<VoiceStore>((set, get) => ({
  wsService: null,
  isConnected: false,
  isRecording: false,
  isPlaying: false,
  language: Language.ENGLISH,
  latency: undefined,
  conversationHistory: [],

  connect: async (sessionId: string) => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

    const svc = new VoiceWebSocketService(
      sessionId,
      (message) => {
        if (message.type === 'text') {
          const role = message.metadata?.role as 'user' | 'assistant';
          set((s) => ({
            conversationHistory: [
              ...s.conversationHistory,
              { role, content: message.data, timestamp: new Date().toISOString() },
            ],
          }));
        }
      },
      (metrics) => set({ latency: metrics }),
      (err) => {
        console.error('WS error:', err);
        set({ isConnected: false });
      },
      (playing) => set({ isPlaying: playing })
    );

    await svc.connect(wsUrl);
    set({ wsService: svc, isConnected: true });
  },

  disconnect: () => {
    get().wsService?.disconnect();
    set({ wsService: null, isConnected: false, isRecording: false, isPlaying: false });
  },

  startRecording: async () => {
    const { wsService } = get();
    if (!wsService) return;
    await wsService.startRecording();
    set({ isRecording: true });
  },

  stopRecording: () => {
    const { wsService } = get();
    if (!wsService) return;
    wsService.stopRecording();
    set({ isRecording: false });
  },

  interrupt: () => {
    const { wsService } = get();
    if (!wsService) return;
    wsService.stopCurrentAudio();
    wsService.sendControl('interrupt');
    set({ isPlaying: false });
  },

  setLanguage: (lang: Language) => {
    get().wsService?.setLanguage(lang);
    set({ language: lang });
  },
}));
