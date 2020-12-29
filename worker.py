import os, sys

from environs import Env

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import redis
from rq import Worker, Queue, Connection

env = Env()
env.read_env()

listen = ['default']

redis_url = env.str("REDISTOGO_URL", default="redis://localhost:6379")

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work(with_scheduler=True)
