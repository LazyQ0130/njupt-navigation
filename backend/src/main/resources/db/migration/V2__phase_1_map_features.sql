CREATE TABLE map_feature (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    external_id VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(160) NOT NULL,
    feature_type VARCHAR(40) NOT NULL,
    geometry geometry(Geometry, 4326) NOT NULL,
    color VARCHAR(16),
    priority INTEGER NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT map_feature_type_check CHECK (feature_type IN (
        'CAMPUS_BOUNDARY', 'GREEN', 'WATER', 'SPORT', 'PLAZA',
        'ROAD_MAIN', 'ROAD_PEDESTRIAN'
    ))
);

CREATE INDEX map_feature_geometry_gix ON map_feature USING GIST (geometry);
CREATE INDEX map_feature_campus_type_idx ON map_feature (campus_id, feature_type, enabled);

UPDATE campus
SET default_longitude = 118.9115,
    default_latitude = 32.1030,
    default_zoom = 16.2,
    default_pitch = 52,
    default_bearing = -18,
    updated_at = now()
WHERE code = 'NJUPT_XIANLIN';
