from flask import Flask, flash, redirect, render_template,\
     request, url_for , session , escape
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('force.html')




if __name__ == '__main__':
    app.run()
