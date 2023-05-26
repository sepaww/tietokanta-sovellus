from flask import Flask
from flask import redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
import psycopg2
from sqlalchemy import text
from sqlalchemy import LargeBinary
from io import BytesIO
import base64
from datetime import datetime



app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///postgres"
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
        
def give_user_id():
    ret=db.session.execute(text("SELECT id FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()
    return ret[0]

@app.route("/")
def index():
    #test sql
    del_session_vals()
    sql = text("SELECT id, password FROM users")
    result = db.session.execute(sql)
    return render_template("index.html")

@app.route("/home", methods=["POST", "GET"])
def home():
    if "username" not in session:
        name = request.form["name"]
        name_hash=generate_password_hash(name)
        passw = request.form["pass"]
    
        sql = text("SELECT id, password, is_admin FROM users WHERE name=:username")
        result = db.session.execute(sql, {"username": name})
        if result.rowcount!=0:
            result = result.fetchone()
            hash=result[1]
            is_admin=result[2]
            ident=result[0]
            print(hash)    
            if check_password_hash(hash, passw):
                
                session["username"]=name
                session["auth"]=name_hash
                sql=text("SELECT * FROM shops")
                result = db.session.execute(sql).fetchall()
                return render_template("home.html", id=is_admin, shop_list=result, ident=ident)
            return render_template("index_witherr.html")
    elif auth_check(session["username"], session["auth"]):
        
        sql = text("SELECT id, password, is_admin FROM users WHERE name=:username")
        result = db.session.execute(sql, {"username": session["username"]}).fetchone()
        ident=result[0]
        is_admin=result[2]
        sql=text("SELECT * FROM shops")
        result = db.session.execute(sql).fetchall()
        return render_template("home.html", id=is_admin, shop_list=result, ident=ident)
    del session["username"]
    del session["auth"]   
    return render_template("index_witherr.html")

@app.route("/register", methods=["POST"])
def register():
    del_session_vals()
    return render_template("register.html")


@app.route("/REGCHECK", methods=["POST", "GET"])
def REGCHECK():
    name = request.form["name"]
    passw = request.form["pass"]
    passw2=request.form["pass2"]
    
    if passw!=passw2:
        return render_template("index_witherr.html")
    
    sql = text("SELECT id, password FROM users WHERE name=:name")
    result = db.session.execute(sql, {"name": name})
    if result.rowcount==0:
        session["username"]=name
        session["auth"]=generate_password_hash(name)
        hash=generate_password_hash(passw)
        sql=text("INSERT INTO users (name, password, is_admin) VALUES (:name, :pass, :false)")
        db.session.execute(sql, {"name": name, "pass": hash, "false": False})
        db.session.commit()
        
        return redirect("/home")
    return render_template("index_witherr.html")


@app.route("/homeshop/<int:id>", methods=["POST", "GET"])
def homeshop(id):
    
    sql=text("SELECT * FROM shops WHERE id = :id")
    result = db.session.execute(sql, {"id": id}).fetchone()
    
    sql=text("SELECT comments.comment, comments.date, comments.likes, users.name, comments.id, comments.user_id, comments.target_id FROM comments JOIN users ON comments.user_id = users.id WHERE comments.target_id = :id")
    result2 = db.session.execute(sql, {"id": id}).fetchall()
    sorted_sql = sorted(result2, key=lambda x: x[2])
    sorted_sql.reverse()
    
    ratings=db.session.execute(text("SELECT rating FROM ratings WHERE target_id= :id"), {"id": id}).fetchall()
    if len(ratings)==0:
        avg_rate=0
    else:
        summ=0
        for rate in ratings:
            summ+=rate[0]
        avg_rate=round(summ/len(ratings), 1)
    
        
    
    return render_template("shoppage.html", info=result, comments=sorted_sql, avgrate=avg_rate, tid=id)

    
@app.route("/logout", methods=["POST", "GET"])
def logout():
    del session["username"]
    del session["auth"]
    return redirect("/")

@app.route("/adminpage", methods=["POST", "GET"])
def adminpage():
    if session["is_admin"]==True:
        return render_template("adminpage.html")
    return redirect("/")









@app.route("/like/<int:cid>/<int:tid>", methods=["POST", "GET"])
def like(cid, tid):
    if not auth_check(session["username"], session["auth"]):
        return render_template("index_witherr.html")
    uid=db.session.execute(text("SELECT id FROM users WHERE name = :name"), {"name": session["username"]}).fetchone()[0]
    sql=text("SELECT * FROM likes WHERE target_id = :id AND user_id = :uid")
    result = db.session.execute(sql, {"id": cid, "uid": uid}).fetchall()
    if len(result)!=0:
        sql=text("DELETE FROM likes WHERE target_id = :id AND user_id = :uid")
        db.session.execute(sql, {"id": cid, "uid": uid})
        db.session.commit()
        sql=text("UPDATE comments SET likes = likes - 1 WHERE id = :cid")
        db.session.execute(sql, {"cid": cid})
        db.session.commit()
    else:
        sql=text("INSERT INTO likes (target_id, user_id) VALUES (:tid, :uid)")
        db.session.execute(sql, {"tid": cid, "uid": uid})
        db.session.commit()
        sql=text("UPDATE comments SET likes = likes + 1 WHERE id = :cid")
        db.session.execute(sql, {"cid": cid})
        db.session.commit()
    return redirect(url_for('homeshop', id=tid))
        
@app.route("/addcomment", methods=["POST", "GET"])
def addcomment():
    content = str(request.form["comment"])
    shopid=request.form["id"]
    datetim = datetime.now()
    datetim = str(datetim.strftime("%Y-%m-%d %H:%M"))
    sql=text("SELECT id FROM users WHERE name = :name")
    kayttajaid = db.session.execute(sql, {"name": session["username"]}).fetchone()[0]
    print(kayttajaid)
    likes=0
    sql=text("INSERT INTO comments (user_id, comment, target_id, likes, date) VALUES (:uid, :cmt, :tid, :lik, :dat)")
    db.session.execute(sql, {"uid": kayttajaid, "cmt": content, "tid": shopid, "lik": likes, "dat": datetim})
    db.session.commit()
    return redirect(url_for('homeshop', id=int(shopid)))
        
@app.route("/addstore", methods=["POST", "GET"])
def addstore():
    
    class shop(db.Model):
        __tablename__="shops"
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255))
        cord_x = db.Column(db.Integer)
        cord_y = db.Column(db.Integer)
        has_pic=db.Column(db.Boolean)
        picture = db.Column(db.LargeBinary)
        
    name=request.form["name"]
    sql=text("SELECT id FROM shops WHERE name=:name")
    result = db.session.execute(sql, {"name": name})
    if result.rowcount!=0:
        return redirect("/adminpage")
    
    
    x=request.form["x"]
    y=request.form["y"]
    pic=request.files.get("picture")
    if pic is None or pic.filename == "":
         shop_data=shop(name=name, cord_x=x, cord_y=y,has_pic=False, picture=None)
    else:
        shop_data=shop(name=name, cord_x=x, cord_y=y,has_pic=True, picture=pic.read())
    
    ##sql=text("INSERT INTO shops (name, cord_x, cord_y, picture) VALUES (:name, :cord_x, :cord_y, :pic)")
    db.session.add(shop_data)
    db.session.commit()
    return redirect("/adminpage")

