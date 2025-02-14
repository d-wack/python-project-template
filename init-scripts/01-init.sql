-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS logging;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA logging GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO logger;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT, INSERT ON TABLES TO logger;

-- Create audit function
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit.audit_log (
            table_name,
            operation,
            new_data,
            changed_by
        ) VALUES (
            TG_TABLE_NAME::text,
            'INSERT',
            row_to_json(NEW),
            current_user
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.audit_log (
            table_name,
            operation,
            old_data,
            new_data,
            changed_by
        ) VALUES (
            TG_TABLE_NAME::text,
            'UPDATE',
            row_to_json(OLD),
            row_to_json(NEW),
            current_user
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_log (
            table_name,
            operation,
            old_data,
            changed_by
        ) VALUES (
            TG_TABLE_NAME::text,
            'DELETE',
            row_to_json(OLD),
            current_user
        );
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql; 