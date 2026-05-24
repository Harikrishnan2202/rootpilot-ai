# RootPilot AI - Incident Root Cause Analyzer

> AI-powered incident intelligence for SRE teams. Detect, explain, and prevent system failures.

## 🎯 Problem Statement

Engineering teams waste valuable time during outages searching logs, dashboards, and alerts to identify root cause. RootPilot AI automates this process using LLMs to deliver instant, explainable root cause analysis.

## ✨ Features

- **Real-time log streaming** with color-coded service badges
- **AI-powered root cause analysis** with confidence scoring
- **Incident timeline reconstruction** – see exactly what happened when
- **Interactive dependency graph** – visualize service failures
- **Natural language chat** – ask questions about incidents
- **Confidence-based ranking** of possible causes
- **Fix recommendations** with estimated impact
- **Incident heatmap** – see which services fail most
- **Incident replay mode** – replay outages for post-mortems

## 🏗️ Architecture

- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, React Flow, Recharts
- **Backend:** FastAPI (Python 3.12), Gemini/OpenAI API
- **Simulation:** Mock log generator with incident triggers

## 🚀 Quick Start

### Prerequisites
- Python 3.12
- Node.js 18+
- Gemini API key (free from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # add your GEMINI_API_KEY
python run.py

Backend runs at http://localhost:8000

Frontend Setup
bash
cd frontend
npm install
npm run dev

Frontend runs at http://localhost:3000

Project Structure
rootpilot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   ├── .env
│   └── run.py
└── frontend/
    ├── app/
    │   ├── components/
    │   ├── lib/
    │   ├── page.tsx
    │   └── globals.css
    ├── package.json
    └── tailwind.config.js

Demo Instructions
1.Start backend and frontend

2.Click "Generate Logs" to see live logs

3.Click "Trigger DB Incident" to simulate a database failure

4.Click "Analyze Root Cause" – AI will identify the problem

5.Explore timeline, dependency graph, confidence ranking

6.Ask the chat panel: "Why did the database fail?"

7.Use "Replay Incident" to replay the outage timeline

🔧 Tech Stack
Layer	                   Technology
Frontend	    Next.js 14, TypeScript, Tailwind CSS
UIComponents	shadcn/ui, Framer Motion, React Flow
Charts	                   Recharts
Backend	           FastAPI, Python 3.12
AI	           Google Gemini 1.5 Flash (or OpenAI GPT-3.5)
HTTP                     Client	Axios

