# 🎯 Worddee.ai

**Master English Vocabulary with AI-Powered Learning**

Worddee.ai is an interactive web application that helps users improve their English vocabulary through AI-powered sentence validation, real-time feedback, and progress tracking.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### 🎓 Learning & Practice
- **Daily Challenges** - Get random vocabulary words with definitions
- **Sentence Writing** - Compose sentences using the given word
- **AI-Powered Scoring** - Intelligent evaluation of grammar, sentence structure, and vocabulary usage
- **Real-time Feedback** - Instant corrections and suggestions for improvement

### 📊 Dashboard & Analytics
- **Progress Tracking** - Monitor your learning statistics
- **Score History** - View your past submissions and scores
- **Achievement Stats** - Total attempts, average score, highest score, current streak

### 🎨 Modern UI/UX
- **Beautiful Design** - Modern gradient-based interface with smooth animations
- **Responsive Layout** - Works on desktop, tablet, and mobile devices
- **Interactive Navigation** - Easy switching between Home, Challenge, and Dashboard pages

---

## 📁 Project Structure

```
word-eiei-main/
├── frontend/
│   └── index.html              # Main web application (Vue-like with vanilla JS)
├── backend/
│   ├── main.py                 # FastAPI application with scoring logic
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Docker configuration for backend
│   └── setup_n8n_workflows.py  # Setup script for n8n workflows
├── docker-compose.yml          # Docker Compose configuration
├── Caddyfile                   # Caddy reverse proxy configuration
├── pgdata/                     # PostgreSQL data volume
├── package.json                # Node.js dependencies (if needed)
└── README.md                   # This file
```

---

## 🔧 Requirements

### Option 1: Using Docker (Recommended)
- Docker & Docker Compose
- 4GB RAM minimum
- 2GB free disk space

### Option 2: Local Development
- Python 3.11+
- Node.js 18+ (optional, for frontend development)
- PostgreSQL 14+
- macOS/Linux/Windows with WSL2

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Thanakorn027/worddee-eiei.git
cd word-eiei-main
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
N8N_SCORER_WEBHOOK=http://n8n:5678/webhook/scorer
N8N_SUMMARY_WEBHOOK=http://n8n:5678/webhook/summary
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace `your_gemini_api_key_here` with your actual Google Gemini API key from:
https://makersuite.google.com/app/apikey

### 3. Docker Setup (Optional but Recommended)

Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

---

## 🚀 Running the Application

### Option 1: Using Docker Compose (Fastest Way)

```bash
cd word-eiei-main

# Start all services (backend, frontend, database, reverse proxy)
docker-compose up -d

# Check if all services are running
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f caddy
```

**Access the application:**
- **Frontend:** http://localhost/
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **n8n UI:** http://localhost:5678

### Option 2: Running Locally (Without Docker)

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with configuration
echo "N8N_SCORER_WEBHOOK=http://localhost:5678/webhook/scorer" > .env
echo "N8N_SUMMARY_WEBHOOK=http://localhost:5678/webhook/summary" >> .env

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
# The frontend is a single HTML file, just serve it:
# Option A: Using Python
cd frontend
python3 -m http.server 8080

# Option B: Using Node.js http-server
npx http-server ./frontend -p 8080
```

Then open http://localhost:8080 in your browser.

---

## 📡 API Endpoints

### 1. Get Random Word

**Request:**
```bash
GET /api/word
```

**Response:**
```json
{
  "word": "Serendipity",
  "definition": "The occurrence of events by chance in a happy or beneficial way",
  "pos": "noun"
}
```

### 2. Submit Sentence for Scoring

**Request:**
```bash
POST /api/score
Content-Type: application/json

