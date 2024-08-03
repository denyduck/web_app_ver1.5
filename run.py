from app import init_app


app = init_app()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    # specifikac pro proměné v ENV docker-compose
    # aplikace bude naslouchat na vsech sitovych rozhrani (pro kontejnery)
    app.run(host='0.0.0.0', port=5000, debug=True)
