-- This script runs automatically when the container starts for the first time
-- It enables the required PostgreSQL extensions for this project

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify (this will show in container logs)
SELECT PostGIS_Version();
SELECT extversion FROM pg_extension WHERE extname = 'vector';
