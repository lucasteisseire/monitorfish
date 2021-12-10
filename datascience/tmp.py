from src.db_config import create_engine


def initialize_test_positions():
    e = create_engine("monitorfish_remote")
    e.execute("DROP TABLE IF EXISTS interim.test_positions;")

    migration = """
    CREATE TABLE interim.test_positions AS SELECT * FROM positions WHERE date_time > '2021-12-01';
    CREATE INDEX ON interim.test_positions USING btree (date_time DESC);
    CREATE INDEX ON interim.test_positions USING btree (external_reference_number, date_time DESC);
    CREATE INDEX ON interim.test_positions USING btree (internal_reference_number, date_time DESC);
    CREATE INDEX ON interim.test_positions USING btree (ircs, date_time DESC);
    """

    e.execute(migration)


def migrate_test_positions():
    e = create_engine("monitorfish_remote")
    migration = """
    ALTER TABLE interim.test_positions
        ADD COLUMN is_at_port BOOLEAN,
        ADD COLUMN meters_from_previous_position REAL,
        ADD COLUMN time_since_previous_position INTERVAL,
        ADD COLUMN average_speed REAL,
        ADD COLUMN is_fishing BOOLEAN;
    """
    e.execute(migration)
