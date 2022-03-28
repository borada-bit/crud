from flask import Flask
import os

app = Flask(__name__)

counter = 0

@app.route('/')
def hello():
    global counter
    counter = counter + 1
    print('incrementing counter')
    return (f'Hi! You saw me {counter} times!')

if __name__=='__main__':
    app.run(host="0.0.0.0", debug = True, port=80)
	