@app.route("/additem", methods=["POST"])
def additem():
    sql=text("SELECT id FROM shops WHERE name=:name")
    shop_name=request.form["shop_name"]
    result=db.session.execute(sql, {"name": shop_name})
    if result.rowcount==0:
        return redirect("/adminpage")
    
    id=result.fetchone()
    price=request.form["price"]
    item_name=request.form["item_name"]
    sql=text("INSERT INTO products (name, price, shop_id) VALUES (:name, :price, :id)")
    result=db.session.execute(sql, {"name": item_name, "price": price, "id": id})
    return redirect("/adminpage")

@app.route("/addrating/<int:tid>", methods=["POST"])
def addrating(tid):
    rate= request.form.get("rating")
    if not rate:
        return redirect(url_for('homeshop', id=tid))
    rate=request.form["rating"]
    if auth_check(session["username"], session["auth"]):
        id=give_user_id()
        print("xd")
        result=db.session.execute(text("SELECT rating FROM ratings WHERE user_id = :id AND target_id = :tid"), {"id": id, "tid": tid}).fetchall()
        if len(result)==0:
            db.session.execute(text("INSERT INTO ratings (user_id, rating, target_id) VALUES (:uid, :rate, :tid)"), {"uid": id, "rate": rate, "tid": tid})
            db.session.commit()
        else:    
            db.session.execute(text("UPDATE ratings SET rating = :rate WHERE target_id = :tid AND user_id = :uid;"), {"uid": id, "rate": rate, "tid": tid})
            db.session.commit()
        return redirect(url_for('homeshop', id=tid))
    return redirect("/logout")












if __name__ == '__main__':
    app.run(debug=True)