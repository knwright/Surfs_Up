import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine('sqlite:///Resources/hawaii.sqlite', echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Routes
@app.route("/")
def welcome():
    """List of all available API routes."""
    return (
        "Hawaii Precipitation and Weather Data<br/><br/>"
        "Pick from the available routes below:<br/><br/>"
        "Precipitation from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/precipitation<br/><br/>"
        "A list of all the weather stations in Hawaii.<br/>"
        "/api/v1.0/stations<br/><br/>"
        "Temperature Observations (tobs) from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/tobs<br/><br/>"
        "Returns the Average, Max and Min temperatures for a given range of dates.<br/>"
        "/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd<br/><br/>"
        "Returns the Average, Max and Min temperature for a given date.<br/>"
        "/api/v1.0/temp/yyyy-mm-dd<br/><br/>"
    )

# Convert the query results to a Dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return Dates and Temperatures from the last year."""
    results = session.query(Measurement.date, func.avg(Measurement.prcp)).\
                        filter(Measurement.date > '2016-08-23').\
                        group_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation = []
    for result in results:
        row = {}
        row['date'] = result[0]
        row['total'] = float(result[1])
        precipitation.append(row)    
    return jsonify(precipitation)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    results = session.query(Station.name).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    station_list = list(np.ravel(results))
    return jsonify(station_list)

# Query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    results = session.query(Measurement.tobs).filter(Measurement.date>'2016-08-23').all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    tobs_list = [record.tobs for record in results]
    return jsonify(tobs_list)
        
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd")
def query_dates(start_date, end_date):
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobes), func.min(Measurement.tobs)).\
       filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
       
    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = float(result[0])
        row["High"] = float(result[1])
        row["Low"] = float(result[2])
        data_list.append(row)

    return jsonify(data_list)


# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/temp/yyyy-mm-dd")
def given_date(date):
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == date).all()
  
    # Query all the stations and for the given date.
    data_list = []
    for result in results:
        row = {}
        row["Date"] = result[0]
        row["Average Temperature"] = float(result[1])
        row["High"] = float(result[2])
        row["Low"] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)