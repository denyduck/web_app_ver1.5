from sqlalchemy import (Text,
                        Column,
                        String,
                        Date,
                        Integer,
                        TIMESTAMP,
                        func,
                        BigInteger,
                        Boolean,
                        ForeignKey,
                        Enum)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

'''
func.now()                  # Používá funkci now() databázového serveru k získání aktuálního data a času.
onupdate=func.now())        # změn hodnotu sloupce pokaždé, když je záznam aktualizován a to časem

'''


# Vytvoření základní třídy, nejsem v kontextu palikace Flask
Base = declarative_base()

# Enum pro typ změny
class ChangeType(enum.Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"

#===================================================================================
# Tabulka `files` zobrazuje informace a aktualni soubory
#===================================================================================
class Files(Base):
    __tablename__ = 'files'  # Název tabulky

    id = Column(Integer, primary_key=True)                       # Primární klíč
    filename = Column(String(255), nullable=False)               # Název souboru
    directory = Column(String(255), nullable=False)              # Cesta k adresáři
    hash = Column(String(64))                                    # Hash souboru (např. SHA-256)
    created_at = Column(TIMESTAMP, server_default=func.now())    # Datum vytvoření, a to přímo v databázi
    last_modified_at = Column(TIMESTAMP, onupdate=func.now())    # Datum poslední změny
    size = Column(BigInteger)                                    # Velikost souboru v bajtech
    is_active = Column(Boolean, default=True)                    # Aktivní status
    message_id = Column(String(255), nullable=False)             # identifikace zpravy

    def __repr__(self):
        return f"<Files(id={self.id}, filename={self.filename}, message_id={self.message_id})>"



    changes = relationship('FileChanges', back_populates='file')
    file_metadata = relationship('FileMetadata', back_populates='file')
#===================================================================================
#Tabulka 'File_changes'
#===================================================================================
#Tabulka sledující změny jednotlivých souborů. Umožňuje archivovat historii změn pro účely logování.

# Tabulka `file_changes`
class FileChanges(Base):
    __tablename__ = 'file_changes'  # Název tabulky

    id = Column(Integer, primary_key=True)                              # Primární klíč
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)    # Opravený cizí klíč na Files
    filename = Column(String(255), nullable=False)  #DOPLNIT POTOM SMAZAT!!
    changed_at = Column(TIMESTAMP, server_default=func.now())    # Datum změny
    change_type = Column(Enum(ChangeType), nullable=False)       # Typ změny
    old_hash = Column(String(64))                                # Původní hash
    new_hash = Column(String(64))                                # Nový hash
    old_size = Column(BigInteger)                                # Původní velikost
    new_size = Column(BigInteger)                                # Nová velikost


    file = relationship('Files', back_populates='changes')       # Správná relace zpět k Files

# Tabulka `file_metadata`
class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id = Column(Integer, primary_key=True)                       # Primární klíč
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)  # Opravený cizí klíč na Files
    title = Column(String(255))                                  # Název
    keyword = Column(Text)                                       # Klíčová slova
    description = Column(Text)                                   # Popis
    content_text = Column(Text)                                  # Obsah textu


    file = relationship('Files', back_populates='file_metadata')      # Správná relace zpět k Files

