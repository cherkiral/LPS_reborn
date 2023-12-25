from io import BytesIO
from typing import List, Dict, Any
import openpyxl
import pandas as pd

from fastapi import APIRouter, HTTPException, Body
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from ..db import SessionLocal
from ..models.model import WCM
from ..services.services import apply_filters, apply_transformers

router = APIRouter()

# @router.get("/testing")
# def testing():
#     try:
#         query = "describe preprod"
#         data = fetch_data(query)
#         return {"data": data}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/get_data")
# def fetch_columns(selected_columns: List[str] = Body(...)):
#     try:
#         query = f"SELECT {', '.join(selected_columns)} FROM preprod limit 1000000"
#         data = fetch_data(query)
#         return {"data": data, "names": selected_columns}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter_data")
async def fetch_filtered_data(selected_columns: List[str] = Body(...),
                              filters: Dict[str, Dict[str, str]] = Body(...),
                              transformers: Dict[str, Any] = Body(...)
                              ):
    try:
        session = SessionLocal()

        # Start with a query for selected columns
        query = session.query(*[getattr(WCM, col) for col in selected_columns if hasattr(WCM, col)])

        # Apply filters
        query = apply_filters(query, WCM, filters)

        # Apply transformers
        query = apply_transformers(query, WCM, transformers)

        # Fetch data with applied filters and transformers
        data = query.all()

        # Convert data to a suitable format for response
        result = [{col: getattr(row, col) for col in selected_columns} for row in data]

        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()




@router.post("/create_report")
async def create_report(data: Dict = Body(...)):
    try:
        selected_columns = data["names"]
        rows = data["data"]

        # Convert data to pandas DataFrame
        df = pd.DataFrame(rows, columns=selected_columns)

        # Create a BytesIO object to save Excel file
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        excel_file.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="report.xlsx"'
        }

        return StreamingResponse(excel_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))