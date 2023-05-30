from flask import Flask
from flask import redirect, render_template, request, session, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
import psycopg2
from sqlalchemy import text
from sqlalchemy import LargeBinary
from io import BytesIO
import base64
from datetime import datetime
from help_funcs import name_check, passw_check, list_of_items, comment_check
from random import choice, uniform
import secrets
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG'] = True
app.jinja_env.filters['b64encode'] = base64.b64encode


db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")


def auth_check(name, hash):
    if check_password_hash(hash, name):
        return True
    return False


def del_session_vals():
    if "username" in session:
        del session["username"]
    if "auth" in session:
        del session["auth"]


def form_check(form):
    if session["csrf_token"] != form:
        return False
    return True
    

def give_user_id():
    ret = db.session.execute(text("SELECT id FROM users WHERE name = :name"), {
                             "name": session["username"]}).fetchone()
    return ret[0]


@app.route("/")
def index():
    del_session_vals()
    return render_template("index.html")


@app.route("/logcheck", methods=["POST"])
def logcheck():
    name = request.form.get("name")
    passw = request.form.get("pass")
    if not name or not passw:
        print("no name or pass", name, passw)
        return render_template("index_witherr.html")

    name = request.form["name"]
    passw = request.form["pass"]
    if not name_check(name) or not passw_check(passw):
        return render_template("index_witherr.html")
    name_hash = generate_password_hash(name)

    sql = text("SELECT id, password, is_admin FROM users WHERE name=:username")
    result = db.session.execute(sql, {"username": name})
    if result.rowcount != 0:
        result = result.fetchone()
        hash = result[1]
        if check_password_hash(hash, passw):

            session["username"] = name
            session["auth"] = name_hash
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/home")
        return render_template("index_witherr.html")


@app.route("/home", methods=["POST", "GET"])
def home():
    if "username" not in session:
        redirect("/")
    elif auth_check(session["username"], session["auth"]):

        sql = text(
            "SELECT id, password, is_admin FROM users WHERE name=:username")
        result = db.session.execute(
            sql, {"username": session["username"]}).fetchone()
        ident = result[0]
        is_admin = result[2]
        sql = text("SELECT * FROM shops")
        result = db.session.execute(sql).fetchall()
        length = len(result)
        return render_template("home.html", id=is_admin, shoplist=result, ident=ident, length=length)
    del_session_vals()
    return render_template("index_witherr.html")


@app.route("/showpic/<pic>", methods=["POST", "GET"])
def showpic(pic):
    response = make_response(pic)
    response.headers.set("Content-Type", "image/png")
    return response


@app.route("/register", methods=["POST"])
def register():
    del_session_vals()
    return render_template("register.html")


@app.route("/REGCHECK", methods=["POST", "GET"])
def REGCHECK():
    name = request.form["name"]
    passw = request.form["pass"]
    passw2 = request.form["pass2"]
    is_admin = False
    if not name_check(name) or not passw_check(passw):
        return render_template("index_witherr.html")
    if passw != passw2:
        return render_template("index_witherr.html")

    sql = text("SELECT id, password FROM users WHERE name=:name")
    result = db.session.execute(sql, {"name": name})
    if result.rowcount == 0:
        if len(db.session.execute(text("SELECT * FROM users")).fetchall()) == 0:
            is_admin = True
        session["username"] = name
        session["auth"] = generate_password_hash(name)
        session["csrf_token"] = secrets.token_hex(16)
        hash = generate_password_hash(passw)
        sql = text(
            "INSERT INTO users (name, password, is_admin) VALUES (:name, :pass, :false)")
        db.session.execute(
            sql, {"name": name, "pass": hash, "false": is_admin})
        db.session.commit()

        return redirect("/home")
    return render_template("index_witherr.html")


@app.route("/homeshop/<int:id>", methods=["POST", "GET"])
def homeshop(id):

    sql = text("SELECT * FROM shops WHERE id = :id")
    result = db.session.execute(sql, {"id": id}).fetchone()

    sql = text("SELECT comments.comment, comments.date, comments.likes, users.name, comments.id, comments.user_id, comments.target_id FROM comments JOIN users ON comments.user_id = users.id WHERE comments.target_id = :id")
    result2 = db.session.execute(sql, {"id": id}).fetchall()
    sorted_sql = sorted(result2, key=lambda x: x[2])
    sorted_sql.reverse()

    ratings = db.session.execute(
        text("SELECT rating FROM ratings WHERE target_id= :id"), {"id": id}).fetchall()
    items = db.session.execute(text(
        "SELECT name, price FROM products WHERE shop_id= :id"), {"id": id}).fetchall()

    if len(ratings) == 0:
        avg_rate = 0
    else:
        summ = 0
        for rate in ratings:
            summ += rate[0]
        avg_rate = round(summ/len(ratings), 1)

    return render_template("shoppage.html", info=result, comments=sorted_sql, avgrate=avg_rate, tid=id, itemlist=items)


