from io import BytesIO
from typing import List, Dict
import openpyxl
import pandas as pd
from pprint import pprint

from fastapi import APIRouter, HTTPException, Body
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
import time

from backend.app.db import SessionLocal
from backend.app.models.model import WCM
# from ..services.services import apply_filters

session = SessionLocal()
start = time.time()
# Fetch the first 10 rows

data = session.query(WCM).where(WCM.account_id == '261965').all()
end = time.time()

# Convert each row to a dictionary
# result = []
# for row in data:
#     row_dict = {column.name: getattr(row, column.name) for column in row.__table__.columns}
#     result.append(row_dict)
print(end - start)
