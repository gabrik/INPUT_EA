#!/usr/bin/python3
from sqlalchemy import Column, Integer, String ,DateTime,Time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from Database import Base

class Contents(Base):
    __tablename__ = 'Contents'
    idContent = Column(Integer, primary_key=True)
    name = Column(String(30))
    description = Column(String(50))
    image = Column(String(100))
    startingTime = Column(DateTime)
    length = Column(Time)
    idContentProvider = Column(Integer, ForeignKey("ContentProviders.idContentProvider"), nullable=False)

    def __repr__(self):
        return "<Content(idContent='%d', name='%s', description='%s',startingtime='%s',length='%s',idContentProvider='%d')>" % (
                             self.idContent, self.name, self.description,self.startingTime,self.length,self.idContentProvider)