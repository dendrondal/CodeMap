from flask import Flask, render_template
from importfinder import ImportGraph
from pathlib import Path

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/hive')
def hive_plot():
    data = ImportGraph(directory=Path('/home/dal/PycharmProjects/pyjanitor_fork')).output_graph()
    return render_template('hive.html', graph_data=data)

if __name__ == '__main__':
    app.run()
