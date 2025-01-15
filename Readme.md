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
make start  # Start Supabase
make run    # Run FastAPI server
```

### Development Commands

- `make setup` - Setup Python environment
- `make start` - Start Supabase
- `make stop` - Stop Supabase
- `make run` - Run FastAPI server
- `make clean` - Clean up environment
