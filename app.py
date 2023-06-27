from flask import Flask
from sqlalchemy import text
from flask import redirect, render_template, make_response
from os import getenv
import base64

from help_funcs import del_session_vals

import site_functions
import shop_functions
import admin_functions

app = Flask(__name__)


app.config['DEBUG'] = True
app.jinja_env.filters['b64encode'] = base64.b64encode
app.secret_key = getenv("SECRET_KEY")

import datab
datab.init_db(app)




@app.route("/")
def index():
    del_session_vals()
    return render_template("index.html")


@app.route("/logcheck", methods=["POST"])
def logcheck():
    return site_functions.logcheck()


@app.route("/home", methods=["POST", "GET"])
def home():
    return site_functions.home()


@app.route("/showpic/<int:id>", methods=["POST", "GET"])
def showpic(id):
    return site_functions.pic_giver(id)


@app.route("/register", methods=["GET"])
def register():
    del_session_vals()
    return render_template("register.html")


@app.route("/REGCHECK", methods=["POST"])
def REGCHECK():
    return site_functions.REGCHECK()


@app.route("/homeshop/<int:id>", methods=["POST", "GET"])
def homeshop(id):
    return site_functions.homeshop(id)

@app.route("/findcheapest", methods=["POST", "GET"])
def findcheapest():
    return shop_functions.findcheapest()


@app.route("/submit_wanted_items", methods=["POST", "GET"])
def submit_wanted_items():
    return shop_functions.submit_wanted_items()

@app.route("/logout", methods=["POST", "GET"])
def logout():
    del_session_vals()
    return redirect("/")


@app.route("/adminpage", methods=["POST", "GET"])
def adminpage():
    return site_functions.adminpage()


@app.route("/like/<int:cid>/<int:tid>", methods=["POST", "GET"])
def like(cid, tid):
    return shop_functions.like(cid, tid)


@app.route("/addcomment", methods=["POST", "GET"])
def addcomment():
    return shop_functions.addcomment()


@app.route("/addstore", methods=["POST", "GET"])
def addstore():
    return admin_functions.addstore()

@app.route("/massadd", methods=["POST"])
def massadd():
    return admin_functions.massadd()

@app.route("/additem", methods=["POST"])
def additem():
    return admin_functions.additem()

@app.route("/addrating/<int:tid>", methods=["POST"])
def addrating(tid):
    return shop_functions.addrating(tid)




@app.route("/delete/<int:cid>/<int:sid>", methods=["GET"])
def delete(cid, sid):
    return shop_functions.delete(cid, sid)


if __name__ == '__main__':
    app.run(debug=True)
