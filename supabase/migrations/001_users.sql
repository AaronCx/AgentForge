-- Users are managed by Supabase Auth (auth.users)
-- This migration ensures RLS is enabled for downstream tables.

-- Enable RLS on auth.users access
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres, service_role;
