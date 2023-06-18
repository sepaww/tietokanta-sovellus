
from sqlalchemy import text
from help_funcs import form_check, auth_check, comment_check, give_user_id
from flask import redirect, render_template, request, session, url_for
from datetime import datetime

from datab import db










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


def delete(cid, sid):
    if auth_check(session["username"], session["auth"]):
        if db.session.execute(text("SELECT is_admin FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]:
            db.session.execute(text("DELETE FROM likes WHERE target_id = :id"), {"id": cid})
            db.session.execute(text("DELETE FROM comments WHERE id = :id"), {"id": cid})
            db.session.commit()
            print(sid)
    return redirect(url_for('homeshop', id=sid))


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
    
    name = db.session.execute(text("SELECT name FROM shops WHERE id = :id"), {
                              "id": idd}).fetchone()
    ret_prices = []
    for item in items:
        price = db.session.execute(text("SELECT price FROM products WHERE name = :name AND shop_id = :id"), {
                                   "name": item[0], "id": idd}).fetchone()[0]
        ret_prices.append((item[0], price, price*item[1]))
    print(name, id)
    return render_template("result.html", price=round(cheapest,2), name=name, id=idd, na=not_available, infolist=ret_prices)


def findcheapest():
    print("d")
    amount=request.form.get("amount")
    print(amount)
    if amount==None or amount=="":
        return redirect("/home")
    amount = request.form["amount"]

    amount = int(amount) + 1
    if type(amount) != int:
        print("notint")
        return redirect("/home")
    if amount == 0:
        return redirect("/home")
    options = db.session.execute(
        text("SELECT DISTINCT name FROM products ORDER BY name ASC")).fetchall()
    print("trhough")
    return render_template("cheap_seeker.html", amount=amount, options=options)