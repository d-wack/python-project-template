-- Create audit log table
CREATE TABLE IF NOT EXISTS audit.audit_log (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    table_name text NOT NULL,
    operation text NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data jsonb,
    new_data jsonb,
    changed_by text NOT NULL,
    changed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    client_info jsonb
);

-- Create indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit.audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit.audit_log(operation);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit.audit_log(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_by ON audit.audit_log(changed_by);

-- Create function to add client info to audit log
CREATE OR REPLACE FUNCTION audit.set_client_info()
RETURNS trigger AS $$
BEGIN
    NEW.client_info = json_build_object(
        'application_name', current_setting('application_name', true),
        'ip_address', current_setting('log_service.client_ip', true),
        'user_agent', current_setting('log_service.user_agent', true),
        'session_id', current_setting('log_service.session_id', true)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for client info
CREATE TRIGGER set_client_info_trigger
    BEFORE INSERT ON audit.audit_log
    FOR EACH ROW
    EXECUTE FUNCTION audit.set_client_info();

-- Create view for recent changes
CREATE OR REPLACE VIEW audit.recent_changes AS
SELECT 
    id,
    table_name,
    operation,
    changed_by,
    changed_at,
    CASE 
        WHEN operation = 'INSERT' THEN new_data
        WHEN operation = 'DELETE' THEN old_data
        ELSE jsonb_diff_val(old_data, new_data)
    END as changes
FROM audit.audit_log
WHERE changed_at > (CURRENT_TIMESTAMP - interval '24 hours')
ORDER BY changed_at DESC; 