-- Create endpoints table
CREATE TABLE endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_id UUID NOT NULL REFERENCES apis(id) ON DELETE CASCADE,
    path VARCHAR(1000) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_http_method CHECK (http_method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')),
    CONSTRAINT uq_endpoint_api_path_method UNIQUE (api_id, path, http_method)
);

-- Create indexes for faster lookups
CREATE INDEX idx_endpoints_api_id ON endpoints(api_id);
CREATE INDEX idx_endpoints_path ON endpoints(path);

-- Add comments to table and columns
COMMENT ON TABLE endpoints IS 'Stores information about API endpoints';
COMMENT ON COLUMN endpoints.id IS 'Unique identifier for the endpoint';
COMMENT ON COLUMN endpoints.api_id IS 'Reference to the API that contains this endpoint';
COMMENT ON COLUMN endpoints.path IS 'URL path of the endpoint';
COMMENT ON COLUMN endpoints.http_method IS 'HTTP method used by the endpoint';
COMMENT ON COLUMN endpoints.description IS 'Description of the endpoint';
COMMENT ON COLUMN endpoints.created_at IS 'Timestamp when the endpoint was created';
COMMENT ON COLUMN endpoints.updated_at IS 'Timestamp when the endpoint was last updated';
