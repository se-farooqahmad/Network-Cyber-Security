from fastapi import FastAPI, Request, Form, HTTPException, Cookie, Depends, status
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles
import datetime
import os
import oracledb
import jwt
import requests
import secrets
import html
import re

from util import get_bill_data
from access_ctrl import AccessController

# Oracle Database Connection
ORACLE_HOME = os.environ.get("ORACLE_HOME")
oracledb.init_oracle_client(lib_dir=ORACLE_HOME)
user_name = os.environ.get("DB_USERNAME")
user_pswd = os.environ.get("DB_PASSWORD")
db_alias  = os.environ.get("DB_ALIAS")
connection = oracledb.connect(user=user_name, password=user_pswd, dsn=db_alias)

# OAuth Config
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
OAUTH_REDIRECT_ENDPOINT = "callback"
AUTH_SERVER_IP = os.environ.get("AUTH_SERVER_IP")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

# FastAPI App
app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

    )
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
access_ctrl = AccessController("access.cfg")

SESSION_COOKIE_NAME = "session_token"
SESSION_DURATION = datetime.timedelta(minutes=2)
HOST_IP = os.environ.get("HOST_IP")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html",
                                        {
                                            "request": request,
                                            "auth_server": AUTH_SERVER_IP,
                                            "client_id": CLIENT_ID,
                                            "redirect_uri": f"https://{HOST_IP}/{OAUTH_REDIRECT_ENDPOINT}"
                                        })

async def validate_session(
    session_token: str | None = Cookie(default=None), 
    csrf_token: str | None = Cookie(default=None)
):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Ensure CSRF token exists and does not regenerate on every request
        if not csrf_token:
            csrf_token = secrets.token_hex(32)

        return {
            "username": payload["sub"], 
            "role": payload.get("role", "user"), 
            "csrf_token": csrf_token
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/callback")
async def getAccessToken(request: Request, code: str | None = None):
    token_url = f"https://{AUTH_SERVER_IP}/token"
    print(token_url)
    data = {"grant_type": "authorization_code", "code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    response = requests.post(token_url, data=data, verify=False)
    print(response.content)
    print(response.status_code)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token")
    token_data = response.json()
    print(token_data)
    access_token = token_data.get("token")
    print(access_token)
    response = RedirectResponse(url="/dashboard",  status_code=303)
    print(SESSION_COOKIE_NAME)
    response.set_cookie(SESSION_COOKIE_NAME, access_token, httponly=True, samesite="Strict", max_age=SESSION_DURATION.total_seconds())
    response.set_cookie("csrf_token", secrets.token_hex(32), httponly=True, samesite="Strict")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, user: dict = Depends(validate_session)):
    print(user)
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user["username"]})

def enforce_access(user, resource):
    """Middleware to enforce role-based access control on endpoints."""
    print("Enforce access")
    role = access_ctrl.get_role_from_username(user["username"])
    print(role)
    if not access_ctrl.is_allowed(role, resource):
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
    return user

@app.get("/bill-payment", response_class=HTMLResponse)
async def get_bill_payment(request: Request, user: dict = Depends(validate_session)):
    enforce_access(user, "/bill-payment")
    return templates.TemplateResponse("bill_payment.html", {"request": request, "csrf_token": user["csrf_token"]})

@app.get("/bill-adjustments", response_class=HTMLResponse)
async def get_bill_adjustments(request: Request, user: dict = Depends(validate_session)):
    enforce_access(user, "/bill-adjustments")
    return templates.TemplateResponse("bill_adjustments.html", {"request": request, "csrf_token": user["csrf_token"]})

@app.get("/bill-retrieval", response_class=HTMLResponse)
async def get_bill_retrieval(request: Request, user: dict = Depends(validate_session)):
    enforce_access(user, "/bill-retrieval")
    return templates.TemplateResponse("bill_retrieval.html", {"request": request, "csrf_token": user["csrf_token"]})


@app.get("/signout", response_class=HTMLResponse)
async def signout(request: Request, user: dict = Depends(validate_session)):
    response = Response()
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

@app.get("/csrf", response_class=HTMLResponse)
async def csrf(request: Request):
    return templates.TemplateResponse("signout.html", {"request": request})

@app.get("/csrf-adjustment", response_class=HTMLResponse)
async def csrf(request: Request):
    return templates.TemplateResponse("csrf-post-adjustment.html", {"request": request})

@app.get("/csrf-payment", response_class=HTMLResponse)
async def csrf(request: Request):
    return templates.TemplateResponse("csrf-post-payment.html", {"request": request})

@app.get("/csrf-retrieval", response_class=HTMLResponse)
async def csrf(request: Request):
    return templates.TemplateResponse("csrf-post-retrieval.html", {"request": request})

@app.get("/csrf-payload", response_class=HTMLResponse)
async def csrf_payload(request: Request, user: dict = Depends(validate_session)):
    return templates.TemplateResponse("csrf-xss-cookie-stealing.html", {"request": request})

@app.get("/csrf-keylogger", response_class=HTMLResponse)
async def csrf_keylogger(request: Request, user: dict = Depends(validate_session)):
    return templates.TemplateResponse("csrf-xss-keylogger.html", {"request": request})

@app.post("/bill-payment", response_class=HTMLResponse)
async def post_bill_payment(request: Request, user: dict = Depends(validate_session), bill_id: int = Form(...), amount: float = Form(...), payment_method_id: int = Form(...)):
    enforce_access(user, "/bill-payment")
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

    return templates.TemplateResponse("payment_receipt.html", {"request": request, "payment_details": payment_details})

