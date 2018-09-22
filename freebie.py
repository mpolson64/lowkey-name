import numpy as np
import sys
import time
import random
import socket
import json

team_name = 'MANDMANDM'

test_mode = True
test_exchange_index = 0

prod_exchange_hostname = 'production'

port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name})
    hello_res = read_from_exchange(exchange)

    print(hello_res)

    while 1:
        write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": "BOND", "dir": "BUY", "price": 999, "size": 100})
        write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": "BOND", "dir": "SELL", "price": 1001,"size": 100})
        time.sleep(1)


if __name__ == "__main__":
    main()
