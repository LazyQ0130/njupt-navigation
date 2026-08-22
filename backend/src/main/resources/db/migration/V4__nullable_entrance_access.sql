ALTER TABLE building_entrance
    ALTER COLUMN walking_access DROP NOT NULL,
    ALTER COLUMN walking_access DROP DEFAULT,
    ALTER COLUMN cycling_access DROP NOT NULL,
    ALTER COLUMN cycling_access DROP DEFAULT,
    ALTER COLUMN accessible DROP NOT NULL,
    ALTER COLUMN accessible DROP DEFAULT,
    ADD COLUMN vehicle_access BOOLEAN,
    ADD COLUMN opening_hours VARCHAR(160);
