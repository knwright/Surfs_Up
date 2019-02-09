import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine('sqlite:///hawaii.sqlite', echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save a reference to the measurement table as 'Measurement'
Measurement = Base.classes.measurements

# Save a reference to the station table as 'Station'
Station = Base.classes.stations

# Create session (link) from Python to the DB
session = Session(engine)

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
        "Precipiation from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/precipitation<br/><br/>"
        "A list of all the weather stations in Hawaii.<br/>"
        "/api/v1.0/stations<br/><br/>"
        "Temperature Observations (tobs) from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/tobs<br/><br/>"
        "Enter a date range (i.e., 2017-02-04/2017-02-15) to see the min, max and avg temperature for that range.<br/>"
        "/api/v1.0/temp/<start>/<end><br/>"
        "Enter a single date (i.e., 2017-02-05) to see the min, max and avg temperature since that date.<br/>"
        "/api/v1.0/temp/<start><br/><br/>"
    )

# Convert the query results to a Dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
    Convert the query results to a dictionary using date as the 'key 'and 'tobs' as the value."""


    # Retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date > begin_date).\
                        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation_data = [results]
        
    return jsonify(precipitation_data)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    station_list = []
    for result in results:
        row = {}
        row["Station"] = stations.station
        row["Station Name"] = stations.name
        row["Latitude"] = stations.latitude
        row["Longitude"] = stations.longitude
        row["Elevation"] = stations.elevation
        station_list.append(row)
    
    return jsonify(station_list)

# Query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= "2016-01-01", Measurement.date <= "2017-01-01").\
                    all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    tobs_list = []
    for result in results:
        row = {}
        row["Station"] = result[0]
        row["Date"] = result[1]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)
    
    return jsonify(tobs_list)
        
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/temp/<start>/<end>")
def calc_stats(start=None, end=None):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    begin_end = []
    
    for Tmin, Tmax, Tavg in results:
        begin_end_dict = {}
        begin_end_dict["Min Temp"] = Tmin
        begin_end_dict["Max Temp"] = Tmax
        begin_end_dict["Avg Temp"] = Tavg
        begin_end.append(begin_end_dict)
    
    return jsonify(begin_end)

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/temp/<start>")
def start_stats(start=None):
    """Return a json list of the minimum temperature, the average temperature, and the
    max temperature for a given start date"""
    
    # Query all the stations and for the given date. 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_stats = []
    
    for Tmin, Tmax, Tavg in results:
        temp_stats_dict = {}
        temp_stats_dict["Min Temp"] = Tmin
        temp_stats_dict["Max Temp"] = Tmax
        temp_stats_dict["Avg Temp"] = Tavg
        temp_stats.append(temp_stats_dict)
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)