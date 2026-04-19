from flask import jsonify

app = Flask(__name__)

@app.route("/")
def hello_world():
    return jsonify(message="Hello, World!")

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(debug=True)