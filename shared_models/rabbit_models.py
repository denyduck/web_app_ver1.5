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
                        Enum,
                        Index)

from shared_models import Base
from sqlalchemy.orm import relationship
import enum
import logging

from sqlalchemy.dialects.mysql import LONGTEXT

'''
func.now()                  # Používá funkci now() databázového serveru k získání aktuálního data a času.
onupdate=func.now())        # změn hodnotu sloupce pokaždé, když je záznam aktualizován a to časem
uselist=False               # říká SQLAlchemy, že se jedná o One-to-One vztah, nikoli o seznam (což je běžné pro One-to-Many). 
                                Bez této volby by relace očekávala, že pro každý soubor může existovat více záznamů v FileMetadata, 
                                což by vedlo k One-to-Many vztahu.
'''

# Enum pro typ změny
class ChangeType(enum.Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "rename"

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    directory = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    change_type = Column(Enum(ChangeType), nullable=True)
    last_modified_at = Column(TIMESTAMP, onupdate=func.now())
    is_active = Column(Boolean, default=True) # activ je True
    message_id = Column(String(255), nullable=False)
    hash_item = Column(String(64), nullable=True)
    size = Column(BigInteger, nullable=True)
    version = Column(Integer)
    validation_status = Column(String(255))
    kontent = Column(LONGTEXT)

    changes = relationship('FileChanges', back_populates='item')

    def __repr__(self):
        return f"<Items(id={self.id}, filename={self.filename}, is_active={self.is_active})>"


class FileChanges(Base):
    __tablename__ = 'file_changes'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    filename = Column(String(255), nullable=True)
    changed_at = Column(TIMESTAMP, server_default=func.now())
    change_type = Column(Enum(ChangeType), nullable=False)
    old_hash = Column(String(64))
    new_hash = Column(String(64))
    old_size = Column(BigInteger)
    new_size = Column(BigInteger)

    item = relationship('Items', back_populates='changes')
    file = relationship('Files', back_populates='changes')

    def __repr__(self):
        return f'<FileChanges(id={self.id}, filename={self.filename}, change={self.change_type})>'


class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    directory = Column(String(255), nullable=False)
    hash_item = Column(String(64))
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_modified_at = Column(TIMESTAMP, onupdate=func.now())
    size = Column(BigInteger)
    message_id = Column(String(255), nullable=False)
    kontent = Column(LONGTEXT)

    changes = relationship('FileChanges', back_populates='file')
    file_metadata = relationship('FileMetadata', back_populates='file', uselist=False)

    def __repr__(self):
        return f"<Files(id={self.id}, filename={self.filename}, hash={self.hash})>"


class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    title = Column(String(255))
    keyword = Column(Text)
    description = Column(Text)
    content_text = Column(LONGTEXT)

    file = relationship('Files', back_populates='file_metadata')

    def __repr__(self):
        return f"<FileMetadata(id={self.id}, file_id={self.file_id}, title={self.title})>"