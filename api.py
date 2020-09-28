from flask import Flask, jsonify
from flask_socketio import SocketIO, join_room
import csv
import requests
import os
import sys
import pika


app = Flask(__name__)



@app.route('/stock/<string:code>')
def stock(code):
    try:
        with requests.Session() as s:
            download = s.get('https://stooq.com/q/l/?s={}&f=sd2t2ohlcv&h&e=csv'.format(code))
            decoded = download.content.decode('utf-8')
            rows = [x for x in csv.reader(decoded.splitlines(), delimiter=',')]
            stock = rows[1][0]
            quote = rows[1][3]
            if quote == 'N/D':
                return jsonify({"error":"Stock not found"}),404  
            return jsonify({"data":"{} quote is ${}".format(stock.upper(),quote)})
    except:
       return jsonify({"error":"Unable to retrieve data"}),401

def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='stock')
channel.basic_consume(queue='stock', on_message_callback=callback, auto_ack=True)
channel.start_consuming()


if __name__ == '__main__':
    app.run(debug=True)
