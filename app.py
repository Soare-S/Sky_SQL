from flask import Flask, request, render_template
from datetime import datetime
import data

app = Flask(__name__)
SQLITE_URI = 'sqlite:///data/flights.sqlite3'
IATA_LENGTH = 3

# Initialize the data manager
data_manager = data.FlightData(SQLITE_URI)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/api/delayed_flights_by_airline', methods=['GET'])
def api_delayed_flights_by_airline():
    airline_input = request.args.get('airline')
    results = data_manager.get_delayed_flights_by_airline(airline_input)
    if not results:
        error = "Invalid airline name"
        return render_template('home.html', error=error)
    else:
        return render_template('home.html', results=results)


@app.route('/api/delayed_flights_by_airport', methods=['GET'])
def api_delayed_flights_by_airport():
    airport_input = request.args.get('airport')
    results = data_manager.get_delayed_flights_by_airport(airport_input)
    if not results:
        error = "Invalid airport code"
        return render_template('home.html', error=error)
    else:
        return render_template('home.html', results=results)


@app.route('/api/flight_by_id', methods=['GET'])
def api_flight_by_id():
    try:
        id_input = int(request.args.get('flight_id'))
    except ValueError:
        error = "Invalid flight ID"
        return render_template('home.html', error=error)

    results = data_manager.get_flight_by_id(id_input)
    return render_template('home.html', results=results)


@app.route('/api/flights_by_date', methods=['GET'])
def api_flights_by_date():
    date_input = request.args.get('date')
    try:
        date = datetime.strptime(date_input, '%d/%m/%Y')
    except ValueError:
        error = 'Invalid date or format, please enter DD/MM/YYYY'
        return render_template('home.html', error=error)

    results = data_manager.get_flights_by_date(date.day, date.month, date.year)
    if not results:
        error = f"Not available results for date {date_input}"
        return render_template('home.html', error=error)
    else:
        return render_template('home.html', results=results)


@app.route('/api/percentage_delayed_flights_on_map', methods=['GET'])
def api_percentage_delayed_flights_on_map():
    data_manager.get_routes_average_delay()
    return render_template("flight_map.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return render_template('405.html'), 405


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

