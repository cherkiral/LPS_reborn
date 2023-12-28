from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = ""

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from clickhouse_driver import Client
from fastapi import HTTPException

# def get_db_client():
#     try:
#         client = Client(
#             host='analytics.weborama.io',
#             port=9440,
#             user='kchernyak',
#             password='',
#             database='wcm',
#             secure=True,
#             verify=False
#         )
#         return client
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
# # Example function to fetch data
# def fetch_data(query: str):
#     client = get_db_client()
#     return client.execute(query)
