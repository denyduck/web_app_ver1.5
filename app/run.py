
from app import create_app

# předat celou aplikaci jakou proměnou do app
flask_app = create_app()


# specifikace pro proměné v ENV docker-compose
# aplikace bude naslouchat na vsech sitovych rozhrani (pro kontejnery)
if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
