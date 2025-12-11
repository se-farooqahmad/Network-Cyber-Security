from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from app.auth.auth import validate_session
from app.security.authorization import authorization_mgr
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATE_DIR
from app.db.database import get_db

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATE_DIR)

def get_bill_data(connection, customer_id, connection_id, month, year):
    cursor = connection.cursor()

    # fetch corresponding customer info
    cust_query = f"""
    SELECT 
        CUST.FirstName, CUST.LastName, CUST.Address, CUST.PhoneNumber, CUST.Email
    FROM 
        CUSTOMERS CUST JOIN CONNECTIONS CONN ON CUST.CUSTOMERID = CONN.CUSTOMERID
    WHERE 
        CONN.CUSTOMERID = '{customer_id}' AND CONN.connectionid = '{connection_id}'
    """

    cursor.execute(cust_query)
    customer_data = cursor.fetchone()

    if not customer_data:
        raise Exception("Customer or connection ID not found.")

    # fetches the required connection info
    connections_query = f"""
    SELECT 
        CT.description, DIV.divisionname, DIV.subdivname, CONN.installationdate, CONN.metertype
    FROM 
        CONNECTIONS CONN
        JOIN CONNECTIONTYPES CT on CONN.connectiontypecode = CT.connectiontypecode
        JOIN DIVINFO DIV on (CONN.divisionid = DIV.divisionid and CONN.subdivid = DIV.subdivid)
    WHERE
        CONN.connectionid = '{connection_id}'
    """

    cursor.execute(connections_query)
    connections_data = cursor.fetchone()

    # fetches the required billing details against the bill
    bill_query = f"""
    SELECT 
        B.billissuedate, B.net_peakunits, B.net_offpeakunits, B.taxamount, B.fixedfee, B.arrears, B.duedate, B.totalamount_beforeduedate, B.totalamount_afterduedate, B.billid
    FROM
        BILL B
    WHERE 
        B.connectionid = '{connection_id}'
        AND B.billingmonth = {month}
        AND B.billingyear = {year}
    """

    cursor.execute(bill_query)
    bill_info = cursor.fetchone()

    if not bill_info:
        raise Exception("No bill record found.")

    bill_id = bill_info[9]
    bill_issuedate = bill_info[0]

    bill_data = bill_info

    # get all applicable taxes against the bill
    taxes_query = f"""
    SELECT 
        TR.taxtype, TR.rate
    FROM 
        TAXRATES TR
        JOIN CONNECTIONS C on C.connectiontypecode = TR.connectiontypecode
    WHERE
        C.connectionid = '{connection_id}'
        AND '{bill_issuedate}' BETWEEN TR.StartDate AND TR.EndDate
    """

    cursor.execute(taxes_query)
    taxes_data = cursor.fetchall()

    ff_query = f"""
    SELECT 
        F.fixedchargetype, F.fixedfee
    FROM 
        FIXEDCHARGES F
        JOIN CONNECTIONS C ON C.connectiontypecode = F.connectiontypecode
    WHERE
        C.connectionid = '{connection_id}'
        AND '{bill_issuedate}' BETWEEN F.startdate AND F.enddate
    """
    
    cursor.execute(ff_query)
    ff_data = cursor.fetchall()

    # fetch previous bills
    bills_prev_query = f"""
    SELECT 
        b.billingmonth, b.billingyear, b.totalamount_beforeduedate, b.duedate, p.paymentstatus
    FROM 
        bill b
        LEFT JOIN paymentdetails p ON b.billid = p.billid
    WHERE 
        b.connectionid = '{connection_id}'
        AND (b.billingyear < {year} OR (b.billingyear = {year} AND b.billingmonth < {month}))
    FETCH FIRST 10 ROWS ONLY
    """

    cursor.execute(bills_prev_query)
    bills_prev_data = cursor.fetchmany(size=10)

    # fetch adjustments details
    adjustments_query = f"""
    SELECT 
        ADJ.AdjustmentAmount, ADJ.AdjustmentReason, ADJ.AdjustmentDate
    FROM 
        BILLADJUSTMENTS ADJ
    WHERE 
        ADJ.BILLID = '{bill_id}'
    """

    cursor.execute(adjustments_query)
    adjustments_data = cursor.fetchall()
    
    return customer_data, connections_data, bill_data, taxes_data, ff_data, bills_prev_data, adjustments_data

# Bill generation page
@router.get("/bill-retrieval", response_class=HTMLResponse)
async def get_bill_retrieval(request: Request, user: dict = Depends(validate_session)):

    authorization_mgr.check_access(request, user)
    return templates.TemplateResponse("retrieval/bill_retrieval.html", {"request": request})

@router.post("/bill-retrieval", response_class=HTMLResponse)
async def post_bill_retrieval(request: Request, customer_id: str = Form(...), connection_id: str = Form(...), month: str = Form(...), year: str = Form(...), user: dict = Depends(validate_session), connection = Depends(get_db)):

    authorization_mgr.check_access(request, user)

    try:
        # make sure valid year and month are given
        if (not (1 <= int(month) <= 12)) or (not (2000 <= int(year) <= 2050)):
            raise Exception("Invalid month or year provided.")

        customer_data, connections_data, bill_data, taxes_data, ff_data, bills_prev_data, adjustments_data = get_bill_data(connection, customer_id, connection_id, month, year)

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
            # applicable taxes
            "taxes": [
                {"name": row[0], "rate": row[1], "amount": row[1]*bill_data[7]}
                for row in taxes_data
            ],
            "adjustments": [
                {"amount": row[0], "reason": row[1], "date": row[2]}
                for row in adjustments_data
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

        return templates.TemplateResponse("retrieval/bill_details.html", {"request": request, "bill_details": bill_details})

    except Exception as e:
        print(e)
        return templates.TemplateResponse(request=request, name="error.html", context={"error_msg": f"An error occured processing the request: {str(e)}"})

