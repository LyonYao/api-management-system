-- Create apis table
CREATE TABLE apis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_id UUID NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    auth_type VARCHAR(50),
    spec_link VARCHAR(1000),
    department VARCHAR(255),
    contact_name VARCHAR(255),
    contact_emails TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_auth_type CHECK (auth_type IN ('API_KEY', 'OAUTH2', 'BASIC_AUTH', 'JWT', 'NONE'))
);

-- Create indexes for faster lookups
CREATE INDEX idx_apis_system_id ON apis(system_id);
CREATE INDEX idx_apis_name ON apis(name);

-- Add comments to table and columns
COMMENT ON TABLE apis IS 'Stores information about APIs within systems';
COMMENT ON COLUMN apis.id IS 'Unique identifier for the API';
COMMENT ON COLUMN apis.system_id IS 'Reference to the system that contains this API';
COMMENT ON COLUMN apis.name IS 'Name of the API';
COMMENT ON COLUMN apis.description IS 'Description of the API';
COMMENT ON COLUMN apis.auth_type IS 'Authentication type used by the API';
COMMENT ON COLUMN apis.spec_link IS 'URL link to the API specification document';
COMMENT ON COLUMN apis.department IS 'Department responsible for the API';
COMMENT ON COLUMN apis.contact_name IS 'Name of the contact person for the API';
COMMENT ON COLUMN apis.contact_emails IS 'Comma-separated list of contact email addresses';
COMMENT ON COLUMN apis.created_at IS 'Timestamp when the API was created';
COMMENT ON COLUMN apis.updated_at IS 'Timestamp when the API was last updated';
