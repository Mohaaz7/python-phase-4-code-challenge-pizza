#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return [r.to_dict(rules=("-restaurant_pizzas",)) for r in restaurants], 200


# GET /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        return restaurant.to_dict(rules=("restaurant_pizzas",)), 200
    else:
        return {"error": "Restaurant not found"}, 404


# DELETE /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return {"error": "Restaurant not found"}, 404
    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return [p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas], 200


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        rp = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(rp)
        db.session.commit()
        response = rp.to_dict()
        response["pizza"] = rp.pizza.to_dict(rules=("-restaurant_pizzas",))
        response["restaurant"] = rp.restaurant.to_dict(rules=("-restaurant_pizzas",))
        return response, 201
    except Exception as e:
        return {"errors": ["validation errors"]}, 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
