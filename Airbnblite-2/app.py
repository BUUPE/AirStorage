from flask import Flask, Response, request, jsonify, render_template, make_response, flash

from flask_pymongo import pymongo

from database import DatabaseConnection

from Services.UserService import UserService

import hashlib

import datetime

import uuid

app = Flask(__name__)

app.secret_key = "airbnblite"

db = DatabaseConnection()

userService = UserService()


@app.route("/addNewProperty", methods=["GET"])
def getPropertyForm():
    return render_template("addNewProperty.html")


@app.route("/addNewProperty", methods=["POST"])
def addNewProperty():
    document = {

        "name": request.form["name"],

        "propertyType": request.form["type"],

        "price": request.form["price"],

        "user": userService.authorize(request.cookies.get('sid'))


    }

    db.insert("properties", document)

    return render_template('properties.html')

@app.route("/properties", methods=["GET"])
def getProperties():
    properties = db.findMany("properties", {})

    return render_template('properties.html', properties=properties)


@app.route("/", methods=["GET"])
def hello():
    #return Response("<h1> Welcome to AirBNB </h1>", status=200, content_type="text/html")
    return render_template("landing.html")

@app.route("/greeting", methods=["POST"])
def greeting():
    name = request.form["name"]

    hourOfDay = datetime.datetime.now().time().hour

    greeting = ""

    if not name:
        return Response(status=404)

    if hourOfDay < 12:

        greeting = "Good Morning "

    elif hourOfDay > 12 and hourOfDay < 18:

        greeting = "Good Afternoon "

    else:

        greeting = "Good Evening "

    response = greeting + " " + name + "!"

    return Response(response, status=200, content_type="text/html")


@app.route("/login", methods=["GET"])
def getLoginView():
    if request.cookies.get("sid"):
        return render_template("welcome.html")

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]

    password = request.form["password"]
    encryptedPassword = hashlib.sha256(password.encode('UTF-8'))  # Specify encryption method
    encryptedPasswordToStoreInDB = encryptedPassword.hexdigest()

    if userService.authenticate(username, encryptedPasswordToStoreInDB):

        response = make_response(render_template("welcome.html"))

        sid = str(uuid.uuid4())

        session = {

            "sid": sid,

            "username": username

        }

        db.insert("sessions", session)

        response.set_cookie("sid", sid)

        return response

    else:

        flash("Incorrect login credentials")

        return render_template("login.html")

        # return Response("Login was invalid", status=400, content_type="text/html")


@app.route("/register", methods=["GET"])
def getRegisterView():
    if request.cookies.get("sid"):
        return render_template("welcome.html")

    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]

    password = request.form["password"]

    firstname = request.form["first name"]
    lastname = request.form["last name"]
    user = db.findOne("users", {"username": username})
    if user is not None:
        flash("Incorrect login credentials")
        return render_template("register.html")

    else:
        encryptedPassword = hashlib.sha256(password.encode('UTF-8'))  # Specify encryption method
        encryptedPasswordToStoreInDB = encryptedPassword.hexdigest()
        document = {
            "username": username,
            "password": encryptedPasswordToStoreInDB,
            "firstName": firstname,
            "lastName": lastname
        }
        db.insert("users", document)
        return render_template("login.html")



        # return Response("Login was invalid", status=400, content_type="text/html")



@app.route("/account", methods=["GET"])
def getMyAccount():
    user = userService.authorize(request.cookies.get('sid'))

    if user:

        firstName = userService.getFirstName(user)

    else:

        flash("Invalid session")

        return render_template("login.html")

    return render_template("account.html", firstName=firstName, userName=user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
