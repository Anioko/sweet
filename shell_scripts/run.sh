#!/usr/bin/env sh
nohup redis-server &
nohup python worker.py &
nohup python sockets.py &
flask run --host=0.0.0.0 --port=5500 --cert=adhoc
