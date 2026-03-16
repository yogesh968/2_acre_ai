export enum AppointmentStatus {
  SCHEDULED = 'scheduled',
  CONFIRMED = 'confirmed',
  CANCELLED = 'cancelled',
  COMPLETED = 'completed',
  NO_SHOW = 'no_show',
}

export enum Language {
  ENGLISH = 'en',
  HINDI = 'hi',
  TAMIL = 'ta',
}

export interface Patient {
  id: string;
  name: string;
  phone: string;
  email?: string;
  language_preference: Language;
}

export interface Doctor {
  id: string;
  name: string;
  specialization: string;
  is_active: boolean;
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  appointment_datetime: string;
  duration_minutes: number;
  status: AppointmentStatus;
  reason?: string;
  notes?: string;
}

export interface AvailabilitySlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface VoiceMessage {
  type: 'audio_chunk' | 'text' | 'control' | 'response' | 'latency';
  data: string;
  sample_rate?: number;
  metadata?: Record<string, any>;
}

export interface SessionState {
  session_id: string;
  patient_id?: string;
  language: Language;
  intent?: string;
  context: Record<string, any>;
  conversation_history: ConversationMessage[];
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface LatencyMetrics {
  stt_latency: number;
  llm_latency: number;
  tool_latency: number;
  tts_latency: number;
  total_latency: number;
  timestamp: string;
}

export interface VoiceState {
  isRecording: boolean;
  isPlaying: boolean;
  isConnected: boolean;
  currentTranscript: string;
  language: Language;
  latency?: LatencyMetrics;
}
