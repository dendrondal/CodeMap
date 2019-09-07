from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/{package}'):
def hive_plot(package):
    
if __name__ == '__main__':
    app.run()
