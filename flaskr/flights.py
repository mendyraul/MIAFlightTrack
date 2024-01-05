from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required

from flask import Blueprint, render_template
from flaskr.db import connect_db


bp = Blueprint('flights', __name__)


@bp.route('/flights')
def flights():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM flights_staging')  
    flights_data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('flights/flights.html', flights=flights_data)


