from app import create_app


flask_app = create_app()



if __name__ == "__main__":

    # aplikace bude naslouchat na vsech sitovych rozhrani (pro kontejnery)
    flask_app.run(host='0.0.0.0', port=5000, debug=True) # port je pro testovani


