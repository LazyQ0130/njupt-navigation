ALTER TABLE map_feature
    DROP CONSTRAINT map_feature_type_check;

ALTER TABLE map_feature
    ADD CONSTRAINT map_feature_type_check CHECK (feature_type IN (
        'CAMPUS_BOUNDARY', 'GREEN', 'WATER', 'SPORT', 'PLAZA',
        'ROAD_MAIN', 'ROAD_PEDESTRIAN', 'DORMITORY_ZONE'
    ));
