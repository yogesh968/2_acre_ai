import { VoiceMessage, LatencyMetrics } from '@/types';

export class VoiceWebSocketService {
  private ws: WebSocket | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private currentAudio: HTMLAudioElement | null = null;
  isPlaying = false;

  constructor(
    private sessionId: string,
    private onMessage: (message: VoiceMessage) => void,
    private onLatency: (metrics: LatencyMetrics) => void,
    private onError: (error: Error) => void,
    private onPlayingChange: (playing: boolean) => void
  ) {}

  connect(wsUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(`${wsUrl}/${this.sessionId}`);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        resolve();
      };

      this.ws.onmessage = async (event) => {
        const message: VoiceMessage = JSON.parse(event.data);

        if (message.type === 'audio_chunk') {
          // Stop any currently playing audio first
          this.stopCurrentAudio();
          await this.playMp3(message.data);
        } else if (message.type === 'latency') {
          this.onLatency(message.metadata as LatencyMetrics);
        } else {
          this.onMessage(message);
        }
      };

      this.ws.onerror = () => {
        this.onError(new Error('WebSocket connection error'));
        reject(new Error('WebSocket connection error'));
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
      };
    });
  }

  async startRecording(): Promise<void> {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      },
    });

    this.audioChunks = [];
    this.mediaRecorder = new MediaRecorder(stream);

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.audioChunks.push(e.data);
    };

    // Send audio only when recording stops
    this.mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());

      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
      if (this.audioChunks.length === 0) return;

      const blob = new Blob(this.audioChunks, { type: 'audio/webm' });
      const buffer = await blob.arrayBuffer();
      const b64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));

      console.log('📤 Sending audio to backend...');
      this.ws.send(
        JSON.stringify({
          type: 'audio_chunk',
          data: b64,
          sample_rate: 16000,
          metadata: { transcript: '' }, // backend will STT this
        })
      );
    };

    this.mediaRecorder.start();
    console.log('🎤 Recording started');
  }

  stopRecording(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
      console.log('🛑 Recording stopped — sending audio');
    }
  }

  private async playMp3(b64: string): Promise<void> {
    try {
      const binary = atob(b64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);

      const blob = new Blob([bytes], { type: 'audio/mpeg' });
      const url = URL.createObjectURL(blob);

      const audio = new Audio(url);
      this.currentAudio = audio;
      this.isPlaying = true;
      this.onPlayingChange(true);

      audio.onended = () => {
        URL.revokeObjectURL(url);
        this.isPlaying = false;
        this.currentAudio = null;
        this.onPlayingChange(false);
        console.log('🔊 Audio playback finished');
      };

      audio.onerror = () => {
        URL.revokeObjectURL(url);
        this.isPlaying = false;
        this.currentAudio = null;
        this.onPlayingChange(false);
      };

      await audio.play();
      console.log('🔊 Playing AI response...');
    } catch (err) {
      console.error('Audio play error:', err);
      this.isPlaying = false;
      this.onPlayingChange(false);
    }
  }

  stopCurrentAudio(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
      this.isPlaying = false;
      this.onPlayingChange(false);
    }
  }

  sendControl(action: string, data?: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'control', data: action, metadata: data || {} }));
    }
  }

  setLanguage(lang: string): void {
    this.sendControl('set_language', { language: lang });
  }

  disconnect(): void {
    this.stopRecording();
    this.stopCurrentAudio();
    this.ws?.close();
    this.ws = null;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
