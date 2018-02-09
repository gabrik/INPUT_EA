#!/usr/bin/python3
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from Database import Base

class Users(Base):
    __tablename__ = 'Users'
    idUser = Column(Integer, primary_key=True)
    username = Column(String(20))

    def __repr__(self):
        return "<User(name='%s', fullname='%d'')>" % (
                             self.username, self.idUser)