@app.post("/bill-retrieval", response_class=HTMLResponse)
async def post_bill_retrieval(request: Request, user: dict = Depends(validate_session),csrf_token: str = Form(...), customer_id: str = Form(...), connection_id: str = Form(...), month: str = Form(...), year: str = Form(...)):
    if csrf_token != user["csrf_token"]:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")    
    enforce_access(user, "/bill-retrieval")
    # TODO: Before proceeding make sure to put in your authentication and authorization logic in here.

    try:
        customer_data, connections_data, bill_data, tariffs_data1, tariffs_data2, tariffs_data3, taxes_data, subsidy_data, ff_data, bills_prev_data, adjustments_data = get_bill_data(connection, customer_id, connection_id, month, year)

        bill_details = {
            "customer_id": customer_id,
            "connection_id": connection_id,
            "customer_name": f"{customer_data[0]} {customer_data[1]}",
            "customer_address": customer_data[2],
            "customer_phone": customer_data[3],
            "customer_email": customer_data[4],
            "connection_type": connections_data[0],
            "division": connections_data[1],
            "subdivision": connections_data[2],
            "installation_date": connections_data[3].strftime("%Y-%m-%d"),
            "meter_type": connections_data[4],
            "issue_date": bill_data[0].strftime("%Y-%m-%d"),
            "net_peak_units": bill_data[1],
            "net_off_peak_units": bill_data[2],
            "bill_amount": bill_data[7],
            "due_date": bill_data[6].strftime("%Y-%m-%d"),
            "amount_after_due_date": bill_data[8],
            "bill_id": bill_data[9],
            "month": month,
            "arrears_amount": bill_data[5],
            "fixed_fee_amount": bill_data[4],
            "tax_amount": bill_data[3],
            # all the applicable tariffs
            "tariffs": [
                {"name": tariffs_data2[0], "units": tariffs_data1[0], "rate": tariffs_data2[1], "amount": tariffs_data1[2]},
                {"name": f"{tariffs_data3[0]} (Off Peak)", "units": tariffs_data1[1], "rate": tariffs_data3[1], "amount": tariffs_data1[3]},
            ],
            # applicable taxes
            "taxes": [
                {"name": row[0], "rate": row[1], "amount": row[1]*bill_data[7]}
                for row in taxes_data
            ],
            "adjustments": [
                {"amount": row[0], "reason": row[1], "date": row[2]}
                for row in adjustments_data
            ],
            # applicable subsidies
            "subsidies": [
                {"name": row[0], "provider_name": row[2], "rate_per_unit": row[1]}
                for row in subsidy_data
            ],
            # applicable fixed fees
            "fixed_fee": [
                {"name": row[0], "amount": row[1]}
                for row in ff_data
            ],
            # the last 10 (or lesser) bills of the customer
            "bills_prev": [
                {"month": f"{row[1]}-{row[0]}", "amount": row[2], "due_date": row[3].strftime("%Y-%m-%d"), "status": row[4]}
                for row in bills_prev_data
            ]
        }

        return templates.TemplateResponse("bill_details.html", {"request": request, "bill_details": bill_details})

    except Exception as e:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": f"An error occured processing the request: {str(e)}"})



def sanitize_input(text):
    """Remove HTML tags and escape special characters."""
    text = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
    return html.escape(text)  # Escape special characters

@app.post("/bill-adjustments", response_class=HTMLResponse)
async def post_bill_adjustments(
    request: Request,
    user: dict = Depends(validate_session),
    csrf_token: str = Form(...),
    bill_id: int = Form(...),
    officer_name: str = Form(...),
    officer_designation: str = Form(...),
    original_bill_amount: float = Form(...),
    adjustment_amount: float = Form(...),
    adjustment_reason: str = Form(...)
):
    if csrf_token != user["csrf_token"]:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    enforce_access(user, "/bill-adjustments")

    cursor = connection.cursor()

    bill_query = f"SELECT B.BILLID, B.TotalAmount_BeforeDueDate FROM BILL B WHERE B.BILLID = {bill_id}"
    cursor.execute(bill_query)
    bill_row = cursor.fetchone()

    if not bill_row:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "Invalid BillID provided."})

    # check if the bill is unpaid so far
    paymentstatus_query = f"SELECT PD.PaymentStatus FROM PAYMENTDETAILS PD WHERE PD.BILLID = {bill_id}"
    cursor.execute(paymentstatus_query)
    paymentstatus = cursor.fetchone()

    if paymentstatus:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "The bill has already been paid. Adjustments cannot be made to a paid bill."})

    # current date as the adjustment date
    adjustment_DATE = datetime.datetime.now()

    # generate an adjustment id
    adjustment_id = int(str(bill_id) + str(adjustment_DATE.year) + str(adjustment_DATE.month))

    result = cursor.callfunc("fun_adjust_Bill", int, [adjustment_id, bill_id, adjustment_DATE, officer_name, officer_designation, original_bill_amount, adjustment_amount, adjustment_reason])

    # **Sanitize adjustment_reason before displaying**
    safe_adjustment_reason = sanitize_input(adjustment_reason)

    adjustment_details = {
        "bill_id": bill_id,
        "officer_name": officer_name,
        "officer_designation": officer_designation,
        "original_bill_amount": original_bill_amount,
        "adjustment_amount": adjustment_amount,
        "adjustment_reason": safe_adjustment_reason,  # Use sanitized text
        "adjustment_date": adjustment_DATE,
        "confirmation_number": adjustment_id
    }

    if result == 1:
        return templates.TemplateResponse("adjustment_receipt.html", {"request": request, "adjustment_details": adjustment_details})
    else:
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": "An error occurred while processing the request. Please try again. Make sure the values are correct."})

