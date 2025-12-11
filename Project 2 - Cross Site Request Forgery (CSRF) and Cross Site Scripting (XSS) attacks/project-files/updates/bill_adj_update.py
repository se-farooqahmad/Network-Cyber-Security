@app.post("/bill-adjustments", response_class=HTMLResponse)
async def post_bill_adjustments(
    request: Request,
    bill_id: int = Form(...),
    officer_name: str = Form(...),
    officer_designation: str = Form(...),
    original_bill_amount: float = Form(...),
    adjustment_amount: float = Form(...),
    adjustment_reason: str = Form(...)
):
    
    # TODO: Before proceeding make sure to put in your authentication and authorization logic in here.

    cursor = connection.cursor()

    bill_query = f"SELECT B.BILLID, B.TotalAmount_BeforeDueDate FROM BILL B WHERE B.BILLID = {bill_id}"
    cursor.execute(bill_query)
    bill_row = cursor.fetchone()

    if not bill_row:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "Invalid BillID provided."})

    # check if the bill is unpaid so far
    paymentstatus_query = f"SELECT PD.PaymentStatus FROM PAYMENTDETAILS PD WHERE PD.BILLID = {bill_id}"
    cursor.execute(paymentstatus_query)
    paymentstatus = cursor.fetchone()[0]

    if paymentstatus:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "The bill has already been paid. Adjustments cannot be made to a paid bill."})

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
        return templates.TemplateResponse("adjustment_receipt.html", {"request": request, "adjustment_details": adjustment_details})
    else:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "An error occured while processing the request. Please try again. Make sure the values are correct"})
