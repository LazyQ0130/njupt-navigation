CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE campus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    boundary geometry(MultiPolygon, 4326),
    default_longitude DOUBLE PRECISION NOT NULL,
    default_latitude DOUBLE PRECISION NOT NULL,
    default_zoom DOUBLE PRECISION NOT NULL DEFAULT 15,
    default_pitch DOUBLE PRECISION NOT NULL DEFAULT 50,
    default_bearing DOUBLE PRECISION NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT campus_longitude_check CHECK (default_longitude BETWEEN -180 AND 180),
    CONSTRAINT campus_latitude_check CHECK (default_latitude BETWEEN -90 AND 90)
);

CREATE TABLE building (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    external_id VARCHAR(128) UNIQUE,
    name VARCHAR(160) NOT NULL,
    aliases TEXT[] NOT NULL DEFAULT '{}',
    category VARCHAR(40) NOT NULL,
    geometry geometry(MultiPolygon, 4326) NOT NULL,
    height DOUBLE PRECISION NOT NULL DEFAULT 10,
    min_height DOUBLE PRECISION NOT NULL DEFAULT 0,
    color VARCHAR(16) NOT NULL DEFAULT '#D7E3F4',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT building_height_check CHECK (height >= min_height AND min_height >= 0)
);

CREATE TABLE building_entrance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    building_id UUID NOT NULL REFERENCES building(id) ON DELETE CASCADE,
    external_id VARCHAR(128) UNIQUE,
    name VARCHAR(128) NOT NULL,
    location geometry(Point, 4326) NOT NULL,
    walking_access BOOLEAN NOT NULL DEFAULT TRUE,
    cycling_access BOOLEAN NOT NULL DEFAULT FALSE,
    accessible BOOLEAN NOT NULL DEFAULT FALSE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE poi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    building_id UUID REFERENCES building(id) ON DELETE SET NULL,
    external_id VARCHAR(128) UNIQUE,
    name VARCHAR(160) NOT NULL,
    aliases TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    category VARCHAR(40) NOT NULL,
    location geometry(Point, 4326) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE path_node (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    external_id VARCHAR(128) UNIQUE,
    location geometry(Point, 4326) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE path_edge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    external_id VARCHAR(128) UNIQUE,
    source_node_id UUID NOT NULL REFERENCES path_node(id),
    target_node_id UUID NOT NULL REFERENCES path_node(id),
    name VARCHAR(160),
    geometry geometry(LineString, 4326) NOT NULL,
    length_m DOUBLE PRECISION NOT NULL,
    walking_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    cycling_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    accessible BOOLEAN NOT NULL DEFAULT TRUE,
    night_access BOOLEAN NOT NULL DEFAULT TRUE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT path_edge_nodes_check CHECK (source_node_id <> target_node_id),
    CONSTRAINT path_edge_length_check CHECK (length_m > 0)
);

CREATE TABLE scenario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    code VARCHAR(80) NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT,
    category VARCHAR(40) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (campus_id, code)
);

CREATE TABLE scenario_stop (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES scenario(id) ON DELETE CASCADE,
    poi_id UUID REFERENCES poi(id) ON DELETE RESTRICT,
    building_id UUID REFERENCES building(id) ON DELETE RESTRICT,
    sequence_no INTEGER NOT NULL,
    title VARCHAR(160) NOT NULL,
    instructions TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT scenario_stop_target_check CHECK (num_nonnulls(poi_id, building_id) = 1),
    UNIQUE (scenario_id, sequence_no)
);

CREATE TABLE map_correction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campus_id UUID NOT NULL REFERENCES campus(id),
    correction_type VARCHAR(40) NOT NULL,
    description TEXT NOT NULL,
    target_type VARCHAR(40),
    target_id UUID,
    anonymous_session_hash VARCHAR(128) NOT NULL,
    source_ip_hash VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    reviewed_by UUID,
    review_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE admin_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(100) NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE map_correction
    ADD CONSTRAINT map_correction_reviewer_fk FOREIGN KEY (reviewed_by) REFERENCES admin_user(id);

CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(120) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    value_type VARCHAR(24) NOT NULL DEFAULT 'STRING',
    description TEXT,
    sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by UUID REFERENCES admin_user(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE operation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID REFERENCES admin_user(id),
    operation VARCHAR(80) NOT NULL,
    target_type VARCHAR(80),
    target_id UUID,
    summary JSONB NOT NULL DEFAULT '{}',
    source_ip_hash VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX campus_boundary_gix ON campus USING GIST (boundary);
CREATE INDEX building_geometry_gix ON building USING GIST (geometry);
CREATE INDEX building_name_trgm_idx ON building USING GIN (name gin_trgm_ops);
CREATE INDEX building_aliases_gin_idx ON building USING GIN (aliases);
CREATE INDEX entrance_location_gix ON building_entrance USING GIST (location);
CREATE INDEX poi_location_gix ON poi USING GIST (location);
CREATE INDEX poi_name_trgm_idx ON poi USING GIN (name gin_trgm_ops);
CREATE INDEX poi_aliases_gin_idx ON poi USING GIN (aliases);
CREATE INDEX poi_keywords_gin_idx ON poi USING GIN (keywords);
CREATE INDEX path_node_location_gix ON path_node USING GIST (location);
CREATE INDEX path_edge_geometry_gix ON path_edge USING GIST (geometry);
CREATE INDEX path_edge_source_idx ON path_edge (source_node_id);
CREATE INDEX path_edge_target_idx ON path_edge (target_node_id);
CREATE INDEX map_correction_status_idx ON map_correction (status, created_at);
CREATE INDEX operation_log_target_idx ON operation_log (target_type, target_id);

INSERT INTO campus (
    code, name, default_longitude, default_latitude, default_zoom, default_pitch, default_bearing
) VALUES (
    'NJUPT_XIANLIN', '南京邮电大学仙林校区', 118.9140, 32.1040, 15.2, 50, -12
);

INSERT INTO system_config (config_key, config_value, value_type, description)
VALUES
    ('routing.walking_speed_mps', '1.3', 'DECIMAL', '步行预计速度，米/秒'),
    ('routing.cycling_speed_mps', '4.0', 'DECIMAL', '校园骑行预计速度，米/秒'),
    ('navigation.snap_max_distance_m', '35', 'INTEGER', 'GPS 最大吸附距离'),
    ('navigation.reroute_threshold_m', '45', 'INTEGER', '偏航重规划距离阈值'),
    ('navigation.reroute_cooldown_seconds', '20', 'INTEGER', '偏航重规划冷却时间');

