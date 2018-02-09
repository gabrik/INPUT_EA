#!/usr/bin/python3
from sqlalchemy import Column, Integer, String ,DateTime
from sqlalchemy.ext.declarative import declarative_base
from Database import Base


class ContentProviders(Base):
    __tablename__ = 'ContentProviders'
    idContentProvider = Column(Integer, primary_key=True)
    name = Column(String(20),unique=True)
    image = Column(String(100))

    def __repr__(self):
        return "<ContentProvider(idContent='%d', name='%s')>" % (
                             self.idContentProvider, self.name)