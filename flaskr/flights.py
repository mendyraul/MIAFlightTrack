from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required

from flask import Blueprint, render_template
from flaskr.db import connect_db
from datetime import datetime 

bp = Blueprint('flights', __name__)




@bp.route('/flights')
def flights():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM flights_staging')
        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        flights_data = []
        for row in rows:
            flight = dict(zip(columns, row))
            # Format datetime objects
            for time_field in ['dep_scheduled', 'dep_estimated', 'dep_actual', 'arr_scheduled', 'arr_estimated', 'arr_actual']:
                if flight[time_field] and isinstance(flight[time_field], datetime):
                    flight[time_field] = flight[time_field].strftime('%I:%M %p')
            flights_data.append(flight)

    except Exception as e:
        print(f"Error occurred: {e}")
        flights_data = []
    finally:
        cursor.close()
        db.close()
    return render_template('flights/flights.html', flights=flights_data)