@app.route("/findcheapest", methods=["POST", "GET"])
def findcheapest():
    print("d")
    amount = request.form["amount"]

    amount = int(amount) + 1
    if type(amount) != int:
        print("notint")
        return redirect("/home")
    if amount == 0:
        return redirect("/home")
    options = db.session.execute(
        text("SELECT DISTINCT name FROM products")).fetchall()
    print("trhough")
    return render_template("cheap_seeker.html", amount=amount, options=options)


@app.route("/submit_wanted_items", methods=["POST", "GET"])
def submit_wanted_items():
    not_available = False
    amount = request.form["amount"]
    amount = int(amount)
    items = []
    for i in range(0, amount):
        name = str("select" + str(i))
        if request.form.get(name):
            item = request.form[name]
        else:
            item = None
        name = str(str(i) + str(0) + str(0) + str(0))
        print(name)
        if request.form.get(name):
            amount = request.form[name]
            amount = int(amount)
        else:
            amount = 0

        if item != None and amount > 0:
            items.append((item, amount))
    print(items)
    # find cheapest store

    ids = db.session.execute(text("SELECT id FROM shops")).fetchall()
    if len(ids) == 0:
        return redirect("/home")
    unavailables = [0]*(len(ids)+1)
    sums = [0]*(len(ids)+1)

    for temp_id in ids:
        id = temp_id[0]

        for temp_item in items:
            item = temp_item[0]

            price = db.session.execute(text("SELECT price FROM products WHERE name = :name AND shop_id = :id"), {
                                       "name": item, "id": id}).fetchone()

            if price == None:
                unavailables[id] = 1
                break
            price = price[0]
            sums[id] += round(price*temp_item[1], 2)
    print(sums)

    for i in range(len(unavailables)):
        if unavailables[i] == 1:
            sums[i] += 9999999999
    sums[0] += 9999999999
    cheapest = min(sums)

    if cheapest >= 9999999999:
        not_available = True
        return render_template("result.html", na=not_available)
    idd = ids[sums.index(cheapest)-1][0]
    print(idd)
    name = db.session.execute(text("SELECT name FROM shops WHERE id = :id"), {
                              "id": idd}).fetchone()
    ret_prices = []
    for item in items:
        price = db.session.execute(text("SELECT price FROM products WHERE name = :name AND shop_id = :id"), {
                                   "name": item[0], "id": idd}).fetchone()[0]
        ret_prices.append((item[0], price, price*item[1]))
    print(name, id)
    return render_template("result.html", price=cheapest, name=name, id=idd, na=not_available, infolist=ret_prices)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    del_session_vals()
    return redirect("/")


@app.route("/adminpage", methods=["POST", "GET"])
def adminpage():
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:
            if form_check(request.form["csrf_token"]):
                
                return render_template("adminpage.html")
    return redirect("/")


@app.route("/like/<int:cid>/<int:tid>", methods=["POST", "GET"])
def like(cid, tid):
    if not auth_check(session["username"], session["auth"]):
        return render_template("index_witherr.html")
    uid = db.session.execute(text("SELECT id FROM users WHERE name = :name"), {
                             "name": session["username"]}).fetchone()[0]
    sql = text("SELECT * FROM likes WHERE target_id = :id AND user_id = :uid")
    result = db.session.execute(sql, {"id": cid, "uid": uid}).fetchall()
    if len(result) != 0:
        sql = text("DELETE FROM likes WHERE target_id = :id AND user_id = :uid")
        db.session.execute(sql, {"id": cid, "uid": uid})
        db.session.commit()
        sql = text("UPDATE comments SET likes = likes - 1 WHERE id = :cid")
        db.session.execute(sql, {"cid": cid})
        db.session.commit()
    else:
        sql = text("INSERT INTO likes (target_id, user_id) VALUES (:tid, :uid)")
        db.session.execute(sql, {"tid": cid, "uid": uid})
        db.session.commit()
        sql = text("UPDATE comments SET likes = likes + 1 WHERE id = :cid")
        db.session.execute(sql, {"cid": cid})
        db.session.commit()
    return redirect(url_for('homeshop', id=tid))


