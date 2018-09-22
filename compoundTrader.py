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

    ctrader(exchange, 5, 10, 0.125)

def ctrader(exchange, rough, smooth, cooldown):
    trading = {'AAPL', 'GOOG', 'MSFT'}

    t0, t1 = 0, 0
    time_since_last_order = cooldown

    hist = {}

    for symbol in trading:
        hist[symbol] = np.zeros(smooth)

    while 1:
        time_since_last_order += (t1 - t0)  # * 100
        t0 = time.time()
        message = read_from_exchange(exchange)

        print(message['type'], message)
        print(hist)
        print(time_since_last_order)
        print("==============================================")

        if(message['type'] == 'trade' and message['symbol'] in trading):
            hist[message['symbol']] = np.append(hist[message['symbol']][1:], np.array(message['price'][0][0]))

        for symbol in trading:
            if 0 not in hist[symbol]:
                rough_average = hist[symbol][-rough:].mean()
                smooth_average = hist[symbol].mean()

                if(rough_average < smooth_average and time_since_last_order > cooldown):
                    trade_id = random.randint(0, 2 ** 31)

                    write_to_exchange(exchange, {"type": "add", "order_id": trade_id, "symbol": symbol, "dir": "BUY", "price": rough_average, "size": 1})
                    time_since_last_order = 0

                    print("tryna buy " + symbol + " @ " + str(hist[symbol][-1]))
                elif(rough_average > smooth_average and time_since_last_order > cooldown):
                    trade_id = random.randint(0, 2 ** 31)

                    write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": symbol, "dir": "SELL", "price": rough_average, "size": 1})
                    time_since_last_order = 0

                    print("tryna sell " + symbol + " @ " + str(hist[symbol][-1]))

        t1 = time.time()


def trader(exchange, symbol, rough, smooth, cooldown):
    t0, t1 = 0, 0
    hist = np.zeros(smooth)
    time_since_last_order = cooldown

    while 1:
        time_since_last_order += (t1 - t0)  # * 100
        t0 = time.time()
        message = read_from_exchange(exchange)

        print(message['type'], message)
        print(hist)
        print(time_since_last_order)
        print("==============================================")

        if(message['type'] == 'trade' and message['symbol'] == symbol):
            hist = np.append(hist[1:], np.array(message['price'][0][0]))

        if 0 not in hist:
            rough_average = hist[-rough:].mean()
            smooth_average = hist.mean()

            if(rough_average < smooth_average and time_since_last_order > cooldown):
                trade_id = random.randint(0, 2 ** 31)

                write_to_exchange(exchange, {"type": "add", "order_id": trade_id, "symbol": symbol, "dir": "BUY", "price": int(hist[-1]), "size": 1})
                time_since_last_order = 0

                print("tryna buy @ " + str(hist[-1]))
            elif(rough_average > smooth_average and time_since_last_order > cooldown):
                trade_id = random.randint(0, 2 ** 31)

                write_to_exchange(exchange, {"type": "add", "order_id": random.randint(0, 2 ** 31), "symbol": symbol, "dir": "SELL", "price": int(hist[-1]), "size": 1})
                time_since_last_order = 0

                print("tryna sell @ " + str(hist[-1]))

        t1 = time.time()


if __name__ == "__main__":
    main()
