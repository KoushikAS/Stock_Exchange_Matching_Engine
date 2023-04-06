from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')

m = MetaData()
m.reflect(engine)
m.drop_all(engine)

Session = sessionmaker(bind=engine)

Base = declarative_base()