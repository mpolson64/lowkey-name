import numpy as np
import sys
import socket
import json

team_name = 'MANDMANDM'

test_mode = True
test_exchange_index = 1

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

    high_bid = None
    low_ask = None

    while 1:

        res = read_from_exchange(exchange)
        if res['type'] == 'book':
            if res['symbol'] == 'AAPL':
                high_bid = res['buy'][0]
                low_ask = res['sell'][0]
        print("AAPL " + str(high_bid) + " @ " + str(low_ask))

if __name__ == "__main__":
    main()
