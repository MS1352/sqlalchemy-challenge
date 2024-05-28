# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine)

# Assign the measurement class to a variable called `Measurement`
Measurement = Base.classes.measurement

# Assign the station class to a variable called `Station`
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform a query to retrieve the precipitation data for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    precipitation_dict = dict(precipitation_data)
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations
    stations = session.query(Station.station).all()
    
    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observation data for the last year."""
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Perform a query to retrieve the temperature observation data for the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= one_year_ago).\
                    filter(Measurement.station == most_active_station).all()
    
    # Convert the query results to a dictionary
    tobs_dict = dict(tobs_data)
    
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return the minimum, average, and maximum temperatures for the given start date."""
    # Perform a query to retrieve the temperature data starting from the given start date
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
               filter(Measurement.date >= start).all()
    
    # Convert the query results to a list
    temp_list = list(np.ravel(temps))
    
    return jsonify(temp_list)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return the minimum, average, and maximum temperatures for the given start and end dates."""
    # Perform a query to retrieve the temperature data within the given start and end dates
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert the query results to a list
    temp_list = list(np.ravel(temps))
    
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)
