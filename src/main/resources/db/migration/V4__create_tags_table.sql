-- Create tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name field for faster lookups
CREATE INDEX idx_tags_name ON tags(name);

-- Add comments to table and columns
COMMENT ON TABLE tags IS 'Stores tags that can be assigned to APIs for categorization';
COMMENT ON COLUMN tags.id IS 'Unique identifier for the tag';
COMMENT ON COLUMN tags.name IS 'Unique name of the tag';
COMMENT ON COLUMN tags.created_at IS 'Timestamp when the tag was created';
