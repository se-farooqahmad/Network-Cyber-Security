from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from app.auth.auth import validate_session
from app.security.authorization import authorization_mgr
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATE_DIR
from app.db.database import get_db

import datetime

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Adjustments page
@router.get("/bill-adjustments", response_class=HTMLResponse)
async def get_bill_adjustment(request: Request, user: dict = Depends(validate_session)):

    authorization_mgr.check_access(request, user)
    return templates.TemplateResponse("adjustment/bill_adjustments.html", {"request": request})

# Code for handling adjustments goes here
@router.post("/bill-adjustments", response_class=HTMLResponse)
async def post_bill_adjustments(
    request: Request,
    bill_id: int = Form(...),
    officer_name: str = Form(...),
    officer_designation: str = Form(...),
    original_bill_amount: float = Form(...),
    adjustment_amount: float = Form(...),
    adjustment_reason: str = Form(...),
    user: dict = Depends(validate_session),
    connection = Depends(get_db)
):
    
    authorization_mgr.check_access(request, user)

    cursor = connection.cursor()

    # check if the bill exists
    bill_query = f"SELECT B.BILLID, B.TotalAmount_BeforeDueDate FROM BILL B WHERE B.BILLID = {bill_id}"
    cursor.execute(bill_query)
    bill_row = cursor.fetchone()
    if not bill_row:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "Invalid BillID provided."})

    # current date as the payment date
    adjustment_DATE = datetime.datetime.now()

    # generate an adjustment id
    adjustment_id = int(str(bill_id) + str(adjustment_DATE.year) + str(adjustment_DATE.month))

    result = cursor.callfunc("fun_adjust_Bill", int, [adjustment_id, bill_id, adjustment_DATE, officer_name, officer_designation, original_bill_amount, adjustment_amount, adjustment_reason])

    adjustment_details = {
        "bill_id": bill_id,
        "officer_name": officer_name,
        "officer_designation": officer_designation,
        "original_bill_amount": original_bill_amount,
        "adjustment_amount": adjustment_amount,
        "adjustment_reason": adjustment_reason,
        "adjustment_date": adjustment_DATE,
        "confirmation_number": adjustment_id
    }

    if result == 1:
        return templates.TemplateResponse("adjustment/adjustment_receipt.html", {"request": request, "adjustment_details": adjustment_details})
    else:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "An error occured while processing the request. Please try again. Make sure the values are correct"})

