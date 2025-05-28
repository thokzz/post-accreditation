-- init.sql - Database Initialization File

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE post_accreditation'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'post_accreditation')\gexec

-- Create user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'app_user') THEN

      CREATE ROLE app_user LOGIN PASSWORD 'App_User_Password_2024';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE post_accreditation TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
