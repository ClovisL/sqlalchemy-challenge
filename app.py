import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, request, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link from Python to DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data
    # Calculate the date 1 year ago from the last data point in the database
    previous = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous).all()

    # Dictionary with the date as the key and precipitation as the value
    precip = {date: prcp for date, prcp in results}

    session.close()
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to show how many stations are available in this dataset
    results = session.query(Station.station).all()

    # Unravel the results into a list
    stations = list(np.ravel(results))

    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Design a query to retrieve the last 12 months of temperature data for the most active station
    # Calculate the date 1 year ago from the last data point in the database
    previous = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and tobs
    # Finds most active station
    mostTemps = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Gets past year of tobs for most active station
    pastYearData = session.query(Measurement.tobs).\
        filter(Measurement.station == mostTemps[0][0]).\
        filter(Measurement.date >= previous).all()

    pastYear = list(np.ravel(pastYearData))

    session.close()
    return jsonify(pastYear)

@app.route("/api/v1.0/<start>")
def stats(start=None):
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*select).\
        filter(Measurement.date >= start).all()
    temps = list(np.ravel(results))
    
    session.close()
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def statsrange(start, end):
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*select).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    temps = list(np.ravel(results))
    
    session.close()
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)