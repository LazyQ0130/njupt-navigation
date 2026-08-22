ALTER TABLE building
    ADD COLUMN dormitory_zone VARCHAR(40),
    ADD COLUMN building_number VARCHAR(16);

COMMENT ON COLUMN building.dormitory_zone IS 'Source-backed dormitory zone name; null when unconfirmed or not applicable';
COMMENT ON COLUMN building.building_number IS 'Short dormitory building number without the 号楼 suffix';
