
from sqlalchemy import text
from datab import db

from help_funcs import form_check, auth_check, name_check, check_password_hash, del_session_vals, passw_check
from flask import redirect, render_template, request, session, make_response
import secrets
from werkzeug.security import check_password_hash, generate_password_hash












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



def homeshop(id):
    name = session["username"]
    is_admin = db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name":name}).fetchone()[0]
    sql = text("SELECT * FROM shops WHERE id = :id")
    result = db.session.execute(sql, {"id": id}).fetchone()

    sql = text("SELECT comments.comment, comments.date, comments.likes, users.name, comments.id, comments.user_id, comments.target_id FROM comments JOIN users ON comments.user_id = users.id WHERE comments.target_id = :id")
    result2 = db.session.execute(sql, {"id": id}).fetchall()
    sorted_sql = sorted(result2, key=lambda x: x[2])
    sorted_sql.reverse()

    ratings = db.session.execute(
        text("SELECT rating FROM ratings WHERE target_id= :id"), {"id": id}).fetchall()
    items = db.session.execute(text(
        "SELECT name, price FROM products WHERE shop_id= :id ORDER BY name ASC"), {"id": id}).fetchall()

    if len(ratings) == 0:
        avg_rate = 0
    else:
        summ = 0
        for rate in ratings:
            summ += rate[0]
        avg_rate = round(summ/len(ratings), 1)

    return render_template("shoppage.html", info=result, comments=sorted_sql, avgrate=avg_rate, tid=id, itemlist=items, is_admin=is_admin)



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


def adminpage():
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:
            if form_check(request.form["csrf_token"]):
                
                return render_template("adminpage.html")
    return redirect("/")

def pic_giver(id):
    sql = text("SELECT picture FROM shops WHERE shops.id=:id")
    result = db.session.execute(sql, {"id":id})
    data = result.fetchone()[0]
    response = make_response(bytes(data))
    response.headers.set("Content-Type", "image/png")
    return response 