@app.route("/addcomment", methods=["POST", "GET"])
def addcomment():
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    content = str(request.form["comment"])
    if not comment_check(content):
        return "too large comment"
    shopid = request.form["id"]
    datetim = datetime.now()
    datetim = str(datetim.strftime("%Y-%m-%d %H:%M"))
    sql = text("SELECT id FROM users WHERE name = :name")
    kayttajaid = db.session.execute(
        sql, {"name": session["username"]}).fetchone()[0]
    print(kayttajaid)
    likes = 0
    sql = text(
        "INSERT INTO comments (user_id, comment, target_id, likes, date) VALUES (:uid, :cmt, :tid, :lik, :dat)")
    db.session.execute(sql, {"uid": kayttajaid, "cmt": content,
                       "tid": shopid, "lik": likes, "dat": datetim})
    db.session.commit()
    return redirect(url_for('homeshop', id=int(shopid)))


@app.route("/addstore", methods=["POST", "GET"])
def addstore():
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:

            name = request.form["name"]
            sql = text("SELECT id FROM shops WHERE name=:name")
            result = db.session.execute(sql, {"name": name})
            if result.rowcount != 0:
                return "already exists"

            x = request.form["x"]
            y = request.form["y"]
            pic = request.files.get("picture")

            if pic is None or pic.filename == "":
                db.session.execute(text("INSERT INTO shops (name, cord_x, cord_y,has_pic, picture) VALUES (:name, :x, :y, :hasp, :pic)"), {
                                   "name": name, "x": x, "y": y, "hasp": False, "pic": 0})
            else:
                picc = request.files["picture"]
                pic = picc.read()
                if len(pic) > 1000*1024:
                    return "Too big file"
                db.session.execute(text("INSERT INTO shops (name, cord_x, cord_y,has_pic, picture) VALUES (:name, :x, :y, :hasp, :pic)"), {
                                   "name": name, "x": x, "y": y, "hasp": True, "pic": pic})
            db.session.commit()
            return redirect("/home")
    return redirect("/")


@app.route("/additem", methods=["POST"])
def additem():
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:

            sql = text("SELECT id FROM shops WHERE name=:name")
            shop_name = request.form["shop_name"]
            result = db.session.execute(sql, {"name": shop_name})
            if result.rowcount == 0:
                return redirect("/home")

            id = result.fetchone()[0]
            price = request.form["price"]
            item_name = request.form["item_name"]
            if len(db.session.execute(text("SELECT price FROM products WHERE name = :name AND shop_id = :id"), {"name": item_name, "id": id}).fetchall()) != 0:
                db.session.execute(text("UPDATE products SET price = :price WHERE name = :name AND shop_id = :id"), {
                                   "name": item_name, "id": id, "price": price})
            else:
                sql = text(
                    "INSERT INTO products (name, price, shop_id) VALUES (:name, :price, :id)")
                db.session.execute(
                    sql, {"name": item_name, "price": price, "id": id})
            db.session.commit()
            return redirect("/home")
    return redirect("/")


@app.route("/addrating/<int:tid>", methods=["POST"])
def addrating(tid):
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    rate = request.form.get("rating")
    if not rate:
        return redirect(url_for('homeshop', id=tid))
    rate = request.form["rating"]
    if auth_check(session["username"], session["auth"]):
        id = give_user_id()
        print("xd")
        result = db.session.execute(text("SELECT rating FROM ratings WHERE user_id = :id AND target_id = :tid"), {
                                    "id": id, "tid": tid}).fetchall()
        if len(result) == 0:
            db.session.execute(text("INSERT INTO ratings (user_id, rating, target_id) VALUES (:uid, :rate, :tid)"), {
                               "uid": id, "rate": rate, "tid": tid})
            db.session.commit()
        else:
            db.session.execute(text("UPDATE ratings SET rating = :rate WHERE target_id = :tid AND user_id = :uid;"), {
                               "uid": id, "rate": rate, "tid": tid})
            db.session.commit()
        return redirect(url_for('homeshop', id=tid))
    return redirect("/logout")


@app.route("/massadd", methods=["POST"])
def massadd():
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    shops = db.session.execute(text("SELECT id FROM shops")).fetchall()
    ids = []
    for id in shops:
        ids.append(id[0])
    for _ in range(1000):
        id = choice(ids)
        name = choice(list_of_items)
        price = round(uniform(0.1, 20.0), 2)
        if len(db.session.execute(text("SELECT price FROM products WHERE name = :name AND shop_id = :id"), {"name": name, "id": id}).fetchall()) != 0:
            db.session.execute(text("UPDATE products SET price = :price WHERE name = :name AND shop_id = :id"), {
                               "name": name, "id": id, "price": price})
        else:
            sql = text(
                "INSERT INTO products (name, price, shop_id) VALUES (:name, :price, :id)")
            db.session.execute(sql, {"name": name, "price": price, "id": id})
            db.session.commit()
    return redirect("/home")


if __name__ == '__main__':
    app.run(debug=True)
