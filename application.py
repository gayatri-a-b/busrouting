# SUMMER CAMPER BUS-ING PYTHON-BASED WEB APPLICATION
import os, sys, json, geopy

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from geopy.geocoders import Nominatim
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.globals.update(apology=apology)
app.jinja_env.globals.update(type=type)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///implementation.db")

# Set up geolocator https://pypi.org/project/geopy/
geolocator = Nominatim(user_agent="gb7777cs50")


###### reference to cs50 FINANCE pset

# LOGIN ALLOWS FOR ONLY ADMIN AND DRIVER, FOR CAMPER SAFETY REGISTRATION IS NOT POSSIBLE
"""Log user in"""
@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via GET
    if request.method == "GET":
        return render_template("login.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username and password
        username = request.form.get("username")
        rows = db.execute("SELECT hash FROM users WHERE username = :username", username=username)
        if rows[0]["hash"] != request.form.get("password"):
            return apology("invalid username and/or password", 403)
        else:
            # Remember which user has logged in
            session["user_id"] = username

            # Redirect user to home page
            if username == "admin":
                return redirect("/admin_dashboard")
            else:
                return redirect("/driver_dashboard")


# LOGOUT
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# HOMEPAGES FOR DRIVER AND ADMIN
@app.route("/")
@login_required
def index():
    # get which user it is and direct them to the corresponding homepage
    user = db.execute("SELECT * FROM users WHERE username=:username", username=session["user_id"])
    if user[0]["username"] == "admin":
       return redirect("/admin_dashboard")
    else:
        return redirect("/driver_dashboard")


# ADMIN_DASHBOARD ACCESSIBLE ONLY TO ADMIN FOR TAKING ROSTER ATTENDANCE THAT SUBMITS TO MAP LOCATIONS
@app.route("/admin_dashboard", methods=['POST', 'GET'])
@login_required
def admin_dashboard():
    # only allow the admin to access /admin_dashboard.html
    if session["user_id"] == "admin":

        # if the admin updates LOCK/RESET attendance, make the corresponding DB changes
        if request.method == "POST":
            # figure out whether LOCK or RESET was hit
            data = request.get_json()
            attendance_action = data["attendance_action"]

            # if lock was hit
            if attendance_action == "lock":
                # get the on_bus campers
                bus_campers = data["bus_campers"]

                # change all the campers to False for on_bus db value
                db.execute("UPDATE campers SET on_bus=:on_bus", on_bus="False")

                # then change on_bus to True for only those campers in bus_campers
                for camper in bus_campers:
                    db.execute("UPDATE campers SET on_bus=:on_bus WHERE camper_name=:camper_name", camper_name=camper, on_bus="True")

            # if reset was hit, change all the campers to false
            elif attendance_action == "reset":
                db.execute("UPDATE campers SET on_bus=:on_bus", on_bus="False")

            # forces the windows refresh in the AJAX success method to make JINJA on the page update
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

        # if page reached via GET, populate the page with the required DB information
        else:
            campers = db.execute("SELECT * FROM campers")
            bus_campers = db.execute("SELECT * FROM campers WHERE on_bus=:on_bus", on_bus="True")
            offbus_campers = db.execute("SELECT * FROM campers WHERE on_bus=:on_bus", on_bus="False")

            return render_template("admin_dashboard.html", campers=campers, bus_campers=bus_campers, offbus_campers=offbus_campers)

    # render error if anyone else besides ADMIN tries to access page
    else:
        return apology("not authorized", 403)


# CAMPER_REGISTRATION ACCESSIBLE ONLY TO ADMIN FOR REGISTERING CAMPERS AND THEIR DROP-OFF ADDRESSES
@app.route("/camper_registration", methods=["GET", "POST"])
@login_required
def camper_registration():
    # only allow the admin to access /camper_registration.html
    if session["user_id"] == "admin":

        # if the admin updates REGISTAR/REMOVE camper for roster, make the corresponding DB changes
        if request.method == "POST":
            # get the camper_name
            camper_name = request.form.get("camper_name")

            # get the camper address and convert it to a lat/lng location
            address = request.form.get("address")
            location = geolocator.geocode(address)

            # get the removed camper name
            removed_camper = request.form.get("removed_camper")

            # get the edit action, whether this is a REGISTAR or REMOVE
            edit_action = request.form["edit_action"]

            # if REGISTRAR was hit
            if edit_action == "add":
                # if no camper name provided
                if not camper_name:
                    return apology("missing name", 403)
                # if no address provided
                elif not address:
                    return apology("missing address", 403)
                # if address does not correspond to a viable lat/lng location
                elif not location:
                    return apology("address has no geographical correspondence", 403)
                # if all the info was provided and correct, insert information into DB
                else:
                    db.execute("INSERT INTO campers (camper_name, address, latitude, longitude) VALUES(:camper_name, :address, :latitude, :longitude)", camper_name=camper_name, address=address, latitude=location.latitude, longitude=location.longitude)

            # if REMOVE was hit
            elif edit_action == "remove":
                # if no camper select in the radio buttons
                if not removed_camper:
                    return apology("missing option", 403)
                # if a camper was selected, remove them from the DB
                else:
                    db.execute("DELETE FROM campers WHERE camper_name = :camper_name", camper_name=removed_camper)

        # whether reached via GET or POST, send the camper data to /camper_registration.html
        campers = db.execute("SELECT * FROM campers")
        return render_template("camper_registration.html", campers=campers)

    # render error if anyone else besides ADMIN tries to access page
    else:
        return apology("not authorized", 403)


# DRIVER_DESTINATION ACCESSIBLE ONLY TO ADMIN FOR ENTERING FINAL DESTINATION OF BUS (STOP FOR STAFF/CAMP-COUNSELORS)
@app.route("/driver_destination", methods=["GET", "POST"])
@login_required
def driver_destination():
    # only allow the admin to access /driver_destination.html
    if session["user_id"] == "admin":

        # if the admin updates SET/RESET final_destination, make the corresponding DB changes
        if request.method == "POST":

            # get the final_destination address and convert it to a lat/lng
            final_destination_address = request.form.get("final_destination_address")
            final_destination_location = geolocator.geocode(final_destination_address)

            # get the action of the button being pressed
            edit_action = request.form["edit_action"]

            # ensure if button was pressed
            if edit_action == "add":
                # if no address provided
                if not final_destination_address:
                    return apology("missing address", 403)
                # if address does not correspond to viable lat/lng
                elif not final_destination_location:
                    return apology("address has no geographical correspondence", 403)
                # if all info works, update the DB
                else:
                    db.execute("UPDATE campers SET address=:address, latitude=:latitude, longitude=:longitude WHERE camper_name=:camper_name", camper_name="final_destination", address=final_destination_address, latitude=final_destination_location.latitude, longitude=final_destination_location.longitude)

        # whether the page was reached via GET or POST, send the final_destination information to /driver_destination.html
        final_destination = db.execute("SELECT * FROM campers WHERE camper_name=:camper_name", camper_name="final_destination")
        return render_template("driver_destination.html", final_destination=final_destination[0])

    # render error if anyone else besides ADMIN tries to access page
    else:
        return apology("not authorized", 403)


# DRIVER_DASHBOARD ACCESSIBLE TO BOTH DRIVER AND ADMIN -- THIS IS THE MAP DISPLAY
@app.route("/driver_dashboard", methods=["GET"])
@login_required
def driver_dashboard():
    # if page reached via GET (accessible to both ADMIN and DRIVER)
    if request.method == "GET":
        # grab the data needed to make the route! (camper information)
        bus_campers = db.execute("SELECT * FROM campers WHERE on_bus=:on_bus", on_bus="True")
        lat = db.execute("SELECT latitude FROM campers WHERE on_bus=:on_bus", on_bus="True")
        lon = db.execute("SELECT longitude FROM campers WHERE on_bus=:on_bus", on_bus="True")
        pointnames = db.execute("SELECT camper_name FROM campers WHERE on_bus=:on_bus", on_bus="True")
        elements = {'latitudes':lat, 'longitudes':lon, 'pointnames':pointnames}

        # separately grab the info about the final destination
        lat_final = db.execute("SELECT latitude FROM campers WHERE camper_name=:camper_name", camper_name="final_destination")
        lon_final = db.execute("SELECT longitude FROM campers WHERE camper_name=:camper_name", camper_name="final_destination")
        elements_final = {'latitudes':lat_final, 'longitudes':lon_final, 'pointnames':"final_destination"}

        # send the information to /driver_dashboard.html
        return render_template("driver_dashboard.html", bus_campers=bus_campers, elements=json.dumps(elements), elements_final=json.dumps(elements_final))


# some methods from CS50 finance pset

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
