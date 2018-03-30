# -*- coding: utf-8 -*-
from flask import Flask, g
from proxypool.db import RedisClient

app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis_client'):
        g.redis_client = RedisClient()
    return g.redis_client


@app.route('/')
def index():
    return '<h1>Welcome to Proxy Pool System</h1>'


@app.route('/proxy/')
def proxy():
    conn = get_conn()
    return conn.pop()


if __name__ == '__main__':
    app.run()
