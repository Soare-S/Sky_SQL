from sqlalchemy import create_engine, text
from plotting_map import plotting_delayed_map

QUERY_FLIGHT_BY_ID = "SELECT airlines.airline as AIRLINE, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY, " \
                     "flights.ORIGIN_AIRPORT, flights.DESTINATION_AIRPORT " \
                     "FROM flights JOIN airlines ON flights.airline = airlines.id WHERE flights.ID = :id"

QUERY_PERCENTAGE_ROUTE_DELAY = "SELECT ORIGIN_AIRPORT, DESTINATION_AIRPORT, ROUND((delayed_flights * 100.0/ " \
                               "total_flights ), 2) as percentage FROM (SELECT ORIGIN_AIRPORT, DESTINATION_AIRPORT, " \
                               "SUM(CASE WHEN DEPARTURE_DELAY > 0 THEN 1 ELSE 0 END) AS delayed_flights, COUNT(*) AS " \
                               "total_flights FROM flights GROUP BY ORIGIN_AIRPORT, DESTINATION_AIRPORT) AS subquery"

QUERY_AIRPORTS_LON_AND_LAT = "SELECT IATA_CODE as CODE, LATITUDE, LONGITUDE FROM airports"

QUERY_DELAYED_FLIGHTS_BY_AIRLINE = "SELECT airlines.airline as AIRLINE, flights.ID as FLIGHT_ID, " \
                                   "flights.DEPARTURE_DELAY as DELAY, flights.ORIGIN_AIRPORT, " \
                                   "flights.DESTINATION_AIRPORT FROM flights JOIN airlines ON flights.airline = " \
                                   "airlines.id WHERE airlines.airline = :airline AND DELAY > 0;"

QUERY_DELAYED_FLIGHTS_BY_AIRPORT = "SELECT airlines.airline as AIRLINE, flights.ID as FLIGHT_ID, " \
                                   "flights.DEPARTURE_DELAY as DELAY, flights.ORIGIN_AIRPORT, " \
                                   "flights.DESTINATION_AIRPORT FROM flights JOIN airlines ON flights.airline = " \
                                   "airlines.id WHERE flights.ORIGIN_AIRPORT = :airport AND DELAY > 0;"

QUERY_FLIGHTS_BY_DATE = "SELECT airlines.airline as AIRLINE, flights.ID as FLIGHT_ID, " \
                       "flights.DEPARTURE_DELAY as DELAY, flights.ORIGIN_AIRPORT, " \
                       "flights.DESTINATION_AIRPORT FROM flights JOIN airlines ON flights.airline = " \
                       "airlines.id WHERE flights.DAY = :day AND flights.MONTH = :month AND flights.YEAR = :year;"


class FlightData:
    """
    The FlightData class is a Data Access Layer (DAL) object that provides an
    interface to the flight data in the SQLITE data. When the object is created,
    the class forms connection to the sqlite data file, which remains active
    until the object is destroyed.
    """

    def __init__(self, db_uri):
        """
        Initialize a new engine using the given data URI
        """
        self._engine = create_engine(db_uri)

    def _execute_query(self, query, params):
        """
        Execute an SQL query with the params provided in a dictionary,
        and returns a list of records (dictionary-like objects).
        If an exception was raised, print the error, and return an empty list.
        """
        with self._engine.connect() as connection:
            query = text(query)
            try:
                results = connection.execute(query, params)
                output = results.fetchall()
                # Get the column names from the query result
                column_names = results.keys()
                if type(params) is list:
                    # Create a list of dictionaries with the desired format
                    converted_results = {}
                    for row in output:
                        converted_results[row[0]] = {'lat': float(row[1]), 'long': float(row[2])}
                else:
                    # Convert the records to a list of dictionary-like objects
                    converted_results = [dict(zip(column_names, record)) for record in output]
                return converted_results
            except Exception as e:
                print(e)
                return []

    def get_flight_by_id(self, flight_id):
        """
        Searches for flight details using flight ID.
        If the flight was found, returns a list with a single record.
        """
        params = {'id': flight_id}
        return self._execute_query(QUERY_FLIGHT_BY_ID, params)

    def get_routes_average_delay(self):
        """
        Retrieve route average delay data and plot it on a map.
        :return: A map displaying route average delay data.
        """
        get_coordinates = self._execute_query(QUERY_AIRPORTS_LON_AND_LAT, params=[])
        get_delays = self._execute_query(QUERY_PERCENTAGE_ROUTE_DELAY, params=None)
        return plotting_delayed_map(get_delays, get_coordinates)

    def get_delayed_flights_by_airline(self, airline_input):
        """
        Retrieve delayed flights by airline.
        :param airline_input: The name of the airline to search for.
        :return: A list of delayed flight details for the specified airline.
        """
        params = {'airline': airline_input}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRLINE, params)

    def get_delayed_flights_by_airport(self, airport_input):
        """
        Retrieve delayed flights by airport.
        :param airport_input: The code of the airport to search for.
        :return: A list of delayed flight details for the specified airport.
        """
        params = {'airport': airport_input}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRPORT, params)

    def get_flights_by_date(self, day, month, year):
        """
        Retrieve flights by date.
        :param day: The day of the flight departure.
        :param month: The month of the flight departure.
        :param year: The year of the flight departure.
        :return: A list of flight details for the specified date.
        """
        params = {'day': day,
                  'month': month,
                  'year': year}
        return self._execute_query(QUERY_FLIGHTS_BY_DATE, params)

    def __del__(self):
        """
        Closes the connection to the data when the object is about to be destroyed
        """
        self._engine.dispose()
