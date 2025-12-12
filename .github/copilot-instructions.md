# Worddee.ai - AI Coding Agent Instructions

## Architecture Overview

Worddee.ai is a full-stack language learning application with the following components:

- **Frontend**: Next.js 16 with React 19, TypeScript, and Tailwind CSS
- **Backend**: Python FastAPI serving REST APIs
- **Database**: PostgreSQL for persistent data storage
- **Automation/AI**: n8n workflows handling AI scoring and data operations
- **AI Service**: Google Gemini API for sentence evaluation and correction

### Data Flow Architecture

```
User Input → Frontend → FastAPI → n8n Webhook → Gemini AI + PostgreSQL → Response
```

- Sentence submissions flow: `frontend/app/word_of_the_day/page.tsx` → `backend/main.py /api/validate-sentence` → n8n scorer webhook → AI evaluation → database storage
- Dashboard data: `frontend/app/dashboard/page.tsx` → `backend/main.py /api/summary` → n8n summary webhook → aggregated statistics

## Development Workflow

### Starting the Full Stack
```bash
docker-compose up -d  # Starts PostgreSQL + n8n services
cd backend && python main.py  # Start FastAPI (requires venv with fastapi, httpx, python-dotenv)
cd frontend && npm run dev   # Start Next.js dev server
```

### Key Development Commands
- **Frontend**: `npm run dev` (port 3000), `npm run build`, `npm run start`
- **Backend**: `python main.py` (port 8000, requires virtual environment)
- **Database**: PostgreSQL runs in Docker (port 5432), data persists in `./pgdata/`
- **n8n**: Web UI at `http://localhost:5678`, workflows hosted externally at `bentosss.app.n8n.cloud`

## Code Patterns & Conventions

### API Communication
- Frontend uses `axios` for HTTP requests with base URL `http://localhost:8000/api`
- Backend uses `httpx.AsyncClient` for proxying requests to n8n webhooks
- Webhook URLs loaded from `.env` file in backend directory
- Error handling: Frontend catches axios errors, backend raises `HTTPException`

### Data Models
- Backend uses Pydantic `BaseModel` for request/response schemas
- TypeScript interfaces in frontend match backend Pydantic models
- Example: `SentenceSubmission` model in `backend/main.py` defines `{word: str, sentence: str}`

### Component Structure
- Next.js App Router with `app/` directory structure
- Client components marked with `'use client'` directive
- State management with React `useState` and `useEffect`
- Chart.js integration for dashboard visualizations

### Database Integration
- n8n handles all database operations (CREATE/READ for submissions table)
- PostgreSQL connection configured in `docker-compose.yml`
- Data persistence through Docker volumes (`./pgdata/`)

## Common Development Tasks

### Adding New API Endpoints
1. Define Pydantic model in `backend/main.py`
2. Create async endpoint function with proper error handling
3. Update frontend TypeScript interfaces
4. Add axios calls in React components

### Modifying AI Scoring Logic
- Changes require updating n8n workflows (external service)
- Test locally by mocking n8n responses in backend
- Webhook endpoints: scorer (`/webhook/scorer/ai`), summary (`/webhook-test/summary/data`)

### Frontend Feature Development
- Add new pages in `frontend/app/` directory
- Use existing patterns: `useState` for form inputs, `axios` for API calls
- Follow TypeScript strict typing for all data structures

## Dependencies & Environment

### Missing Frontend Dependencies
Add to `frontend/package.json`:
```json
"axios": "^1.6.0",
"chart.js": "^4.4.0",
"react-chartjs-2": "^5.2.0"
```

### Backend Environment
- Python virtual environment required (`backend/venv/`)
- Install: `pip install fastapi uvicorn httpx python-dotenv`
- `.env` file contains n8n webhook URLs (currently in `backend/venv/.env`)

### External Services
- **n8n Cloud**: Hosted workflows at `bentosss.app.n8n.cloud`
- **Gemini AI**: API key configured in n8n environment
- **PostgreSQL**: Local Docker instance with persistent storage

## Debugging & Troubleshooting

### Common Issues
- **CORS errors**: Ensure FastAPI CORS middleware is configured
- **n8n connection failures**: Check webhook URLs in `.env` and n8n service status
- **Database connection**: Verify PostgreSQL container is running (`docker ps`)
- **Missing dependencies**: Frontend axios/chart.js not in package.json

### Testing API Endpoints
- Use browser dev tools or Postman to test FastAPI endpoints
- n8n webhooks can be tested directly via their URLs
- Frontend components can be tested by mocking API responses

## Key Files Reference

- `docker-compose.yml`: Service orchestration and environment variables
- `backend/main.py`: FastAPI application with all endpoints
- `frontend/app/word_of_the_day/page.tsx`: Main challenge interface
- `frontend/app/dashboard/page.tsx`: Statistics and history display
- `backend/venv/.env`: n8n webhook configuration</content>
<parameter name="filePath">c:\Users\bike\worddee-ai\.github\copilot-instructions.md