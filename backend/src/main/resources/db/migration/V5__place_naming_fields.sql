ALTER TABLE building
    ADD COLUMN official_name VARCHAR(200),
    ADD COLUMN display_name VARCHAR(160),
    ADD COLUMN label_visible BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE poi
    ADD COLUMN official_name VARCHAR(200),
    ADD COLUMN display_name VARCHAR(160),
    ADD COLUMN label_visible BOOLEAN NOT NULL DEFAULT TRUE;

UPDATE building
SET official_name = name,
    display_name = name;

UPDATE poi
SET official_name = name,
    display_name = name;

COMMENT ON COLUMN building.name IS 'Backward-compatible canonical name; normally official_name when known';
COMMENT ON COLUMN building.official_name IS 'Source-backed formal name; null when no formal name is verified';
COMMENT ON COLUMN building.display_name IS 'Short user-facing map label; falls back to name';
COMMENT ON COLUMN building.label_visible IS 'Whether the building may appear in the student-facing label layers';
COMMENT ON COLUMN poi.official_name IS 'Source-backed formal place name; null when no formal name is verified';
COMMENT ON COLUMN poi.display_name IS 'Short user-facing map label; falls back to name';
COMMENT ON COLUMN poi.label_visible IS 'Whether the POI may appear in the student-facing label layers';
