
from flask import session
from werkzeug.security import check_password_hash
from datab import db
from sqlalchemy import text












def name_check(name):
    if len(name)>20:
        print("bad name")
        return False
    return True
def passw_check(passw):
    if 3 > len(passw) or len(passw) > 30:
        print("bad passw")
        return False
    return True
def comment_check(comment):
    if len(comment)>2000:
        return False
    return True

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








list_of_items=[
    "apples",
    "bananas",
    "carrots",
    "bread",
    "milk",
    "eggs",
    "chicken",
    "rice",
    "potatoes",
    "onions",
    "lettuce",
    "tomatoes",
    "cheese",
    "yogurt",
    "orange juice",
    "pasta",
    "beef",
    "broccoli",
    "salmon",
    "cereal",
    "peanut butter",
    "jam",
    "cookies",
    "chips",
    "soda",
    "water",
    "tea",
    "coffee",
    "sugar",
    "flour",
    "salt",
    "pepper",
    "olive oil",
    "vinegar",
    "mayonnaise",
    "ketchup",
    "mustard",
    "salsa",
    "honey",
    "maple syrup",
    "canned beans",
    "canned tomatoes",
    "canned soup",
    "canned tuna",
    "frozen vegetables",
    "frozen pizza",
    "frozen chicken nuggets",
    "ice cream",
    "chocolate",
    "toilet paper",
    "paper towels",
    "facial tissues",
    "dish soap",
    "laundry detergent",
    "fabric softener",
    "toothpaste",
    "toothbrush",
    "shampoo",
    "conditioner",
    "soap",
    "hand sanitizer",
    "aluminum foil",
    "plastic wrap",
    "ziplock bags",
    "garbage bags",
    "batteries",
    "light bulbs",
    "candles",
    "razors",
    "feminine products",
    "baby diapers",
    "baby wipes",
    "pet food",
    "cat litter",
    "dog treats",
    "dog toys",
    "birdseed",
    "fish food",
    "greeting cards",
    "birthday candles",
    "balloons",
    "party decorations",
    "wrapping paper",
    "scissors",
    "tape",
    "glue",
    "pens",
    "pencils",
    "notebooks",
    "folders",
    "printer paper",
    "envelopes",
    "stamps",
    "batteries",
    "phone charger",
    "headphones",
    "USB flash drive",
    "DVDs",
    "playing cards",
    "board games",
    "picture frames",
    "candles",
    "vase",
    "plant pot",
    "paintbrushes",
    "canvas",
    "sewing kit",
    "craft paper",
    "glitter",
    "ribbon",
    "scrapbook",
    "coloring book",
    "crayons",
    "markers",
    "paints"
]

