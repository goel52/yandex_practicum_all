from typing import Dict

from flask import Flask, request

from redis_service import RedisClientFactory, RestaurantLoader, UserLoader, RedisTestLoader

app = Flask(__name__)


@app.get('/health')
def hello_world():
    return 'healthy'


@app.post('/load_restaurants')
def load_restaurants():
    req: Dict = request.get_json()  # type: ignore
    (redis, err) = RedisClientFactory.from_json(req)
    if redis is None:
        return {
            "status": "Error",
            "error": err
        }

    rl = RestaurantLoader(redis)
    resp = rl.load_restaurants()
    return {
        "status": "OK",
        "load_restaurants_response": resp
    }


@app.post('/get_restaurant')
def get_restaurant():
    req: Dict = request.get_json()  # type: ignore
    (redis, err) = RedisClientFactory.from_json(req)
    if redis is None:
        return {
            "status": "Error",
            "error": err
        }

    rl = RestaurantLoader(redis)
    resp = rl.get_restaurant(req['restaurant_id'])
    return {
        "status": "OK",
        "response": resp
    }


@app.post('/load_users')
def load_users():
    req: Dict = request.get_json()  # type: ignore
    (redis, err) = RedisClientFactory.from_json(req)
    if redis is None:
        return {
            "status": "Error",
            "error": err
        }

    rl = UserLoader(redis)
    resp = rl.load_users()
    return {
        "status": "OK",
        "load_users_response": resp
    }


@app.post('/get_user')
def get_user():
    req: Dict = request.get_json()  # type: ignore
    (redis, err) = RedisClientFactory.from_json(req)
    if redis is None:
        return {
            "status": "Error",
            "error": err
        }

    ul = UserLoader(redis)
    resp = ul.get_user(req['user_id'])
    return {
        "status": "OK",
        "response": resp
    }


@app.post('/test_redis')
def test_redis():
    req: Dict = request.get_json()  # type: ignore
    (redis, err) = RedisClientFactory.from_json(req)
    if redis is None:
        return {
            "status": "Error",
            "error": err
        }

    rt = RedisTestLoader(redis)
    resp = rt.load_test_string()
    return {
        "status": "OK",
        "test_redis_response": resp
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
