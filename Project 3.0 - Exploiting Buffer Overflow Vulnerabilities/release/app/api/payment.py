from fastapi import APIRouter, Request, Depends, HTTPException, status, Cookie, Form
from fastapi.responses import HTMLResponse
from app.auth.auth import validate_session
from app.security.authorization import authorization_mgr
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATE_DIR
from app.db.database import get_db

import datetime

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Bill payment page
@router.get("/bill-payment", response_class=HTMLResponse)
async def get_bill_payment(request: Request, user: dict = Depends(validate_session)):
    authorization_mgr.check_access(request, user)
    return templates.TemplateResponse("payment/bill_payment.html", {"request": request})

@router.post("/bill-payment", response_class=HTMLResponse)
async def post_bill_payment(request: Request, bill_id: int = Form(...), amount: float = Form(...), payment_method_id: int = Form(...), user: dict = Depends(validate_session), connection = Depends(get_db)):

    authorization_mgr.check_access(request, user)
    
    # try:
    cursor = connection.cursor()

    # check if the bill exists
    bill_query = f"SELECT B.BILLID FROM BILL B WHERE B.BILLID = {bill_id}"
    cursor.execute(bill_query)
    bill_row = cursor.fetchone()

    if not bill_row:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "Invalid BillID provided."})

    payment_date = datetime.datetime.now()

    # This function processes the payment in the database. It returns 1 if the payment is successful, and 0 otherwise. (currently no support for error codds)
    status = cursor.callfunc("fun_process_Payment", int, [bill_id, payment_date, payment_method_id, amount])

    if status != 1:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "An error occured while processing the request. Please try again. Make sure the values are correct"})

    # find the payment status and the outstanding amount
    paymentstatus_query = f"SELECT PD.PaymentStatus FROM PAYMENTDETAILS PD WHERE PD.BILLID = {bill_id}"
    cursor.execute(paymentstatus_query)
    paymentstatus = cursor.fetchone()[0]

    pd_description = cursor.execute(f"SELECT PaymentMethodDescription FROM PaymentMethods WHERE PaymentMethodID = {payment_method_id}").fetchone()[0]

    payment_details = {
        "bill_id": bill_id,
        "amount": amount,
        "payment_method_id": payment_method_id,
        "payment_method_description": pd_description,
        "payment_date": payment_date,
        "payment_status": paymentstatus
    }

    return templates.TemplateResponse("payment/payment_receipt.html", {"request": request, "payment_details": payment_details})

