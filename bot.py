import os, sys, pika, requests, csv

def callback(ch, method, properties, body):
    data = body.decode("utf-8") 
    stock_code=data.split("|")[0]
    room = data.split("|")[1]
    try:
        with requests.Session() as s:
            download = s.get('https://stooq.com/q/l/?s={}&f=sd2t2ohlcv&h&e=csv'.format(stock_code))
            decoded = download.content.decode('utf-8')
            rows = [x for x in csv.reader(decoded.splitlines(), delimiter=',')]
            stock = rows[1][0]
            quote = rows[1][3]
            if quote == 'N/D':
                requests.post('http://45.56.96.56:5000/message', json={"message":"Unable to find stock!","room": room,"username":"StockBot","secret":"jobsitystockbotkey"})
            else:
                requests.post('http://45.56.96.56:5000/message', json={"message":"{} quote is ${}".format(stock_code.upper(),quote),"room": room,"username":"StockBot","secret":"jobsitystockbotkey"})
    except:
        try:
            requests.post('http://45.56.96.56:5000/message', json={"message":"Error while fetching stock prices","room": room,"username":"StockBot","secret":"jobsitystockbotkey"})
        except:
            pass

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='stock-query')
channel.basic_consume(queue='stock-query', on_message_callback=callback, auto_ack=True)
channel.start_consuming()