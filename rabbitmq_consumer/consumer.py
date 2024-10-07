import os
import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rabbit_models import Files, Base, FileMetadata, FileChanges, ChangeType

from extract_message_from_json import extract_message_from_json
#==========================================================================
# Připojení k databazi
#==========================================================================
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root_password@db/my_database')
engine = create_engine(DATABASE_URL)        # Vytvoření připojení k databázi
Session = sessionmaker(bind=engine)         # Session umožňí provádět operace s databází, jako je ukládání, aktualizace nebo mazání da
Base.metadata.create_all(engine)




#==========================================================================
# Funkce pro únik znaků a vyčištění obsahu
#==========================================================================




#==========================================================================
# Funkce pro konzumaci zpráv z RabbitMQ
#==========================================================================
def consume_messages_outcoming():
    connection = None        # inicializace na None, zajistuje ze promena existuje ikdyz pripojeni selze

    try: # ostereni vyvovlani vyjimky, preskoc na except

        '''prihlasovaci udeje'''
        credentials = pika.PlainCredentials(             # prihlasovaci udaje
            os.getenv('RABBITMQ_USER', 'user'),          # nacti z compose/.env, pokud nic tak user
            os.getenv('RABBITMQ_PASSWORD', 'password'))  # stejne

        '''pripojeni'''
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),    # prihlasovaci udaje, pokud nejsou default: rabbitmq
            port=int(os.getenv('RABBITMQ_PORT', '5672')),   # port jinak default 5672
            credentials=credentials))

        '''vytvor kanal'''
        channel = connection.channel()      # vytvori kanal pro komunikaci

        '''vytvor frontu do kanalu a nastav ji'''
        channel.queue_declare(
            queue='file_events',    # fronta s nazvem file_events
            durable=True)           # True = fronta přezije restart kontejneru

        '''Registrace callback funkce pro zpracování zpráv'''
        channel.basic_consume(                         # paramater basic_consume urcuje nazev fronty, ktera je konzumovana
            queue='file_events',                       # nazev fronty
            on_message_callback=callback_outcoming,    # funkce ktera je volana pokazde kdyz je k dispozici nova zprava
            auto_ack=True)                             # RABBITMQ povazuje zpravu za potvrzenou po zavolane callback_outcoming, zprava je pote odstranena z fronty

        print('Čekám na příchozí zprávy od psa. Pro ukončení stitkni CTRL+C')     # Informace pro uzivatele

        channel.start_consuming()   # vola fci->akce pro zpravu

    except Exception as e:
        print(f'Chyba při zpracování zprávy: {e}')     # Debug pro info

    finally:
        # Zajištění, že spojení bude vždy uzavřeno
        if connection and connection.is_open:
            connection.close()






#==========================================================================
# Callback pro zpracování příchozí zprávy
#==========================================================================


def callback_outcoming(ch, method, properties, body):
    # Získání ID a metody zprávy z hlavičky
    mass_head = properties.headers.get('message_id')
    method_type = properties.headers.get('method')
    print(f"Headers - message_id: {mass_head}, method: {method_type}")


    # Dekódování těla zprávy
    message_content = body.decode()
    print(f"Message body decoded: {message_content}")

    file_id,filename, directory, hash, change_type, metadata, content = extract_message_from_json(message_content)



    #content_escape = ex_path(content)

    print(f'mesage: {file_id}')

    print(f"Extracted message - ID: {file_id}, Filename: {filename}, Directory: {directory}, Hash: {hash}, Type: {change_type}, Metadata: {metadata}, content: {content}")


    # Debug výstup pro kontrolu
    print("Zpráva přijata:")
    print(f"  ID: {mass_head}")
    print(f"  Metoda: {method_type}")
    print(f"  Obsah: {message_content}")
    print(f"  Nazev: {filename}")


    '''Zpracování do databaze podle hlavicky zpravy'''
    session = Session()  # Otevři novou session

    try:
        if method_type == 'new':

            # Vytvoření nové zprávy a uložení do databáze
            message = Files(filename=filename,
                            directory=directory,
                            hash=hash,
                            metadata=metadata,
                            message_id=mass_head,
                            kontent=content)

            session.add(message)
            session.commit()  # Potvrzení změn

            id_db_row = message.id


            print(f"Zprava byla uspesne ulozena s metodou 'new' a prirazenym ID z databeze {id_db_row} .")

            if metadata: # dalsi infa z metadata do dalsi tabulky
                file_metadata = FileMetadata(
                    file_id = id_db_row,
                    title = metadata.get('title'),
                    keyword = metadata.get('keyword'),
                    description = metadata.get('description'),
                    content_text = metadata.get('content_text')
                )


                session.add(file_metadata)
                session.commit()






        elif method_type == 'del':
            print(f'Debug pro del{filename}')
            # Smazání zprávy podle obsahu zprávy
            existing_message = session.query(Files).filter(Files.filename==filename, Files.directory==directory).first()
            print(f'tady je metoda pro odstraneni: {existing_message}')     # debug zprava


            if existing_message:
                # Před smazáním záznamu, vytvor záznam o změně
                change_record = FileChanges(
                    file_id = existing_message.id,
                    change_type = ChangeType.DELETED,
                    old_hash = existing_message.hash,
                    new_hash = None,
                    old_size = existing_message.size,
                    new_size = None
                )

                session.add(change_record)  # Smazání zprávy
                session.commit()  # Potvrzení změn

                session.delete(existing_message)
                session.commit()

                print(f"Zprava: s obsahem '{existing_message}' byla uspesne smazana.")
            else:
                print(f"Zadna zprava s obsahem '{existing_message}' nebyla nalezena.")


        elif method_type == 'edit':
            # Při detekci změn, aktualizace obsahu existující zprávy
            message_to_edit = session.query(Files).filter_by(message_content=message_content).first()
            if message_to_edit:
                change_record = FileChanges(
                    file_id = message_to_edit.id,
                    filename = filename, # upraveno smazat #
                    change_type = ChangeType.MODIFIED,
                    old_hash = message_to_edit.hash,
                    new_hash = hash,
                    old_size = message_to_edit.size,
                    new_size = len(message_content),

                )
                session.add(change_record)
                session.commit()  # Potvrzení změn

                # aktuaizace zaznamu
                message_to_edit.hash = hash
                message_to_edit.size = len(message_content)
                session.commit()    # potvrzení změn

                print(f"Zpráva byla úspěšně aktualizována s novým obsahem: '{message_content}'.")
            else:
                print(f"Žádná zpráva s obsahem '{message_content}' k editaci nebyla nalezena.")

    except Exception as e:
        session.rollback()  # V případě chyby vrátíme změny zpět
        print(f"chyba proces {e}")

    finally:
        session.close()  # Zavření session



if __name__ == '__main__':
    consume_messages_outcoming()