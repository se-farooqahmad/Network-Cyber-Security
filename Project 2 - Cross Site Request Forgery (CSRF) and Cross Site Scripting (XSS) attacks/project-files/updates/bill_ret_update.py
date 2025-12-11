@app.post("/bill-retrieval", response_class=HTMLResponse)
async def post_bill_retrieval(request: Request, customer_id: str = Form(...), connection_id: str = Form(...), month: str = Form(...), year: str = Form(...)):

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