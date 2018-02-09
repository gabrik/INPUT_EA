#!/usr/bin/python3
from sqlalchemy import Column, Integer, String ,DateTime,Time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from Database import Base

class UsersContentProviders(Base):
    __tablename__ = 'UsersContentProviders'
    idUserContent = Column(Integer,primary_key=True)
    idContentProvider = Column(Integer,ForeignKey("ContentProviders.idContentProvider"),nullable=False)
    idUser = Column(Integer, ForeignKey("Users.idUser"),nullable=False)

    def __repr__(self):
        return "<UsersContentProviders(idContentProvider='%d', IdUser='%s'>" % (
                             self.idContentProvider, self.idUser)