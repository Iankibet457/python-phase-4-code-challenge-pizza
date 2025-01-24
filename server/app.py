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

class Restaurants(Resource):
    def get(self, id=None):
        if id is None:
            restaurants = Restaurant.query.all()
            response = [
                {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "address": restaurant.address
                }
                for restaurant in restaurants
            ]
            return make_response(response, 200)
        
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return make_response(
                {"error": "Restaurant not found"},
                404
            )

        response = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza_id": rp.pizza_id,
                    "restaurant_id": rp.restaurant_id,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    }
                }
                for rp in restaurant.restaurant_pizzas
            ]
        }
        return make_response(response, 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return make_response(
                {"error": "Restaurant not found"},
                404
            )

        db.session.delete(restaurant)
        db.session.commit()
        
        return "", 204

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        response = [
            {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            for pizza in pizzas
        ]
        return make_response(response, 200)

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            restaurant = Restaurant.query.filter_by(id=data.get('restaurant_id')).first()
            pizza = Pizza.query.filter_by(id=data.get('pizza_id')).first()
            
            if not restaurant or not pizza:
                return make_response(
                    {"errors": ["Restaurant/Pizza not found"]},
                    404
                )
            
            restaurant_pizza = RestaurantPizza(
                price=data.get('price'),
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id')
            )
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            
            response = {
                "id": restaurant_pizza.id,
                "price": restaurant_pizza.price,
                "pizza_id": restaurant_pizza.pizza_id,
                "restaurant_id": restaurant_pizza.restaurant_id,
                "pizza": {
                    "id": pizza.id,
                    "name": pizza.name,
                    "ingredients": pizza.ingredients
                },
                "restaurant": {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "address": restaurant.address
                }
            }
            
            return make_response(response, 201)
            
        except ValueError:  
            return make_response(
                {"errors": ["validation errors"]},
                400
            )

api.add_resource(Restaurants, '/restaurants', '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
