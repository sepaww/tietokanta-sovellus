
from sqlalchemy import text

from random import choice, uniform
from help_funcs import form_check, auth_check, list_of_items
from flask import redirect,request, session
from datab import db









def addstore():
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:

            name = request.form["name"]
            if type(name)!=str or name=="":
                return ("no valid name given")
            sql = text("SELECT id FROM shops WHERE name=:name")
            result = db.session.execute(sql, {"name": name})
            if result.rowcount != 0:
                return "already exists"

            x = request.form["x"]
            if x=="":
                x=0
            else:
                try:
                    x=int(x)
                except:
                    return ("given x cord is not a valid integer")
            y = request.form["y"]
            if y=="":
                y=0
            else:
                try:
                    y=int(y)
                except:
                    return ("given y cord is not a valid integer")
                
            pic = request.files.get("picture")

            if pic is None or pic.filename == "":
                db.session.execute(text("INSERT INTO shops (name, cord_x, cord_y,has_pic) VALUES (:name, :x, :y, :hasp)"), {
                                   "name": name, "x": x, "y": y, "hasp": False})
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


def additem():
    
    if not form_check(request.form["csrf_token"]):
        return redirect("/")
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:

            sql = text("SELECT id FROM shops WHERE name=:name")
            shop_name = request.form["shop_name"]
            result = db.session.execute(sql, {"name": shop_name})
            if result.rowcount == 0:
                return ("no given shop exists")

            id = result.fetchone()[0]
            price = request.form["price"]
            if price=="":
                return ("no price given")
            try:
                float(price)
            except:
                return("given price is not a known number")
            price=round(float(price),2)
            item_name = request.form["item_name"]
            if item_name=="":
                return ("no name for item has been given")
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