import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine('sqlite:///hawaii.sqlite', echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)
# Base.classes.keys()
# Save a reference to the measurement table as 'Measurement'
Measurement = Base.classes.measurement

# Save a reference to the station table as 'Station'
Station = Base.classes.station

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
    results1 = session.query(Measurement.date, func.avg(Measurement.prcp)).\
                        filter(Measurement.date > '2016-08-23').\
                        group_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation= []
    for result in results1:
        row = {}
        row['date'] = result[0]
        row['total'] = float(result[1])
        precipitation.append(row)    
    return jsonify(precipitation)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    results2 = session.query(Station.name).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    station_list = list(np.ravel(results2))
    return jsonify(station_list)

# Query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    results3 = session.query(Measurement.tobs).filter(Measurement.date>'2016-08-23').all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    tobs_list = [record.tobs for record in results3]
    return jsonify(tobs_list)
        
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_sum_start_end(start, end):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    results4 = session.query(func.min(Measurement.tobs).label("min_temp"),
                        func.avg(Measurement.tobs).label("avg_temp"),
                        func.max(Measurement.tobs).label("max_temp")).filter(Measurement.date.between(start,end)).all()


    temp_sum_start_end = list(np.ravel(results4))
    return jsonify(temp_sum_start_end)

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/temp/<start>")
def temp_start_stats(start):
    """Return a json list of the minimum temperature, the average temperature, and the
    max temperature for a given start date"""
    
    # Query all the stations and for the given date. 
    results5 = session.query(func.min(Measurement.tobs).label("min_temp"),
                        func.avg(Measurement.tobs).label("avg_temp"),
                        func.max(Measurement.tobs).label("max_temp")).filter(Measurement.date>=start).all()
    
    temp_start_stats = list(np.ravel(results5))
    return jsonify(temp_start_stats)

if __name__ == '__main__':
    app.run(debug=True)