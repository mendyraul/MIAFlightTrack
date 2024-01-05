
import requests
import psycopg2
import psycopg2.extras
from flaskr.config import API_KEY, DB_HOST, DB_USER, DB_NAME, DB_PASSWORD

# Function to connect to the database
def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


# Function to truncate flights_staging table
def truncate_staging_table():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE flights_staging;")
        conn.commit()
        print("flights_staging table truncated successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to commit staging data into history table
def load_to_history_table():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.callproc('process_flight_data')
        conn.commit()
        print("flights_staging table processed into history table successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to insert flight data into the database
def insert_flights(flights):
    conn = connect_db()
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO flights_staging (flight_number, status, airline_code, dep_airport, dep_scheduled, dep_estimated, 
    dep_actual, arr_airport, arr_scheduled, arr_estimated, arr_actual, duration)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (flight_number, dep_scheduled) DO NOTHING;
    """

    for flight in flights:
        flight_number = flight['flight_iata']
        dep_scheduled = flight['dep_time']
        arr_scheduled = flight['arr_time']

        # Check if flight_number, dep_scheduled, and arr_scheduled are not NULL (aka None)
        if flight_number is not None and dep_scheduled is not None and arr_scheduled is not None:
            cursor.execute(insert_query, (
                flight_number, flight['status'], flight['airline_iata'],
                flight['dep_iata'], dep_scheduled, flight['dep_estimated'],
                flight['dep_actual'], flight['arr_iata'], arr_scheduled,
                flight['arr_estimated'], flight['arr_actual'], flight['duration']
            ))

    print("Records inserted.")
    conn.commit()
    cursor.close()
    conn.close()

# Function to grab API response
def process_flights(response):
    flights = []
    for schedule in response['response']:
        flight_info = {
            'airline_iata': schedule.get('airline_iata'),
            'flight_iata': schedule.get('flight_iata'),
            'status': schedule.get('status'),
            'dep_iata': schedule.get('dep_iata'),
            'dep_time': schedule.get('dep_time'),
            'dep_estimated': schedule.get('dep_estimated'),
            'dep_actual': schedule.get('dep_actual'),
            'arr_iata': schedule.get('arr_iata'),
            'arr_time': schedule.get('arr_time'),
            'arr_estimated': schedule.get('arr_estimated'),
            'arr_actual': schedule.get('arr_actual'),
            'duration': schedule.get('duration')
        }
        flights.append(flight_info)
    return flights

def main():
    # API Endpoints for Departing and Arriving Flights
    API_KEY = "2f222ffa-6ceb-4261-ae17-4369ebca0eca"
    dep_iata = 'MIA'
    dep_url = f'https://airlabs.co/api/v9/schedules?dep_iata={dep_iata}&api_key={API_KEY}'
    arr_iata = 'MIA'
    arr_url = f'https://airlabs.co/api/v9/schedules?arr_iata={arr_iata}&api_key={API_KEY}'

    # Get Departing Flights Data
    print("Script beginning...")
    dep_result = requests.get(dep_url)
    if dep_result.status_code == 200:
        flights_dep = process_flights(dep_result.json())
        print("API response acquired.")
    else:
        print(f"Failed to retrieve departing flights. Status code: {dep_result.status_code}")
        print(dep_result.text)
        flights_dep = []

    # Get Arriving Flights Data
    arr_result = requests.get(arr_url)
    if arr_result.status_code == 200:
        flights_arr = process_flights(arr_result.json())
    else:
        print(f"Failed to retrieve arriving flights. Status code: {arr_result.status_code}")
        print(arr_result.text)
        flights_arr = []

    # Truncate the table before inserting new data
    truncate_staging_table()

    # Insert data into the database
    insert_flights(flights_dep + flights_arr)

    # Run the proc to merge data into history table
    load_to_history_table()




if __name__ == "__main__":
    main()
    
