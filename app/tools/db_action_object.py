from pdfs.models import db


# prida objekt do databaze a osetri chybu rollbackem
def add_object(obj):
    try:
        db.session.add(obj)
        db.session.commit()
        print("Objekt byl úspěšně přidán do databáze.")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Chyba při přidávání objektu do databáze: {e}")
        return False



# odstrani objekt z databaze a osetri chybu rollbackem
def delete_object(obj):
    try:
        db.session.delete(obj)
        db.session.commit()
        print('Objekt byl úspěšně smazán z databáze')
        return True
    except:
        db.session.rollback()
        return False

