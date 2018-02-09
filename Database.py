#!/usr/bin/python3
from datetime import datetime,time,timedelta
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.exc import InternalError
Base = declarative_base()
from Model import Users,ContentProviders,Contents,UsersContentProviders

class Database(object):
    def __init__(self,nomeDb,ip,dbport,username,password):
        self.engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(username,password,ip,dbport,nomeDb),echo=False)
        self.Session = sessionmaker(bind=self.engine)
        session = self.Session()
        try:
            if(session.query(Users.Users.idUser).first() is None):
                self.PopolateDb()
        except ProgrammingError as ex:
            if "1146" in ex.args[0]:
                self.CreateTables()
        except InternalError as ex:
            print("prova: {}".format((ex.args[0])))
            if "1049" in ex.args[0]:
                print("Database non e' presente")
        session.close()

    def CreateTables(self):
        Base.metadata.create_all(self.engine)
        print("Database Created")
        self.PopolateDb()

    def PopolateDb(self):
        session=self.Session()
        starttime2=datetime.now()+timedelta(hours=2)
        path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"Image")
        # print(path)
        # print(os.path.join(path,"InputProvider1"))
        # print(len(path))
        # print(len(os.path.join(path,"InputProvider1")))
        firstUser = Users.Users(idUser = 1,username = "InputUser1")
        secondUser = Users.Users(idUser = 2,username= "InputUser2")
        firstContentProvider = ContentProviders.ContentProviders(idContentProvider = 1 ,name = "InputProvider1",image=os.path.join(path,"InputProvider1.jpg"))
        firstContent = Contents.Contents(name = "InputContent1" , description="Cartone animato per bambini",startingTime = datetime.now(), length=time(2,00,00),idContentProvider=firstContentProvider.idContentProvider,image=os.path.join(path,"InputContent1.jpg"))
        secondContentProvider = ContentProviders.ContentProviders(idContentProvider = 2,name = "InputProvider2",image=os.path.join(path,"InputProvider2.jpg"))
        secondContent = Contents.Contents(name = "InputContent2" , description="Sport ",startingTime = datetime.now(), length=time(2,00,00),idContentProvider=secondContentProvider.idContentProvider,image=os.path.join(path,"InputContent2.jpg"))
        thirdContent = Contents.Contents(name = "InputContent3" , description="Videogiochi",startingTime = starttime2, length=time(2,00,00),idContentProvider=firstContentProvider.idContentProvider,image=os.path.join(path,"InputContent3.jpg"))
        firstUsersContentProviders = UsersContentProviders.UsersContentProviders(idContentProvider=firstContentProvider.idContentProvider,idUser=firstUser.idUser)
        secondUserContentProvider = UsersContentProviders.UsersContentProviders(idContentProvider=secondContentProvider.idContentProvider,idUser=secondUser.idUser)
        session.add(firstUser)
        session.add(secondUser)
        session.add(firstContentProvider)
        session.add(secondContentProvider)
        session.commit()
        session.add(firstContent)
        session.add(secondContent)
        session.add(thirdContent)
        session.commit()
        session.add(firstUsersContentProviders)
        session.add(secondUserContentProvider)
        session.commit()
        print("Database Popolato")
        session.close()


    def getContents(self,name):
        session = self.Session()
        contentList=[]
        idContentProviders=[]
        idUser=session.query(Users.Users.idUser).filter(Users.Users.username==name).first()
        id=idUser[0]
        for element in session.query(ContentProviders.ContentProviders.idContentProvider).join(UsersContentProviders.UsersContentProviders).filter(UsersContentProviders.UsersContentProviders.idUser==id).all():
            idContentProviders.append(element[0])
        print ("{}".format(idContentProviders))
        for content in session.query(Contents.Contents).filter(Contents.Contents.idContentProvider.in_(idContentProviders)).all():
            tmp=dict(content.__dict__)
            tmp.pop('_sa_instance_state', None)
            contentList.append(tmp)
        session.close()
        return contentList

    #{'length': datetime.time(2, 0), 'name': 'InputContent1', 'description': 'Cartone animato per bambini', 'image': '/home/ale
    #ssandro/EdgeAcquirer ffserver/Image/InputContent1.jpg', 'idContentProvider': 1, 'idContent': 1, '_sa_instance_state': <sql
    #alchemy.orm.state.InstanceState object at 0x7fc5613fb470>, 'startingTime': datetime.datetime(2017, 6, 21, 16, 40, 56)
    def getInfoRec(self,idContent):
        session = self.Session()
        q=session.query(Contents.Contents,ContentProviders.ContentProviders.name).join(ContentProviders.ContentProviders).filter(Contents.Contents.idContent == int(idContent)).first()
        #q=session.query(Contents.Contents).filter(Contents.Contents.idContent == int(idContent)).first()
        #q=session.query(ContentProviders.ContentProviders,Contents.Contents).filter(Contents.Contents.idContent == int(idContent)).filter(Contents.Contents.idContentProvider==ContentProviders.ContentProviders.idContentProvider).first()        
        #q=session.query(Contents.Contents).filter(Contents.Contents.idContent == int(idContent)).filter(Contents.Contents.idContentProvider==ContentProviders.ContentProviders.idContentProvider).first()        
        #result = db.engine.execute("select Contents.name,Contents.length,Contents.startingTime,ContentProviders.name FROM contents,ContentProvider WHERE Contents.idContentProvider==ContentProviders.idContentProvider and Content.idContent== 1")
        #tmp=q.__dict__
        #for elem in q:
        #    print ("{}".format(elem.__dict__))
        print ("{}".format(q[0].__dict__))
        tmp=dict(q[0].__dict__)
        tmp.pop('_sa_instance_state', None)
        tmp.pop('image',None)
        tmp.pop('description',None)
        tmp.pop('idContentProvider',None)
        tmp.pop('idContent',None)
        tmp['nameProvider']=q[1]
        tmp['nameContent']=tmp.pop('name',None)
        return tmp

    def getContentProviders(self,name):
        session = self.Session()
        providerList=[]
        idUser=session.query(Users.Users.idUser).filter(Users.Users.username==name).first()
        id=idUser[0]
        for content in session.query(ContentProviders.ContentProviders).join(UsersContentProviders.UsersContentProviders).filter(UsersContentProviders.UsersContentProviders.idUser==id).all():
            tmp=dict(content.__dict__)
            tmp.pop('_sa_instance_state', None)
            providerList.append(tmp)
        return providerList
    
    def getProvidersKeys(self):
        session = self.Session()
        key_list=[]
        for content in session.query(ContentProviders.ContentProviders).all():
            key_list.append(content.__dict__['name'])
        session.close()
        return key_list

    def getContentProviderName(self,idContent):
        session=self.Session()
        name=session.query(ContentProviders.ContentProviders).filter(idContentProvider==idContent).first()
        print(name)
        session.close()
        return name