#################################################
# Imports
#################################################

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Homepage")


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start a session
    session = Session(engine)

    # Query for precipitation data for the last year
    data = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= "2016-08-23") \
        .order_by(Measurement.date) \
        .all()

    # Close the session
    session.close()

    # Convert query results to a dictionary
    data_dict = {date: prcp for date, prcp in data}

    # Return JSON response
    return jsonify(data_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Start a session
    session = Session(engine)

    # Query for all information on each Station
    data = session.query(
        Station.station,
        Station.name,
        Station.latitude,
        Station.longitude,
        Station.elevation
    ).all()

    # Close the session
    session.close()

    # Convert query results to a list of dictionaries
    data_formatted = []
    for station, name, latitude, longitude, elevation in data:
        data_dict = {
            'station': station,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation
        }
        data_formatted.append(data_dict)

    # Return JSON response
    return jsonify(data_formatted)


@app.route("/api/v1.0/tobs")
def tobs():

    # Start a session
    session = Session(engine)

    # Query for dates and temperatures of the most active station over the last year
    data = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == "USC00519281", Measurement.date >= "2016-08-23") \
        .order_by(Measurement.date) \
        .all()

    # Close the session
    session.close()

    # Convert the query results to a list of dictionaries
    data_formatted = [{'Date': date, 'Temp': tobs} for date, tobs in data]

    # Return JSON response
    return jsonify(data_formatted)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    try:
        # Format the input date properly
        start_formatted = dt.datetime.strptime(start_date, "%Y%m%d").date()

        # Start a session
        session = Session(engine)

        # Query for min, max, and average temperature data from the specified start date to the latest date
        data = session.query(
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ).filter(Measurement.date >= start_formatted).all()

        # Close the session
        session.close()

        # Format the query output into a dictionary
        results_dict = {
            'Minimum Temp': data[0][0],
            'Maximum Temp': data[0][1],
            'Average Temp': round(data[0][2], 2)
        }

        # Return JSON response
        return jsonify(results_dict)

    except:
        return jsonify({
            "error": "Start date not found. Please enter a date in the format 'YYYYMMDD' between 2010-01-01 and 2017-08-23"
        }), 404

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    try:
        # Format the input dates properly
        start_formatted = dt.datetime.strptime(start_date, "%Y%m%d").date()
        end_formatted = dt.datetime.strptime(end_date, "%Y%m%d").date()

        # Start a session
        session = Session(engine)

        # Query for min, max, and average temperature data from the specified start date to the specified end date
        data = session.query(
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ).filter(
            Measurement.date >= start_formatted,
            Measurement.date <= end_formatted
        ).all()

        # Close the session
        session.close()

        # Format the query output into a dictionary
        results_dict = {
            'Minimum Temp': data[0][0],
            'Maximum Temp': data[0][1],
            'Average Temp': round(data[0][2], 2)
        }

        # Return JSON response
        return jsonify(results_dict)

    except:
        return jsonify({
            "error": "Dates not found. Please enter start and end dates in the format 'YYYYMMDD' between 2010-01-01 and 2017-08-23"
        }), 404


#################################################
# Run the App
#################################################

if __name__ == '__main__':
    app.run(debug=True)