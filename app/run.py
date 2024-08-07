
from __init__ import init_app

# předat celou aplikaci jakou proměnou do app
app = init_app()


# specifikace pro proměné v ENV docker-compose
# aplikace bude naslouchat na vsech sitovych rozhrani (pro kontejnery)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
