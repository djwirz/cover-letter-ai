# Cover Letter AI

An AI-powered cover letter generation system built with FastAPI and Supabase, featuring intelligent analysis and generation capabilities through multiple specialized AI agents.

## Getting Started

### Prerequisites

- Python 3.13.1+
- Supabase CLI
- OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone <your-repo>
cd djwirz-cover-letter-ai
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
make start       # Start Supabase
make db-init     # Initialize database
make run         # Run FastAPI server
```

## Development Commands

- `make setup` - Setup Python environment
- `make install-dev` - Install development dependencies
- `make start` - Start Supabase
- `make stop` - Stop Supabase
- `make db-init` - Initialize database schema
- `make run` - Run FastAPI server
- `make test` - Run all tests
- `make test-v` - Run tests with verbose output
- `make test-cov` - Run tests with coverage report
- `make test-unit` - Run only unit tests
- `make test-api` - Run only API tests
- `make lint` - Run linter
- `make format` - Format code
- `make clean` - Clean up environment
- `make check` - Run all checks (format, lint, test)
- `make dev-setup` - Setup complete development environment

## AI Agents

### Skills Analysis Agent

- Analyzes resumes to extract:
  - Technical skills and proficiency levels
  - Soft skills with supporting evidence
  - Professional achievements with metrics
  - Skill context and years of experience

### Requirements Analysis Agent

- Analyzes job descriptions to identify:
  - Core requirements and years of experience
  - Nice-to-have skills
  - Company culture indicators
  - Key responsibilities
  - Role-specific qualifications

### Strategy Analysis Agent

- Develops cover letter strategies based on:
  - Skill gap analysis
  - Talking points prioritization
  - Company culture alignment
  - Experience mapping
  - Past successful approaches

### Generation Analysis Agent

- Generates professional cover letters using:
  - Skills and requirements analysis
  - Strategic positioning
  - Personalized content
  - Custom preferences and tone
  - Structured section organization

### ATS Scanner Agent

- Analyzes cover letters for ATS compatibility:
  - Keyword matching and scoring
  - Format verification
  - Header analysis
  - Parsing confidence assessment
  - Improvement suggestions

### Content Validation Agent

- Validates cover letter content against:
  - Resume claims accuracy
  - Job requirement coverage
  - Supporting evidence
  - Consistency checks
  - Professional standards

### Technical Term Agent

- Ensures terminology consistency by:
  - Standardizing technical terms
  - Aligning with job description usage
  - Identifying variant forms
  - Suggesting terminology updates
  - Maintaining industry standards

## API Endpoints

### Document Processing

```bash
POST /api/documents
{
  "content": "Document content...",
  "doc_type": "resume|job_description|cover_letter",
  "metadata": {"user_id": "123"}
}
```

### Skills Analysis

```bash
POST /api/analyze/skills
{
  "content": "Resume content...",
  "metadata": {"optional": "metadata"}
}
```

### Requirements Analysis

```bash
POST /api/analyze/requirements
{
  "job_description": "Job posting content...",
  "metadata": {"optional": "metadata"}
}
```

### Strategy Development

```bash
POST /api/analyze/strategy
{
  "resume_content": "Resume content...",
  "job_description": "Job description...",
  "metadata": {"optional": "metadata"}
}
```

### Cover Letter Generation

```bash
POST /api/generate
{
  "job_description": "Job description...",
  "resume_id": "123",
  "resume_content": "Resume content...",
  "preferences": {
    "tone": "professional",
    "focus": "technical"
  }
}
```

### Cover Letter Refinement

```bash
POST /api/refine/cover-letter
{
  "cover_letter": {Cover letter object},
  "feedback": {
    "tone": "Make more enthusiastic",
    "content": "Add more technical details"
  }
}
```

### ATS Analysis

```bash
POST /api/analyze/ats
{
  "cover_letter": "Cover letter content...",
  "job_description": "Job description...",
  "requirements_analysis": {Requirements object}
}
```

### Content Validation

```bash
POST /api/validate/content
{
  "cover_letter": "Cover letter content...",
  "resume": "Resume content...",
  "job_description": "Job description..."
}
```

### Technical Term Standardization

```bash
POST /api/standardize/terms
{
  "job_description": "Job description...",
  "cover_letter": "Cover letter content..."
}
```

## Features

- Multiple specialized AI agents for comprehensive analysis
- Intelligent document processing with vector search
- ATS compatibility checking and optimization
- Content validation and accuracy verification
- Technical terminology standardization
- Vector similarity search for context-aware generation
- OpenAI GPT-4 integration
- Professional cover letter generation with customizable preferences
- Metadata tracking and document management
- Comprehensive test coverage
- Structured error handling and logging
- Performance monitoring and metrics collection

## Project Structure

The project follows a modular architecture with clear separation of concerns:

- `app/agents/` - AI agent implementations
- `app/api/` - FastAPI routes and dependencies
- `app/models/` - Data models and schemas
- `app/services/` - Core services (AI, database, vector store)
- `app/settings/` - Configuration management
- `app/utils/` - Utility functions and helpers
- `tests/` - Comprehensive test suite

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
