import mysql.connector
from sql_insert import sqlconfig
import datetime


def create_connection():
    """
    Create SQL connection to the server
    Returns:

    """
    return mysql.connector.connect(
        host=sqlconfig.host,
        user=sqlconfig.user,
        password=sqlconfig.password,
        database=sqlconfig.database
    )


def handle_sql_archiving(results):
    """
    Handles the total insertion and connection fo the sql
    Args:
        results: dictionary with results
    """
    mydb = create_connection()
    # Get the current timestamp
    now = datetime.datetime.now().isoformat()

    for key, result in results.items():
        values = format_values(key, result, now)
        insert_into_sql(mydb, values)

    mydb.close()


def format_values(key, values, time_now):
    # format correctly the values received
    quality = '0'

    value = values['value']
    if value:
        quality = '1'

    values = ('PV', key, time_now, values['value'], 'Kapalkowo', quality, values['unit'])
    return values


def insert_into_sql(connection, values):
    mycursor = connection.cursor()

    # Define the SQL query with placeholders for parameterized query
    sqlInsert = """
           INSERT INTO measurements(`SYSTEM`, NAME, `TIMESTAMP`, VALUE, DESCRIPTION, QUALITY, UNIT) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)
       """

    # Execute the SQL query with the values
    mycursor.execute(sqlInsert, values)

    # Commit the transaction to save changes
    connection.commit()
    mycursor.close()
