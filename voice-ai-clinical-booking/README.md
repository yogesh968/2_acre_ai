# Real-Time Multilingual Voice AI Agent for Clinical Appointment Booking

## System Architecture

```mermaid
graph TB
    subgraph Client Layer
        A[Next.js Frontend] -->|WebSocket| B[FastAPI Backend]
    end
    
    subgraph API Gateway
        B -->|Route| C[WebSocket Handler]
        B -->|Route| D[REST API]
    end
    
    subgraph Voice Pipeline
        C -->|Audio Stream| E[Whisper STT]
        E -->|Text + Lang| F[Language Detector]
        F -->|Detected Lang| G[LangGraph Agent]
        G -->|Response| H[Coqui TTS]
        H -->|Audio| C
    end
    
    subgraph Agent Layer
        G -->|Tool Call| I[Tool Executor]
        I -->|Execute| J[Scheduling Engine]
        I -->|Execute| K[Patient Service]
    end
    
    subgraph Memory Layer
        G <-->|Session State| L[Redis Cache]
        J <-->|Persistent Data| M[PostgreSQL]
        K <-->|Patient Data| M
    end
    
    subgraph Background Jobs
        N[Celery Worker] -->|Outbound Calls| O[Campaign Manager]
        O -->|Trigger| C
        P[Redis Queue] -->|Tasks| N
    end
    
    subgraph Monitoring
        Q[Logging Service] -->|Metrics| R[Latency Tracker]
    end
    
    B --> Q
    G --> Q
```

## Latency Breakdown

Target: **< 450ms** from speech end to response start

| Component | Target Latency | Optimization Strategy |
|-----------|---------------|----------------------|
| Speech-to-Text (Whisper) | 80-120ms | Streaming mode, smaller model (base/small) |
| Language Detection | 5-10ms | Cached patterns, fastText |
| LLM Agent (Tool Selection) | 150-200ms | Optimized prompts, streaming |
| Tool Execution | 20-50ms | Indexed DB queries, Redis cache |
| Text-to-Speech (Coqui) | 100-150ms | Streaming synthesis, pre-warmed models |
| Network + Processing | 50-80ms | WebSocket, async I/O |

**Total: 405-610ms** (optimized path: ~420ms)

### Latency Optimization Techniques:
1. **Streaming STT/TTS**: Start processing before complete audio
2. **Model Caching**: Keep models in memory
3. **Connection Pooling**: Reuse DB connections
4. **Predictive Loading**: Pre-load common responses
5. **Parallel Processing**: Run independent operations concurrently

## Memory Design

### Session Memory (Redis)
**Purpose**: Fast access to active conversation state  
**TTL**: 30 minutes of inactivity

```json
{
  "session_id": "uuid",
  "patient_id": "P123",
  "language": "hindi",
  "intent": "book_appointment",
  "context": {
    "doctor_id": "D456",
    "preferred_date": "2024-01-15",
    "pending_confirmation": true
  },
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### Long-Term Memory (PostgreSQL)
**Purpose**: Persistent patient data and appointment records

**Schema Design**:
- `patients`: Profile, language preference, contact info
- `doctors`: Availability schedules, specializations
- `appointments`: Bookings with status tracking
- `availability_slots`: Pre-computed available times
- `conversation_logs`: Audit trail

**Indexing Strategy**:
- B-tree on `appointment.datetime`, `doctor_id`
- Composite index on `(doctor_id, date, status)`
- Hash index on `patient_id`, `session_id`

## Trade-offs

### 1. **Whisper Model Size**
- **Choice**: Base model (74M params)
- **Trade-off**: Accuracy vs Latency
- **Rationale**: 95%+ accuracy with 80-120ms latency acceptable for clinical use

### 2. **LLM Selection**
- **Choice**: GPT-4-turbo / Claude-3 (API) or Llama-3-8B (self-hosted)
- **Trade-off**: Cost/Latency vs Control
- **Rationale**: API for production (reliability), self-hosted for scale

### 3. **TTS Engine**
- **Choice**: Coqui TTS (open-source)
- **Trade-off**: Quality vs Cost
- **Alternative**: ElevenLabs (higher quality, higher cost)

### 4. **Memory Architecture**
- **Choice**: Redis + PostgreSQL (hybrid)
- **Trade-off**: Complexity vs Performance
- **Rationale**: Redis for speed, PostgreSQL for consistency

### 5. **Scheduling Concurrency**
- **Choice**: Optimistic locking with retry
- **Trade-off**: Throughput vs Consistency
- **Rationale**: Rare conflicts, retry acceptable

### 6. **Language Detection**
- **Choice**: First-utterance detection + session persistence
- **Trade-off**: Flexibility vs Accuracy
- **Rationale**: Users rarely switch languages mid-conversation

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Whisper model
python -c "import whisper; whisper.load_model('base')"

# Setup database
export DATABASE_URL="postgresql://user:pass@localhost/clinical_ai"
alembic upgrade head

# Setup Redis
export REDIS_URL="redis://localhost:6379"

# Run migrations
python -m app.db.init_db

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

**Backend (.env)**:
```env
DATABASE_URL=postgresql://user:pass@localhost/clinical_ai
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
LOG_LEVEL=INFO
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## API Endpoints

### REST API
- `POST /api/appointments` - Create appointment
- `GET /api/appointments/{id}` - Get appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment
- `GET /api/doctors/availability` - Check availability
- `POST /api/patients` - Register patient

### WebSocket
- `ws://localhost:8000/ws/{session_id}` - Voice conversation stream

**Message Format**:
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio",
  "sample_rate": 16000
}
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/ -v

# Load testing
locust -f tests/load_test.py
```

## Monitoring

- **Metrics**: Prometheus + Grafana
- **Logging**: Structured JSON logs
- **Tracing**: OpenTelemetry
- **Alerts**: Latency > 500ms, Error rate > 1%

## Production Deployment

### Scaling Strategy
1. **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
2. **Model Serving**: Separate STT/TTS services
3. **Database**: Read replicas for queries
4. **Redis**: Cluster mode for high availability

### Security
- TLS/SSL for all connections
- JWT authentication
- Rate limiting
- Input validation
- HIPAA compliance considerations

## License
MIT
