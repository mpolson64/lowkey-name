import numpy as np
import sys
import time
import random
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

    trader(2, 5, exchange, 'AAPL')


def trader(rough, smooth, exchange, symbol):
    hist = np.zeros(smooth)

    write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": "BOND", "dir": "BUY", "price": 1000, "size": 1})
    while 1:
        message = read_from_exchange(exchange)

        print(message['type'], message)
        print(hist)
        print("==============================================")

        if(message['type'] == 'book' and message['symbol'] == symbol):
            hist = np.append(hist[1:], np.array(message['sell'][0][0]))

        if 0 not in hist:
            rough_average = hist[-rough:].mean()
            smooth_average = hist.mean()

            if(rough_average <= smooth_average):
                write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": symbol, "dir": "BUY", "price": int(hist[-1]), "size": 1})
                print("tryna buy @ " + str(hist[-1]))
            else:
                write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": symbol, "dir": "SELL", "price": int(hist[-1]), "size": 1})
                print("tryna sell @ " + str(hist[-1]))


        time.sleep(1)


if __name__ == "__main__":
    main()
