from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean  # noqa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker  # noqa


BaseModel = declarative_base()

engine = create_engine('sqlite:///finances_v2.db', echo=False)

_Session = sessionmaker(bind=engine)
session = _Session()
