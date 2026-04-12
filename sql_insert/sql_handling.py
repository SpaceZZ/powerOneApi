import logging
import datetime
import mysql.connector

logger = logging.getLogger(__name__)


def create_connection(config):
    """
    Create SQL connection using credentials from the Configurator object.
    :param config: Configurator instance
    :return: mysql.connector connection
    """
    return mysql.connector.connect(
        host=config.db_host,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
    )


def handle_sql_archiving(results, config):
    """
    Archives all measurement results to the database in a single transaction.
    :param results: dict with measurement data
    :param config: Configurator instance (provides DB credentials)
    """
    if not config.db_host:
        logger.warning("No [DATABASE] section in config.ini — skipping SQL archiving")
        return

    try:
        mydb = create_connection(config)
    except mysql.connector.Error as ex:
        logger.error(f"Could not connect to database: {ex}")
        return

    now = datetime.datetime.now().isoformat()

    try:
        mycursor = mydb.cursor()
        sql_insert = """
            INSERT INTO measurements(`SYSTEM`, NAME, `TIMESTAMP`, VALUE, DESCRIPTION, QUALITY, UNIT)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        rows = [_format_values(key, result, now) for key, result in results.items()]
        mycursor.executemany(sql_insert, rows)
        mydb.commit()  # single commit for the entire batch
        mycursor.close()
        logger.info(f"Archived {len(rows)} measurements to database")
    except mysql.connector.Error as ex:
        logger.error(f"Database insert failed: {ex}")
        mydb.rollback()
    finally:
        mydb.close()


def _format_values(key, values, time_now):
    """Formats a single measurement row for SQL insertion."""
    value = values["value"]
    quality = "1" if value is not None else "0"
    return ("PV", key, time_now, value, "Kapalkowo", quality, values["unit"])
