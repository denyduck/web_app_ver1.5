from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    # specifikac pro proměné v ENV docker-compose
    # aplikace bude naslouchat na vsech sitovych rozhrani (pro kontejnery)
    app.run(host='0.0.0.0', port=5000)
