-- Create api_tags junction table for many-to-many relationship
CREATE TABLE api_tags (
    api_id UUID NOT NULL REFERENCES apis(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (api_id, tag_id)
);

-- Create index on tag_id for faster lookups when querying by tag
CREATE INDEX idx_api_tags_tag_id ON api_tags(tag_id);

-- Add comments to table and columns
COMMENT ON TABLE api_tags IS 'Junction table for many-to-many relationship between APIs and tags';
COMMENT ON COLUMN api_tags.api_id IS 'Reference to the API';
COMMENT ON COLUMN api_tags.tag_id IS 'Reference to the tag';
