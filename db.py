import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, MetaData, Float

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = os.environ["FASTAPI_DATABASE_URL"]

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables

meta = MetaData()

class_priors = Table(
   'class_priors', meta, 
   Column('idx', String, primary_key = True), 
   Column('cl', String, primary_key = True), 
   Column('p_real', Float), 
   Column('p_fake', Float), 
)

feature_probas = Table(
   'feature_probas', meta, 
   Column('idx', String, primary_key = True), 
   Column('word', String, primary_key = True), 
   Column('p_real', Float), 
   Column('p_fake', Float), 
)

stats = Table(
   'stats', meta, 
   Column('idx', String), 
   Column('stats', String),
)

meta.create_all(engine)