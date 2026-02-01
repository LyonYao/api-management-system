-- Create relationships table
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    caller_type VARCHAR(10) NOT NULL,
    caller_id UUID NOT NULL,
    callee_type VARCHAR(10) NOT NULL,
    callee_id UUID NOT NULL,
    endpoint_id UUID NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    auth_type VARCHAR(50),
    auth_config JSONB,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_caller_type CHECK (caller_type IN ('SYSTEM', 'API')),
    CONSTRAINT chk_callee_type CHECK (callee_type IN ('SYSTEM', 'API')),
    CONSTRAINT chk_relationship_auth_type CHECK (auth_type IN ('API_KEY', 'OAUTH2', 'BASIC_AUTH', 'JWT', 'NONE'))
);

-- Create indexes for faster lookups
CREATE INDEX idx_relationships_caller ON relationships(caller_type, caller_id);
CREATE INDEX idx_relationships_callee ON relationships(callee_type, callee_id);
CREATE INDEX idx_relationships_endpoint ON relationships(endpoint_id);

-- Add comments to table and columns
COMMENT ON TABLE relationships IS 'Stores call relationships between systems and APIs';
COMMENT ON COLUMN relationships.id IS 'Unique identifier for the relationship';
COMMENT ON COLUMN relationships.caller_type IS 'Type of the caller entity (SYSTEM or API)';
COMMENT ON COLUMN relationships.caller_id IS 'ID of the caller entity';
COMMENT ON COLUMN relationships.callee_type IS 'Type of the callee entity (SYSTEM or API)';
COMMENT ON COLUMN relationships.callee_id IS 'ID of the callee entity';
COMMENT ON COLUMN relationships.endpoint_id IS 'Reference to the specific endpoint being called';
COMMENT ON COLUMN relationships.auth_type IS 'Authentication type used for this relationship';
COMMENT ON COLUMN relationships.auth_config IS 'JSON configuration for authentication';
COMMENT ON COLUMN relationships.description IS 'Description of the call relationship';
COMMENT ON COLUMN relationships.created_at IS 'Timestamp when the relationship was created';
COMMENT ON COLUMN relationships.updated_at IS 'Timestamp when the relationship was last updated';
