import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

recent_date = session.query(Measurement.date).order_by((Measurement.date)).limit(1).all()

print(recent_date)

prev_yr = (dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)).date()

print(prev_yr)

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
        f"Welcome to my Hawaii weather API!<br/>"
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"Temperature Stats: /api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"Temperature Stats: /api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("status:OK")

    #query to retrieve the last 12 months of precipitation data.
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_yr)\
        .filter(Measurement.station == Station.station).all()

    #Convert the query results to a Dictionary using date as the key and prcp as the value.
    precip = []
    for result in results:
        row = {}
        row["date"] = result[0]
        row["prcp"] = result[1]
        precip.append(row)

    #Return the JSON representation of your dictionary.
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    print("status:OK")

    # Query all Stations
    results = session.query(Station.station).\
                 order_by(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)



@app.route("/api/v1.0/tobs")
def tobs():
    print("status:OK")

    # Query all tobs
    results = session.query(Measurement.date,  Measurement.tobs,Measurement.prcp).\
                filter(Measurement.date >= prev_yr).\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()

    # Convert the list to Dictionary
    observations = []
    for prcp, date,tobs in results:
        observations_dict = {}
        observations_dict["prcp"] = prcp
        observations_dict["date"] = date
        observations_dict["tobs"] = tobs
        observations.append(observations_dict)

    return jsonify(observations)


@app.route("/api/v1.0/<startdate>")
def tobs_by_date(startdate):
    print("status:OK")

    # Query tobs
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= recent_date).all()

    # Convert the list to Dictionary
    recent_tobs = []
    for min,avg,max in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        recent_tobs.append(tobs_dict)

    return jsonify(recent_tobs)


@app.route("/api/v1.0/<startdate>/<enddate>")
def date_range(startdate, enddate):
    print("status:OK")

    # Query tobs in range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= recent_date).filter(Measurement.date <= prev_yr).all()

    # Convert the list to Dictionary
    tobs_in_range = []
    for min,avg,max in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_in_range.append(tobs_dict)

    return jsonify(tobs_in_range)


if __name__ == "__main__":
    app.run(debug=True)