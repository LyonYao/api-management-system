-- Create health_check_results table
CREATE TABLE health_check_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_id UUID NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    response_code INT,
    response_time_ms INT,
    error_message TEXT,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_status CHECK (status IN ('SUCCESS', 'FAILURE', 'TIMEOUT'))
);

-- Create indexes for faster lookups
CREATE INDEX idx_health_check_results_endpoint_id ON health_check_results(endpoint_id);
CREATE INDEX idx_health_check_results_checked_at ON health_check_results(checked_at DESC);

-- Add comments to table and columns
COMMENT ON TABLE health_check_results IS 'Stores results of health checks performed on endpoints';
COMMENT ON COLUMN health_check_results.id IS 'Unique identifier for the health check result';
COMMENT ON COLUMN health_check_results.endpoint_id IS 'Reference to the endpoint that was checked';
COMMENT ON COLUMN health_check_results.status IS 'Status of the health check (SUCCESS, FAILURE, or TIMEOUT)';
COMMENT ON COLUMN health_check_results.response_code IS 'HTTP response code received from the endpoint';
COMMENT ON COLUMN health_check_results.response_time_ms IS 'Response time in milliseconds';
COMMENT ON COLUMN health_check_results.error_message IS 'Error message if the health check failed';
COMMENT ON COLUMN health_check_results.checked_at IS 'Timestamp when the health check was performed';
