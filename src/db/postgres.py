import psycopg2
from psycopg2 import Error


def get_cursor():
    global cursor, connector
    try:
        connector = psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
            user="postgres",
            password="YourPW",
            host="localhost",
            port="5432",
            dbname="trading"))

        cursor = connector.cursor()
        return cursor, connector
    except(Exception, Error) as error:
        print("Error: DB connection.", error)
