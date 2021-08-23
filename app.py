import datetime as dt
import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

app = Flask(__name__)


@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    year_data = session.query(measurement.date, measurement.prcp). \
        filter(measurement.date >= prior_year). \
        filter(measurement.date <= dt.date(2017, 8, 23)).all()

    session.close()

    prcp_dict = {date: prcp for date, prcp in year_data}
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(station.station).all()

    session.close()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    temp_data = session.query(measurement.date, measurement.tobs). \
        filter(measurement.date >= prior_year). \
        filter(measurement.date <= dt.date(2017, 8, 23)). \
        filter(measurement.station == 'USC00519281').all()

    session.close()

    top_station = list(np.ravel(temp_data))

    return jsonify(top_station)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    session = Session(engine)

    if not end:
        temp_data = session.query(measurement.station, func.min(measurement.tobs),
                                  func.max(measurement.tobs), func.avg(measurement.tobs)). \
            filter(measurement.date >= start). \
            group_by(measurement.station).all()

        all_temps = list(np.ravel(temp_data))

        return jsonify(all_temps)

    temp_data = session.query(measurement.station, func.min(measurement.tobs),
                              func.max(measurement.tobs), func.avg(measurement.tobs)). \
        filter(measurement.date >= start). \
        filter(measurement.date <= end). \
        group_by(measurement.station).all()

    session.close()

    all_temps = list(np.ravel(temp_data))

    print(temp_data)

    return jsonify(all_temps)


if __name__ == "__main__":
    app.run(debug=True)
