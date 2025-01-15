create table cover_letters (
  id uuid default gen_random_uuid() primary key,
  content text not null,
  metadata jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS (Row Level Security)
alter table cover_letters enable row level security;