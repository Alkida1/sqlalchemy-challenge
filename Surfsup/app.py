# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

from flask import Flask, jsonify

# Set up the database
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Set up Flask
app = Flask(__name__)

# Define the routes
@app.route("/")
def home():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;'>/api/v1.0/&lt;start&gt;</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;/&lt;end&gt;'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data."""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the precipitation data
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary from the query results and return as JSON
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset."""
    # Query the station data
    stations = session.query(Station.station, Station.name).all()

    # Create a list of dictionaries from the query results and return as JSON
    station_list = [{"station": station, "name": name} for station, name in stations]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations of the most active station for the previous year."""
    # Calculate the date 1 year ago from the last data point in the database
    most_active_station=session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()[0]

    # Query the temperature observations for the most active station for the previous year
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station[0]).\
            filter(Measurement.date >= one_year_ago).all()
    
@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    """Return the minimum, maximum, and average temperatures for a given start date."""
    # Query the temperature data
    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    # Create a list of dictionaries from the query results and return as JSON
    temp_list = [{"min_temp": temp[0], "max_temp": temp[1], "avg_temp": temp[2]} for temp in temp_data]
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start, end):
    """Return the minimum, maximum, and average temperatures for a given date range."""
    # Query the temperature data
    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a list of dictionaries from the query results and return as JSON
    temp_list = [{"min_temp": temp[0], "max_temp": temp[1], "avg_temp": temp[2]} for temp in temp_data]
    return jsonify(temp_list)
