# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

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
    return "Welcome to the Hawaii Weather API!"

@app.route("/api/v1/precipitation")
def precipitation():
    # Calculate the date one year from the most recent date
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_ago = recent_date_dt - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_str).all()
    
    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1/stations")
def stations():
    # Query all stations
    results = session.query(Station.station, Station.name).all()
    
    # Convert query results to a list of dictionaries
    stations_list = [{"station": station, "name": name} for station, name in results]

    return jsonify(stations_list)

@app.route("/api/v1/tobs")
def tobs():
    # Find the most active station
    most_active_station_query = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    
    most_active_station = most_active_station_query.station

    # Calculate the date one year from the most recent date
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_ago = recent_date_dt - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')

    # Query temperature observations for the most active station
    results = session.query(Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago_str
    ).all()
    
    # Convert query results to a list
    tobs_list = [tobs for (tobs,) in results]

    return jsonify(tobs_list)

@app.route("/api/v1/temp_stats")
def temp_stats():
    # Find the most active station
    most_active_station_query = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    
    most_active_station = most_active_station_query.station

    # Calculate the date one year from the most recent date
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date_dt = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_ago = recent_date_dt - relativedelta(years=1)
    one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')

    # Query temperature data for the most active station
    results = session.query(Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago_str
    ).all()
    
    # Convert query results to a list
    temperatures = [tobs for (tobs,) in results]
    
    # Calculate summary statistics
    temp_stats = {
        'max': max(temperatures),
        'min': min(temperatures),
        'avg': np.mean(temperatures)
    }

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)