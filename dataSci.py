from flask import Flask, flash, redirect, jsonify, render_template,\
     request, url_for , session , escape
import postProcessing

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('force.html')

@app.route('/visualize', methods=['GET'])
def visualize():
    input_year = request.args.get('year', 0, type=int)
    duration = request.args.get('duration', 0, type=int)
    clusters = request.args.get('clusters', 0, type=int)
    pp = postProcessing.PostProcessing()
    path = pp.main(input_year, duration,clusters)
    return jsonify(result=path)

@app.route('/add_numbers', methods=['GET'])
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
    #pp = postProcessing.PostProcessing()
    #return jsonify(pp.main(a, b))

if __name__ == '__main__':
    app.run(debug=True)
