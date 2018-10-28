# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy import DateTime

from sqlalchemy.orm import sessionmaker  
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
Base = declarative_base()

# CREATE TABLE IF NOT EXISTS `dialog`(
   # `userid` VARCHAR(16),
   # `msg` VARCHAR(128) NOT NULL,
   # `time_stamp` VARCHAR(32) NOT NULL,
   # `showed` INT,
   # PRIMARY KEY (`time_stamp`)
# )ENGINE=InnoDB DEFAULT CHARSET=utf8;

# INSERT INTO visitor (userid,time_stamp,isCurrent)
# VALUES ('21050632', '2007-01-01 10:00:00', 1);


class Dialog(Base):
    # 表的名字:
    __tablename__ = 'dialog'

    # 表的结构:
    userid = Column(String(16), primary_key=True)
    msg = Column(String(128))
    time_stamp = Column(String(64), primary_key=True)
    showed = Column(Integer)


class Visitor(Base):

    __tablename__ = 'visitor'
    
    userid = Column(String(10), primary_key=True)
    time_stamp = Column(DateTime, primary_key=True)
    isCurrent = Column(Integer)
    
class ConnSQL():
    
    def __init__(self):
        

        # DB_CONNECT = 'mysql+mysqldb://stkqj:Gmcc_123@127.0.0.1:3306/stkqj?charset=utf8'
        DB_CONNECT = 'mysql+mysqldb://root:root@10.245.132.42:3306/aiterminal?charset=utf8'
        DB_CONNECT = 'mysql+mysqldb://root:root@192.168.28.97:3306/aiterminal?charset=utf8'
        DB_CONNECT = 'sqlite:///aiterminal.db'
        engine = create_engine(DB_CONNECT, echo=True, encoding='utf-8')
        # metadata = MetaData(engine)
        # metadata.create_all()

        DB_Session = sessionmaker(bind=engine)
        self.session = DB_Session()
        # Base.metadata.create_all(engine)


    def insert_data(self, dialog):

        # 添加到session:
        self.session.add(dialog)
        # 提交即保存到数据库:
        self.session.commit()

    def select_data(self):
        
        # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
        try:
            visitor = self.session.query(Visitor).filter(Visitor.isCurrent==1).all()
            userid = visitor[0].userid
        except: 
            userid = '21050222'
        # 打印类型和对象的name属性:
        # print('len of row', len(user))
        # for u in user:
        return userid
        
    
    def __del__(self):
        # 关闭session:
        self.session.close()
        
if __name__ == '__main__':
    
    conn_sql = ConnSQL()
    
    new_dialog = Dialog(userid='bot', 
                          msg=u'MySQL是Web世界中使用最广泛的数据库服务器', 
                          time_stamp='%s'%datetime.now(), 
                          showed=0)
    conn_sql.insert_data(new_dialog)
    userid = conn_sql.select_data()
    print(userid)
    