{
  "word": "Innovation",
  "sentence": "The team showed great innovation in solving the problem."
}
```

**Response:**
```json
{
  "score": 85.5,
  "level": "Intermediate",
  "suggestion": "Good job! You're on the right track. ✓ Your sentence demonstrates strong command of English.",
  "corrected_sentence": "The team showed great innovation in solving the problem."
}
```

### 3. Get Dashboard Summary

**Request:**
```bash
GET /api/summary
```

**Response:**
```json
{
  "statistics": {
    "total_submissions": 42,
    "avg_score": 78.5,
    "max_score": 98.0,
    "min_score": 65.0
  },
  "recent_submissions": [
    {
      "word": "Innovation",
      "sentence": "The team showed great innovation.",
      "score": 85.0,
      "level": "Intermediate",
      "timestamp": "2025-12-13T10:30:00Z"
    }
  ]
}
```

---

## 🏗 Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | HTML5 + Vanilla JavaScript | User interface & interaction |
| **Backend** | FastAPI (Python) | REST API & scoring logic |
| **Database** | PostgreSQL 14 | Store submissions & user data |
| **Reverse Proxy** | Caddy 2 | HTTP routing & TLS |
| **Automation** | n8n (Optional) | Workflow automation & AI integration |
| **Containerization** | Docker & Docker Compose | Application deployment |

### System Flow

```
User Browser (http://localhost)
    ↓
Caddy Reverse Proxy (Port 80/443)
    ↓
    ├→ /            → Serve frontend (index.html)
    └→ /api/*       → FastAPI Backend (Port 8000)
         ↓
         ├→ /api/word          → Get random word from list
         ├→ /api/score         → Score sentence & store submission
         ├→ /api/summary       → Fetch statistics
         └→ /webhook/scorer    → Mock n8n webhook (AI scoring)
              ↓
         PostgreSQL Database (Port 5432)
         n8n Automation (Port 5678) [Optional]
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `N8N_SCORER_WEBHOOK` | Webhook URL for scoring workflow | `http://n8n:5678/webhook/scorer` |
| `N8N_SUMMARY_WEBHOOK` | Webhook URL for summary workflow | `http://n8n:5678/webhook/summary` |
| `GEMINI_API_KEY` | Google Gemini API key for AI features | (required for real AI) |
| `POSTGRES_DB` | Database name | `worddeedb` |
| `POSTGRES_USER` | Database user | `worddee_user` |
| `POSTGRES_PASSWORD` | Database password | `bb05112545` |

### Scoring Algorithm

The scoring system evaluates sentences on the following criteria:

- **Sentence Length** (6+ words recommended): +10-15 points
- **Word Usage** (must contain the target word): +20 points
- **Capitalization** (starts with capital letter): +5 points
- **Punctuation** (ends with . ! or ?): +5 points
- **Grammar** (contains valid verbs): +15 points
- **Prepositions** (proper use of prepositions): +10 points

**Score Levels:**
- **Beginner**: 0-69 points
- **Intermediate**: 70-84 points
- **Advanced**: 85-100 points

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using port 80, 8000, 5432, etc.
lsof -i :80
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### PostgreSQL Connection Error

```bash
# Ensure PostgreSQL container is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### Backend Not Responding

```bash
# Rebuild backend image
docker-compose build --no-cache backend
docker-compose up -d backend

# Check backend logs
docker-compose logs -f backend
```

### Frontend Not Loading

```bash
# Clear browser cache (Ctrl+Shift+Delete)
# Check if Caddy is running
docker-compose logs caddy

# Restart Caddy
docker-compose restart caddy
```

### API Endpoint Returns 500 Error

```bash
# Check backend logs for detailed error
docker-compose logs -f backend

# If n8n webhook fails, mock endpoint is used automatically
# This is normal behavior during development
```

---

## 📝 Development

### Adding New Features

1. **Backend**: Edit `backend/main.py` and add new endpoints
2. **Frontend**: Edit `frontend/index.html` and modify JavaScript logic
3. **Rebuild**: Run `docker-compose build` and `docker-compose up -d`

### Testing API Endpoints

```bash
# Test word endpoint
curl http://localhost:8000/api/word | jq .

# Test scoring endpoint
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"word":"Innovation","sentence":"Innovation is important."}'

# Test summary endpoint
curl http://localhost:8000/api/summary | jq .
```

### Enabling Real AI (Gemini)

1. Get API key: https://makersuite.google.com/app/apikey
2. Set environment variable: `GEMINI_API_KEY=your_key`
3. Create n8n workflow to call Gemini API
4. Update backend webhook URL to point to n8n

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [n8n Workflow Automation](https://n8n.io/)
- [Docker & Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Google Gemini API](https://ai.google.dev/)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Thanakorn** - [GitHub](https://github.com/Thanakorn027)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on [GitHub Issues](https://github.com/Thanakorn027/worddee-eiei/issues).

---

## 🎯 Roadmap

- [ ] Real Gemini AI integration for scoring
- [ ] User authentication & login system
- [ ] Leaderboards & competitions
- [ ] Spaced repetition algorithm
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Teacher/student mode

---

**Happy Learning! 🚀📚**
