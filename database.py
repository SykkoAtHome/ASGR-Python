from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql://bwnntcgd:mdlF2WaBFTn2AGWWmGcW0cX5l0rCKL7i@lucky.db.elephantsql.com/bwnntcgd'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()