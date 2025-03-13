from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Mock Server for Fetcher Testing"

@app.route('/facebook/login')
def facebook_login():
    return render_template('facebook_login.html')

@app.route('/facebook/feed')
def facebook_feed():
    return render_template('facebook_feed.html')

@app.route('/infinite-scroll')
def infinite_scroll():
    return render_template('infinite_scroll.html')

if __name__ == "__main__":
    app.run(debug=True)
