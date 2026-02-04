
-- neutralization flag for the database
INSERT INTO ir_config_parameter (key, value)
VALUES ('database.is_neutralized', 'true')
    ON CONFLICT (key) DO
       UPDATE SET value = 'true';
