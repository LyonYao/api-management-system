-- Create systems table
CREATE TABLE systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name field for faster lookups
CREATE INDEX idx_systems_name ON systems(name);

-- Add comment to table
COMMENT ON TABLE systems IS 'Stores information about systems that contain APIs';
COMMENT ON COLUMN systems.id IS 'Unique identifier for the system';
COMMENT ON COLUMN systems.name IS 'Unique name of the system';
COMMENT ON COLUMN systems.description IS 'Description of the system';
COMMENT ON COLUMN systems.created_at IS 'Timestamp when the system was created';
COMMENT ON COLUMN systems.updated_at IS 'Timestamp when the system was last updated';
