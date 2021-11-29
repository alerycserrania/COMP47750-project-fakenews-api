import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, MetaData, Float
from sqlalchemy.sql.sqltypes import Text

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = os.environ["FASTAPI_DATABASE_URL"]

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, # connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables

meta = MetaData()

class_priors = Table(
   'class_priors', meta, 
   Column('idx', String(64)), 
   Column('cl', String(1)), 
   Column('p_real', Float), 
   Column('p_fake', Float), 
)

feature_probas = Table(
   'feature_probas', meta, 
   Column('idx', String(64)), 
   Column('word', String(255)), 
   Column('p_real', Float), 
   Column('p_fake', Float), 
)

stats = Table(
   'stats', meta, 
   Column('idx', String(255)), 
   Column('stats', Text),
)

meta.create_all(engine)