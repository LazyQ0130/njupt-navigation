ALTER TABLE campus
    ADD COLUMN data_source VARCHAR(40) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN verification_status VARCHAR(40) NOT NULL DEFAULT 'UNVERIFIED',
    ADD COLUMN source_id VARCHAR(128),
    ADD COLUMN source_updated_at TIMESTAMPTZ;

ALTER TABLE building
    ALTER COLUMN height DROP NOT NULL,
    ALTER COLUMN height DROP DEFAULT,
    ADD COLUMN height_source VARCHAR(40) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN data_source VARCHAR(40) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN verification_status VARCHAR(40) NOT NULL DEFAULT 'UNVERIFIED',
    ADD COLUMN source_id VARCHAR(128),
    ADD COLUMN source_updated_at TIMESTAMPTZ;

ALTER TABLE poi
    ADD COLUMN data_source VARCHAR(40) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN verification_status VARCHAR(40) NOT NULL DEFAULT 'UNVERIFIED',
    ADD COLUMN source_id VARCHAR(128),
    ADD COLUMN source_updated_at TIMESTAMPTZ;

ALTER TABLE map_feature
    ADD COLUMN data_source VARCHAR(40) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN verification_status VARCHAR(40) NOT NULL DEFAULT 'UNVERIFIED',
    ADD COLUMN source_id VARCHAR(128),
    ADD COLUMN source_updated_at TIMESTAMPTZ;

ALTER TABLE building_entrance
    ADD COLUMN data_source VARCHAR(40) NOT NULL DEFAULT 'UNKNOWN',
    ADD COLUMN verification_status VARCHAR(40) NOT NULL DEFAULT 'UNVERIFIED',
    ADD COLUMN source_id VARCHAR(128),
    ADD COLUMN source_updated_at TIMESTAMPTZ;

ALTER TABLE building ADD CONSTRAINT building_verification_status_check
    CHECK (verification_status IN ('UNVERIFIED', 'SOURCE_VERIFIED', 'MANUALLY_REVIEWED', 'FIELD_VERIFIED'));
ALTER TABLE poi ADD CONSTRAINT poi_verification_status_check
    CHECK (verification_status IN ('UNVERIFIED', 'SOURCE_VERIFIED', 'MANUALLY_REVIEWED', 'FIELD_VERIFIED'));
ALTER TABLE map_feature ADD CONSTRAINT map_feature_verification_status_check
    CHECK (verification_status IN ('UNVERIFIED', 'SOURCE_VERIFIED', 'MANUALLY_REVIEWED', 'FIELD_VERIFIED'));
ALTER TABLE building_entrance ADD CONSTRAINT entrance_verification_status_check
    CHECK (verification_status IN ('UNVERIFIED', 'SOURCE_VERIFIED', 'MANUALLY_REVIEWED', 'FIELD_VERIFIED', 'PENDING_FIELD_VERIFICATION'));

UPDATE building SET data_source = 'SYNTHETIC', source_id = 'phase1-demo'
WHERE external_id LIKE 'demo-%';
UPDATE poi SET data_source = 'SYNTHETIC', source_id = 'phase1-demo'
WHERE external_id LIKE 'demo-%';
UPDATE map_feature SET data_source = 'SYNTHETIC', source_id = 'phase1-demo'
WHERE external_id LIKE 'demo-%';

CREATE INDEX building_source_idx ON building (data_source, source_id);
CREATE INDEX poi_source_idx ON poi (data_source, source_id);
CREATE INDEX map_feature_source_idx ON map_feature (data_source, source_id);
CREATE INDEX entrance_source_idx ON building_entrance (data_source, source_id);
