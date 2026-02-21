from flask import Flask
from DB.database import Database

app = Flask(__name__)
db = Database(app, wipeDB= True, backend='sqlite')

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
