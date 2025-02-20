# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, render_template, jsonify
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
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
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
    return render_template("index.html")

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query the last 12 months of precipitation data
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    precipitation_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .order_by(Measurement.date)
        .all()
    )
    
    # Convert to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query the station data
    stations_data = session.query(Station.station, Station.name).all()
    
    # Convert to a list of dictionaries
    stations_list = [{"station": station, "name": name} for station, name in stations_data]
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Use the most active station (from previous query)
    most_active_station_id = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Query the temperature data for the most active station over the last 12 months
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    tobs_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station_id)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    
    # Convert to a list of dictionaries
    tobs_list = [{"date": date, "temperature": temp} for date, temp in tobs_data]
    
    return jsonify(tobs_list)

if __name__ == "__main__":
    app.run(debug=True)