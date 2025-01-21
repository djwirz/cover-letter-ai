# Cover Letter AI

An AI-powered cover letter generation system built with FastAPI and Supabase.

## Getting Started

### Prerequisites

- Python 3.13.1+
- Supabase CLI
- OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone <your-repo>
cd cover-letter-ai
```

2. Set up environment:

```bash
make setup
```

3. Create `.env` file:

```
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=your_supabase_anon_key
```

4. Start services:

```bash
make start # Start Supabase
make db-init # Initialize database
make run # Run FastAPI server
```

### Development Commands

- `make setup` - Setup Python environment
- `make start` - Start Supabase
- `make stop` - Stop Supabase
- `make db-init` - Initialize database schema
- `make run` - Run FastAPI server
- `make test` - Run test suite
- `make clean` - Clean up environment

### Project Structure

```
app/
├── agents/
│ ├── **init**.py
│ ├── skills_analysis.py
│ └── requirements_analysis.py
├── models/
│ └── schemas.py
├── core/
│ ├── database.py
│ └── vector_store.py
├── api/
│ └── routes.py
└── main.py
```

### AI Agents

#### Skills Analysis Agent

- Analyzes resumes to extract:
- Technical skills
- Soft skills
- Professional achievements
- Provides structured skill data for matching

#### Requirements Analysis Agent

- Analyzes job descriptions to identify:
- Core requirements
- Nice-to-have skills
- Company culture indicators
- Key responsibilities
- Enables intelligent job-candidate matching

### API Endpoints

#### Upload Document

```bash
curl -X POST "http://localhost:8000/api/documents"
-H "Content-Type: application/json"
-d '{
"content": "Your document text here...",
"doc_type": "resume",
"metadata": {"user_id": "123"}
}'
```

#### Analyze Resume Skills

```bash
curl -X POST "http://localhost:8000/api/analyze/skills"
-H "Content-Type: application/json"
-d '{
"resume_id": "123"
}'
```

#### Analyze Job Requirements

```bash
curl -X POST "http://localhost:8000/api/analyze/requirements"
-H "Content-Type: application/json"
-d '{
"job_description": "Job description text..."
}'
```

#### Generate Cover Letter

```bash
curl -X POST "http://localhost:8000/api/generate"
-H "Content-Type: application/json"
-d '{
"job_description": "Job description text...",
"resume_id": "123",
"preferences": {
"tone": "professional",
"focus": "technical"
}
}'
```

### Features

- Intelligent AI agents for skills and requirements analysis
- Document processing with intelligent chunking
- Vector similarity search for context-aware generation
- OpenAI GPT-4 integration for high-quality content generation
- Metadata tracking and document management
- Professional cover letter generation with customizable preferences
