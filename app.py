from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))


@app.route('/cities', methods=['GET'])
def get_cities():
    cities = City.query.all()
    return jsonify([
        {
            "id": city.id,
            "name": city.name,
            "description": city.description
        } for city in cities
    ])


@app.route('/cities', methods=['POST'])
def add_city():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({"error": "Необходимо имя"}), 400

    city = City(name=name, description=description)
    db.session.add(city)
    db.session.commit()
    return jsonify({"message": "Город добавлен", "id": city.id}), 201


@app.route('/cities/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    city = City.query.get_or_404(city_id)
    db.session.delete(city)
    db.session.commit()
    return jsonify({"message": "Город удалён"})


@app.route('/weather/<city_name>', methods=['GET'])
def get_weather(city_name):
    api_key = '3860a9cd4056d6404081b3acfffed1ae'
    print(api_key)
    if not api_key:
        return jsonify({"error": "Не установлен API-ключ"}), 500

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=ru'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Город не найден"}), 404

    data = response.json()
    weather = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }
    return jsonify(weather)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
