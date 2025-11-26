from fastapi import FastAPI, Request, HTTPException, Response
import requests
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from weasyprint import HTML, CSS
from functools import lru_cache
import io
from typing import Optional, Dict, List
import httpx

app = FastAPI()

# Test commit for vishal
# add new comment for test

# Optimize the Pydantic model with better typing and validation
class GuestInfo(BaseModel):
    name: str
    room_type: str
    occupancy: str
    meal_plan: str

class BookingData(BaseModel):
    NAME: Optional[str] = Field(None, description="Guest name")
    CHECKIN: Optional[str] = Field(None, description="Check-in date")
    CHECKOUT: Optional[str] = Field(None, description="Check-out date")
    DAYOF_CHECKIN: Optional[str] = None
    DAYOF_CHECKOUT11: Optional[str] = None
    NO_OF_NIGHTS: Optional[str] = None
    CHECK_IN_TIME: Optional[str] = None
    CHECK_OUT_TIME: Optional[str] = None
    HOTELNAME: Optional[str] = None
    HOTELADDRESS: Optional[str] = None
    HOTELPHONE: Optional[str] = None
    ROOMCOUNT: Optional[str] = None
    CLIENT: Optional[str] = None
    GUESTCOUNT: Optional[str] = None
    ROOM_CHARGES: Optional[str] = None
    INCLUSIONS: Optional[str] = None
    SUBTOTAL: Optional[str] = None
    GST_VALUE: Optional[str] = None
    AMT_TO_BE_PAID: Optional[str] = None
    PAYMENTMODE: Optional[str] = None
    LOCATIONLINK: Optional[str] = None
    CANCELLATIONPOLICY: Optional[str] = None
    ADDON_POLICES: Optional[str] = None
    DEFAULT_POLICES: Optional[str] = None
    EMPNAME: Optional[str] = None
    EMPPHONE: Optional[str] = None
    EMPEMAIL: Optional[str] = None
    TABLEDATA: Optional[Dict[str, list]] = None
    SHOWTRAIFF: Optional[str] = None
    CLIENT_GST: Optional[str] = None
    FILENAME: Optional[str] = None
    Booking_Date: Optional[str] = None
    Booking_Id: Optional[str] = None
    Brid: Optional[str] = None
    GST_PRECENT: Optional[str] = None
    NEARBY:Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "NAME": "John Doe",
                "CHECKIN": "2024-01-01",
                # Add other example values as needed
            }
        }

# Cache the HTML template reading
@lru_cache(maxsize=1)
def get_html_template(template_name: str) -> str:
    try:
        with open(template_name, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Template file {template_name} not found")

# Optimize PDF generation with error handling
def generate_pdf_from_html(html_content: str) -> io.BytesIO:
    try:
        pdf_io = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_io, presentational_hints=True)
        pdf_io.seek(0)
        return pdf_io
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

# Optimize table generation with list comprehension and join
def generate_guest_table(table_data: Dict[str, list]) -> str:
    if not table_data or "GUESTNAME" not in table_data:
        return ""

    header = '''<table style="border-collapse: collapse; width: 100%; border: 0px solid #dddddd; font-size:16px;">
        <tr>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">S.no</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Guest Name</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Room Type</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Occupancy</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Meal Plan</th>
        </tr>'''

    rows = []
    for i, guest_name in enumerate(table_data["GUESTNAME"], 1):
        row = f'''<tr>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{i}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{guest_name}</td>
            <td style="border: 0px solid #dddddd; text-align:center; padding: 8px;">{table_data.get("ROOMTYPE", [""])[i-1]}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("OCC", [""])[i-1]}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("MEALPLAN", [""])[i-1]}</td>
        </tr>'''
        rows.append(row)

    return header + "".join(rows) + "</table>"

@app.post("/booking-confirmation")
async def booking_confirmation(data: BookingData):
    try:
        # print(data.dict()) 
        # Get cached template
        html_content = get_html_template("voucher.html")
        
        # Generate guest table
        table = generate_guest_table(data.TABLEDATA)

        # Create replacements dict with only non-None values
        replacements = {
            key: str(value) if value is not None else ""
            for key, value in {
                "{{ name }}": data.NAME,
                "{{checkindate}}": data.CHECKIN,
                "{{checkoutdate}}": data.CHECKOUT,
                "{{dayofcheckin}}": data.DAYOF_CHECKIN,
                "{{dayofcheckout}}": data.DAYOF_CHECKOUT11,
                "{{no_of_night}}": data.NO_OF_NIGHTS,
                "{{checkintime}}": data.CHECK_IN_TIME,
                "{{checkouttime}}": data.CHECK_OUT_TIME,
                "{{hotelname}}": data.HOTELNAME,
                "{{hoteladdress}}": data.HOTELADDRESS,
                "{{hotelphone}}": str(data.HOTELPHONE) if data.HOTELPHONE else "",
                "{{noofrooms}}": data.ROOMCOUNT,
                "{{noofguest}}": data.GUESTCOUNT,
                "{{roomcharges}}": data.ROOM_CHARGES,
                "{{inclusions}}": data.INCLUSIONS,
                "{{gst}}": data.GST_VALUE,
                "{{SUBTOTAL}}": data.SUBTOTAL,
                "{{grandtotal}}": data.AMT_TO_BE_PAID,
                "{{PAYMENTMODE}}": data.PAYMENTMODE,
                "{{ADDON_POLICES}}": data.ADDON_POLICES,
                "{{DEFAULT_POLICES}}": data.DEFAULT_POLICES,
                "{{CANCELLATIONPOLICY}}": data.CANCELLATIONPOLICY,
                "{{GUESTTABLE}}": table,
                "{{EMPNAME}}": data.EMPNAME,
                "{{EMPPHONE}}": data.EMPPHONE,
                "{{EMPEMAIL}}": data.EMPEMAIL,
                "{{location}}": data.LOCATIONLINK,
                "{{client}}": data.CLIENT,
                "{{clientgst}}": data.CLIENT_GST,
                "{{booking_date}}": data.Booking_Date,
                "{{booking_id}}": data.Booking_Id,
                "{{Brid}}": data.Brid,
                "{{gstpre}}": data.GST_PRECENT,
                "{{NEARBY}}" : data.NEARBY
            }.items()
        }

        # Handle Bill to Company case
        if data.PAYMENTMODE == "Bill to Company" or data.PAYMENTMODE == "Pay at Check-In"or data.PAYMENTMODE == "Pay at check Out" or data.PAYMENTMODE == "Prepaid":
            if data.SHOWTRAIFF == "No":
                html_content = html_content.replace(
                    '''<table style="max-width:552px;width:100%;"><tbody><tr><td>Room Charges</td><td style="text-align: right">{{roomcharges}}</td></tr><tr><td>Inclusion</td><td style="text-align: right">{{inclusions}}</td></tr><tr><td>Subtotal</td><td style="text-align: right">{{SUBTOTAL}}</td></tr><tr><td>Tax(gst)</td><td style="text-align: right">{{gst}}</td></tr><tr><td><b>GRAND TOTAL</b></td><td style="text-align: right"><b>{{grandtotal}}</b></td></tr></tbody></table>''',
                    ""
                )
                # Keep only relevant fields for Bill to Company with shown tariff
                #replacements = {k: v for k, v in replacements.items() if k in {
                #   "{{ name }}","{{checkindate}}", "{{checkoutdate}}", "{{dayofcheckin}}","{{dayofcheckout}}","{{no_of_night}}","{{checkintime}}","{{checkouttime}}","{{hotelname}}","{{hoteladdress}}","{{hotelphone}}","{{noofrooms}}","{{noofguest}}","{{roomcharges}}", "{{inclusions}}", "{{gst}}", "{{SUBTOTAL}}","{{grandtotal}}", "{{PAYMENTMODE}}", "{{EMPNAME}}", "{{EMPPHONE}}","{{EMPEMAIL}}", "{{GUESTTABLE}}", "{{SHOWTRAIFF}}", "{{client}}", "{{clientgst}}", "{{booking_date}}", "{{booking_id}}", "{{Brid}}", "{{gstpre}}",
                #}}
            else:
                print("Bill to Company with shown tariff")
                # Remove tariff table if not shown
                #html_content = html_content.replace(
                #    '''<table style="max-width:552px;width:100%;"><tbody><tr><td>Room Charges</td><td style="text-align: right">{{roomcharges}}</td></tr><tr><td>Inclusion</td><td style="text-align: right">{{inclusions}}</td></tr><tr><td>Subtotal</td><td style="text-align: right">{{SUBTOTAL}}</td></tr><tr><td>Tax(gst)</td><td style="text-align: right">{{gst}}</td></tr><tr><td><b>GRAND TOTAL</b></td><td style="text-align: right"><b>{{grandtotal}}</b></td></tr></tbody></table>''',
                #    ""
                #)

        # Remove policies section if no policies
        if not data.ADDON_POLICES and not data.DEFAULT_POLICES:
            html_content = html_content.replace(
                '''<div class="info-section"><h4>Policies:</h4><p>{{ADDON_POLICES}} <br />{{DEFAULT_POLICES}}</p></div>''',
                ""
            )

        # Replace placeholders
        for placeholder, value in replacements.items():
            html_content = html_content.replace(placeholder, value)

        # Generate PDF
        pdf = generate_pdf_from_html(html_content)
        filename = f"{data.FILENAME}.pdf" if data.FILENAME else "booking_confirmation.pdf"

        return StreamingResponse(
            pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#for vochuer for email
class BookingDataMail(BaseModel):
    NAME: str = None
    CHECKIN: str = None
    CHECKOUT: str = None
    DAYOF_CHECKIN: str = None
    DAYOF_CHECKOUT11: str = None
    NO_OF_NIGHTS: str = None
    CHECK_IN_TIME: str = None
    CHECK_OUT_TIME: str = None
    HOTELNAME: str = None
    HOTELADDRESS: str = None
    HOTELPHONE: str = None
    ROOMCOUNT: str = None
    CLIENT: str = None

    GUESTCOUNT:str = None
    ROOM_CHARGES: str = None
    INCLUSIONS: str = None
    SUBTOTAL: str = None
    GST_VALUE: str = None
    AMT_TO_BE_PAID: str = None
    PAYMENTMODE: str = None
    LOCATIONLINK:str = None
    #IMGLINK:str
    CANCELLATIONPOLICY:str=None
    ADDON_POLICES:str=None 
    DEFAULT_POLICES:str=None
    EMPNAME:str = None
    EMPPHONE:str = None
    EMPEMAIL:str =None
    TABLEDATA: Optional[Dict[str, list]] = None
    SHOWTRAIFF: str = None
    CLIENT_GST:str = None
    FILENAME:str = None
    typeofbooking :str = None
    Booking_Date:str = None
    Booking_Id:Optional[str] = None
    Brid:str=None
    GST_PRECENT:str = None

@app.post("/booking-confirmation-mail")
async def booking_confirmation1(data: BookingDataMail):
    # Open and read the HTML file
    with open("voucherMail.html", "r") as file:
        html_content = file.read()

    # HTML table structure
    table = """<table style="border-collapse: collapse; width: 100%; border: 0px solid #dddddd; font-size:16px;">
        <tr>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">S.no</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Guest Name</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Room Type</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Occupancy</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Meal Plan</th>
        </tr>"""

    num_rows = len(data.TABLEDATA["GUESTNAME"])

    # Create a new row for each guest
    for i in range(num_rows):
        s_no = i + 1
        guest_name = data.TABLEDATA.get("GUESTNAME", [""])[i]
        room_type = data.TABLEDATA.get("ROOMTYPE", [""])[i]
        occupancy = data.TABLEDATA.get("OCC", [""])[i]
        meal_plan = data.TABLEDATA.get("MEALPLAN", [""])[i]
        new_row = f"""<tr>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{s_no}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{guest_name}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{room_type}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{occupancy}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{meal_plan}</td>
        </tr>"""
        table += new_row

    # Close the table
    table += "</table>"

    replacements = {
        "{{ name }}": data.NAME,
        "{{checkindate}}": data.CHECKIN,
        "{{checkoutdate}}": data.CHECKOUT,
        "{{dayofcheckin}}": data.DAYOF_CHECKIN,
        "{{dayofcheckout}}": data.DAYOF_CHECKOUT11,
        "{{no_of_night}}": data.NO_OF_NIGHTS,
        "{{checkintime}}": data.CHECK_IN_TIME,
        "{{checkouttime}}": data.CHECK_OUT_TIME,
        "{{hotelname}}": data.HOTELNAME,
        "{{hoteladdress}}": data.HOTELADDRESS,
        "{{hotelphone}}": str(data.HOTELPHONE) if data.HOTELPHONE else " ",
        "{{noofrooms}}": data.ROOMCOUNT,
        "{{noofguest}}": data.GUESTCOUNT,
        "{{roomcharges}}": data.ROOM_CHARGES,
        "{{inclusions}}": data.INCLUSIONS,
        "{{gst}}": data.GST_VALUE,
        "{{SUBTOTAL}}": data.SUBTOTAL,
        "{{grandtotal}}": data.AMT_TO_BE_PAID,
        "{{PAYMENTMODE}}": data.PAYMENTMODE,
        "{{ADDON_POLICES}}": data.ADDON_POLICES,
        "{{DEFAULT_POLICES}}": data.DEFAULT_POLICES,
        "{{CANCELLATIONPOLICY}}": data.CANCELLATIONPOLICY,
        "{{EMPNAME}}": data.EMPNAME,
        "{{EMPPHONE}}": data.EMPPHONE,
        "{{EMPEMAIL}}": data.EMPEMAIL,
        "{{location}}": data.LOCATIONLINK,
        "{{GUESTTABLE}}": table,
        "{{client}}": data.CLIENT,
        "{{clientgst}}": data.CLIENT_GST,
        "{{booking_date}}": data.Booking_Date,
        "{{booking_id}}": data.Booking_Id if data.Booking_Id else " ",
        "{{BRID}}":data.Brid,
        "{{GST_PRECENT}}":data.GST_PRECENT
    }

    if data.PAYMENTMODE == "Bill to Company" or data.PAYMENTMODE == "Pay at Check-In"or data.PAYMENTMODE == "Pay at check Out" or data.PAYMENTMODE == "Prepaid":
            if data.SHOWTRAIFF == "No":
                html_content = html_content.replace(
                    '''<table style="border-collapse:collapse; width:100%" width="100%"><tbody><tr><td style="padding:10px 0; word-wrap:break-word">Room Charges</td><td style="padding:10px 0; word-wrap:break-word; text-align:right" align="right">{{roomcharges}}</td></tr><tr><td style="padding:10px 0; word-wrap:break-word">Inclusion IX</td><td style="padding:10px 0; word-wrap:break-word; text-align:right" align="right">{{inclusions}}</td></tr><tr><td style="padding:10px 0; word-wrap:break-word">Subtotal</td><td style="padding:10px 0; word-wrap:break-word; text-align:right" align="right">{{SUBTOTAL}}</td></tr><tr><td style="padding:10px 0; word-wrap:break-word">Tax( {{GST_PRECENT}} )</td><td style="padding:10px 0; word-wrap:break-word; text-align:right" align="right">{{gst}}</td></tr><tr><td style="padding:10px 0; word-wrap:break-word"><b>GRAND TOTAL</b></td><td style="padding:10px 0; word-wrap:break-word; text-align:right" align="right"><b>{{grandtotal}}</b></td></tr></tbody></table>''',
                    ""
                )
                # Keep only relevant fields for Bill to Company with shown tariff
                #replacements = {k: v for k, v in replacements.items() if k in {
                #   "{{ name }}","{{checkindate}}", "{{checkoutdate}}", "{{dayofcheckin}}","{{dayofcheckout}}","{{no_of_night}}","{{checkintime}}","{{checkouttime}}","{{hotelname}}","{{hoteladdress}}","{{hotelphone}}","{{noofrooms}}","{{noofguest}}","{{roomcharges}}", "{{inclusions}}", "{{gst}}", "{{SUBTOTAL}}","{{grandtotal}}", "{{PAYMENTMODE}}", "{{EMPNAME}}", "{{EMPPHONE}}","{{EMPEMAIL}}", "{{GUESTTABLE}}", "{{SHOWTRAIFF}}", "{{client}}", "{{clientgst}}", "{{booking_date}}", "{{booking_id}}", "{{Brid}}", "{{gstpre}}",
                #}}
            else:
                print("Bill to Company with shown tariff")

    # Replace placeholders in the HTML content with actual values
    for placeholder, value in replacements.items():
        if value:
            html_content = html_content.replace(placeholder, value)

    return HTMLResponse(content=html_content, status_code=200)

#TESTING VOCUHER PDF
class GuestInfo1(BaseModel):
    name: str
    room_type: str
    occupancy: str
    meal_plan: str

class BookingData1(BaseModel):
    typeofbooking: str = None
    NAME: Optional[str] = Field(None, description="Guest name")
    CHECKIN: Optional[str] = Field(None, description="Check-in date")
    CHECKOUT: Optional[str] = Field(None, description="Check-out date")
    DAYOF_CHECKIN: Optional[str] = None
    DAYOF_CHECKOUT11: Optional[str] = None
    NO_OF_NIGHTS: Optional[str] = None
    CHECK_IN_TIME: Optional[str] = None
    CHECK_OUT_TIME: Optional[str] = None
    HOTELNAME: Optional[str] = None
    HOTELADDRESS: Optional[str] = None
    HOTELPHONE: Optional[str] = None
    ROOMCOUNT: Optional[str] = None
    CLIENT: Optional[str] = None
    GUESTCOUNT: Optional[str] = None
    ROOM_CHARGES: Optional[str] = None
    INCLUSIONS: Optional[str] = None
    SUBTOTAL: Optional[str] = None
    GST_VALUE: Optional[str] = None
    AMT_TO_BE_PAID: Optional[str] = None
    PAYMENTMODE: Optional[str] = None
    LOCATIONLINK: Optional[str] = None
    CANCELLATIONPOLICY: Optional[str] = None
    ADDON_POLICES: Optional[str] = None
    DEFAULT_POLICES: Optional[str] = None
    EMPNAME: Optional[str] = None
    EMPPHONE: Optional[str] = None
    EMPEMAIL: Optional[str] = None
    TABLEDATA: Optional[Dict[str, list]] = None
    SHOWTRAIFF: Optional[str] = None
    CLIENT_GST: Optional[str] = None
    FILENAME: Optional[str] = None
    Booking_Date: Optional[str] = None
    Booking_Id: Optional[str] = None
    Brid: Optional[str] = None
    GST_PRECENT: Optional[str] = None
    NEARBY: Optional[str] = None

    class Config1:
        schema_extra = {
            "example": {
                "NAME": "John Doe",
                "CHECKIN": "2024-01-01",
            }
        }

@lru_cache(maxsize=1)
def get_html_template1(template_name: str) -> str:
    try:
        with open(template_name, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Template file {template_name} not found")

def generate_pdf_from_html1(html_content: str) -> io.BytesIO:
    try:
        pdf_io = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_io, presentational_hints=True)
        pdf_io.seek(0)
        return pdf_io
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")



def generate_pdf_from_html1(html_content: str) -> io.BytesIO:
    try:
        pdf_io = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_io, presentational_hints=True)
        pdf_io.seek(0)
        return pdf_io
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

def generate_guest_table1(table_data: Dict[str, list], booking_type: str) -> str:
    if not table_data or "GUESTNAME" not in table_data:
        return ""

    if booking_type != "Bulk":
        header = '''<table style="border-collapse: collapse; width: 100%; border: 0px solid #dddddd; font-size:16px;">
        <tr>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">S.no</th>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Guest Name</th>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Room Type</th>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Occupancy</th>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Meal Plan</th>
        </tr>'''
        rows = []
        for i, guest_name in enumerate(table_data["GUESTNAME"], 1):
            row = f'''<tr>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{i}</td>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{guest_name}</td>
                <td style="border: 0px solid #dddddd; text-align:center; padding: 8px;">{table_data.get("ROOMTYPE", [""])[i-1]}</td>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("OCC", [""])[i-1]}</td>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("MEALPLAN", [""])[i-1]}</td>
            </tr>'''
            rows.append(row)
        return header + "".join(rows) + "</table>"

    else:
        # Bulk booking
        include_guest_name_column = all(name and name.strip() for name in table_data["GUESTNAME"])

        # Start table header
        header = '''<table style="border-collapse: collapse; width: 100%; border: 0px solid #dddddd; font-size:16px;">
        <tr>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">S.no</th>'''

        if include_guest_name_column:
            header += '''<th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Guest Name</th>'''

        header += '''
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Check In & Out</th>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Description</th>
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Nights</th>
        </tr>'''

        # Build rows
        rows = []
        for i in range(len(table_data["GUESTNAME"])):
            row = f'''<tr>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{i+1}</td>'''

            if include_guest_name_column:
                guest_name = table_data["GUESTNAME"][i]
                row += f'''<td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{guest_name}</td>'''

            row += f'''
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("CHECKIN", [""])[i]} to {table_data.get("CHECKOUT", [""])[i]}</td>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("ROOMTYPE", [""])[i]}-{table_data.get("OCC", [""])[i]}-{table_data.get("MEALPLAN", [""])[i]} x {table_data.get("QTY", [""])[i]}</td>
                <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{table_data.get("NIGHTS", [""])[i]}</td>
            </tr>'''
            rows.append(row)

        return header + "".join(rows) + "</table>"

@app.post("/booking-confirmation-test")
async def booking_confirmation(data: BookingData1):
    try:
        html_content = get_html_template1("Bulkvoucher.html" if data.typeofbooking == "Bulk" else "voucher.html")

        table = generate_guest_table1(data.TABLEDATA,data.typeofbooking)

        replacements = {
            key: str(value) if value is not None else ""
            for key, value in {
                "{{ name }}": data.NAME,
                "{{checkindate}}": data.CHECKIN,
                "{{checkoutdate}}": data.CHECKOUT,
                "{{dayofcheckin}}": data.DAYOF_CHECKIN,
                "{{dayofcheckout}}": data.DAYOF_CHECKOUT11,
                "{{no_of_night}}": data.NO_OF_NIGHTS,
                "{{checkintime}}": data.CHECK_IN_TIME,
                "{{checkouttime}}": data.CHECK_OUT_TIME,
                "{{hotelname}}": data.HOTELNAME,
                "{{hoteladdress}}": data.HOTELADDRESS,
                "{{hotelphone}}": data.HOTELPHONE if data.HOTELPHONE else " ",
                "{{noofrooms}}": data.ROOMCOUNT,
                "{{noofguest}}": data.GUESTCOUNT,
                "{{roomcharges}}": data.ROOM_CHARGES,
                "{{inclusions}}": data.INCLUSIONS,
                "{{no_of_night}}": data.NO_OF_NIGHTS,
                "{{gst}}": data.GST_VALUE,
                "{{SUBTOTAL}}": data.SUBTOTAL,
                "{{grandtotal}}": data.AMT_TO_BE_PAID,
                "{{PAYMENTMODE}}": data.PAYMENTMODE,
                "{{ADDON_POLICES}}": data.ADDON_POLICES,
                "{{DEFAULT_POLICES}}": data.DEFAULT_POLICES,
                "{{CANCELLATIONPOLICY}}": data.CANCELLATIONPOLICY,
                "{{GUESTTABLE}}": table,
                "{{EMPNAME}}": data.EMPNAME,
                "{{EMPPHONE}}": data.EMPPHONE,
                "{{EMPEMAIL}}": data.EMPEMAIL,
                "{{location}}": data.LOCATIONLINK,
                "{{client}}": data.CLIENT,
                "{{clientgst}}": data.CLIENT_GST,
                "{{booking_date}}": data.Booking_Date,
                "{{booking_id}}": data.Booking_Id if data.Booking_Id else " ",
                "{{Brid}}": data.Brid,
                "{{gstpre}}": data.GST_PRECENT,
                "{{NEARBY}}": data.NEARBY
            }.items()
        }

        if data.PAYMENTMODE in ["Bill to Company", "Pay at Check-In", "Pay at check Out", "Prepaid"]:
            if data.SHOWTRAIFF == "No":
                html_content = html_content.replace(
                    '''<table style="max-width:552px;width:100%;"><tbody><tr><td>Room Charges</td><td style="text-align: right">{{roomcharges}}</td></tr><tr><td>Inclusion</td><td style="text-align: right">{{inclusions}}</td></tr><tr><td>Subtotal</td><td style="text-align: right">{{SUBTOTAL}}</td></tr><tr><td>Tax(gst)</td><td style="text-align: right">{{gst}}</td></tr><tr><td><b>GRAND TOTAL</b></td><td style="text-align: right"><b>{{grandtotal}}</b></td></tr></tbody></table>''',
                    ""
                )
            else:
                print("Bill to Company with shown tariff")

        if data.PAYMENTMODE in ["Pay at Check-In", "Pay at check Out", "Prepaid"]:
            html_content = html_content.replace("GRAND TOTAL", "Total Amount to pay")
            html_content = html_content.replace(
                '''<p style="font-size:x-small; margin-bottom:10px; margin-top:0"><small>*Any extra expenses/meals apart from Room rent will be payable at the hotel</small></p>''',
                ""
            )

        if not data.ADDON_POLICES and not data.DEFAULT_POLICES:
            html_content = html_content.replace(
                '''<div class="info-section"><h4>Policies:</h4><p>{{ADDON_POLICES}} <br />{{DEFAULT_POLICES}}</p></div>''',
                ""
            )

        for placeholder, value in replacements.items():
            html_content = html_content.replace(placeholder, value)

        pdf = generate_pdf_from_html(html_content)
        filename = f"{data.FILENAME}.pdf" if data.FILENAME else "booking_confirmation.pdf"

        return StreamingResponse(
            pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TESTING VOCUHER PDF

@app.post("/booking-confirmation-mail-test")
async def booking_confirmation2(data: BookingDataMail):
    # HTML table structure
    table = ""

    if data.typeofbooking == "Bulk":
        # Open and read the HTML file
        with open("BulkVoucherMail.html", "r") as file:
            html_content = file.read()

        # bulk booking
        table_data = data.TABLEDATA
        include_guest_name_column = all(name and name.strip() for name in table_data["GUESTNAME"])

        header = """<table style="border-collapse: collapse; width: 100%; border: 0px solid #dddddd; font-size:16px;">
        <tr>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">S.no</th>"""

        if include_guest_name_column:
            header += '''
            <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Guest Name</th>'''

        header += '''
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Check In & Out</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Description</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Nights</th>
        </tr>'''

        num_rows = len(table_data["ROOMTYPE"])

        rows = []
        for i in range(num_rows):
            s_no = i + 1
            checkin = table_data.get("CHECKIN", [""])[i]
            checkout = table_data.get("CHECKOUT", [""])[i]
            qty = table_data.get("QTY", [""])[i]
            guest_name = table_data.get("GUESTNAME", [""])[i]
            room_type = table_data.get("ROOMTYPE", [""])[i]
            occupancy = table_data.get("OCC", [""])[i]
            meal_plan = table_data.get("MEALPLAN", [""])[i]
            nights = table_data.get("NIGHTS", [""])[i]

            row = f"""<tr>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{s_no}</td>"""

            if include_guest_name_column:
                row += f"""<td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{guest_name}</td>"""

            row += f"""
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{checkin} to {checkout}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{room_type}-{occupancy}-{meal_plan} x {qty}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{nights}</td>
            </tr>"""

            rows.append(row)

        table = header + "".join(rows) + "</table>"

    else:
        # Open and read the HTML file  vocuherMail.html => BulkVoucherMail.html
        with open("voucherMail.html", "r") as file:
            html_content = file.read()

        table = """<table style="border-collapse: collapse; width: 100%; border: 0px solid #dddddd; font-size:16px;">
        <tr>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">S.no</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Guest Name</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Room Type</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Occupancy</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Inclusion Services</th>
        <th style="border: 0px solid #dddddd; text-align: center; padding: 8px;">Meal Plan</th>
        </tr>"""

        num_rows = len(data.TABLEDATA["GUESTNAME"])

        for i in range(num_rows):
            s_no = i + 1
            guest_name = data.TABLEDATA.get("GUESTNAME", [""])[i]
            room_type = data.TABLEDATA.get("ROOMTYPE", [""])[i]
            occupancy = data.TABLEDATA.get("OCC", [""])[i]
            inclusion_services = data.TABLEDATA.get("INCLUSION_SERVICES", [""])[i]
            meal_plan = data.TABLEDATA.get("MEALPLAN", [""])[i]

            new_row = f"""<tr>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{s_no}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{guest_name}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{room_type}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{occupancy}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{inclusion_services}</td>
            <td style="border: 0px solid #dddddd; text-align: center; padding: 8px;">{meal_plan}</td>
            </tr>"""
            table += new_row

        table += "</table>"
        print("TABLE DATA:", data.TABLEDATA)


    replacements = {
        "{{ name }}": data.NAME,
        "{{checkindate}}": data.CHECKIN,
        "{{checkoutdate}}": data.CHECKOUT,
        "{{dayofcheckin}}": data.DAYOF_CHECKIN,
        "{{dayofcheckout}}": data.DAYOF_CHECKOUT11,
        "{{no_of_night}}": data.NO_OF_NIGHTS,
        "{{checkintime}}": data.CHECK_IN_TIME,
        "{{checkouttime}}": data.CHECK_OUT_TIME,
        "{{hotelname}}": data.HOTELNAME,
        "{{hoteladdress}}": data.HOTELADDRESS,
        "{{hotelphone}}": str(data.HOTELPHONE) if data.HOTELPHONE else "",
        "{{noofrooms}}": data.ROOMCOUNT,
        "{{noofguest}}": data.GUESTCOUNT,
        "{{roomcharges}}": data.ROOM_CHARGES,
        "{{inclusions}}": data.INCLUSIONS,
        "{{gst}}": data.GST_VALUE,
        "{{SUBTOTAL}}": data.SUBTOTAL,
        "{{grandtotal}}": data.AMT_TO_BE_PAID,
        "{{PAYMENTMODE}}": data.PAYMENTMODE,
        "{{ADDON_POLICES}}": data.ADDON_POLICES,
        "{{DEFAULT_POLICES}}": data.DEFAULT_POLICES,
        "{{CANCELLATIONPOLICY}}": data.CANCELLATIONPOLICY,
        "{{EMPNAME}}": data.EMPNAME,
        "{{EMPPHONE}}": data.EMPPHONE,
        "{{EMPEMAIL}}": data.EMPEMAIL,
        "{{location}}": data.LOCATIONLINK,
        "{{GUESTTABLE}}": table,
        "{{client}}": data.CLIENT,
        "{{clientgst}}": data.CLIENT_GST,
        "{{booking_date}}": data.Booking_Date,
        "{{booking_id}}":data.Booking_Id if data.Booking_Id else " ",
        "{{BRID}}": data.Brid,
        "{{GST_PRECENT}}": data.GST_PRECENT
    }

    if data.PAYMENTMODE in ["Bill to Company", "Pay at Check-In", "Pay at check Out", "Prepaid"]:
        if data.SHOWTRAIFF == "No":
            html_content = html_content.replace(
                '''<table style="max-width:552px;width:100%;"><tbody><tr><td>Room Charges</td><td style="text-align: right">{{roomcharges}}</td></tr><tr><td>Inclusion</td><td style="text-align: right">{{inclusions}}</td></tr><tr><td>Subtotal</td><td style="text-align: right">{{SUBTOTAL}}</td></tr><tr><td>Tax(gst)</td><td style="text-align: right">{{gst}}</td></tr><tr><td><b>GRAND TOTAL</b></td><td style="text-align: right"><b>{{grandtotal}}</b></td></tr></tbody></table>''',
                ""
            )
        else:
            print("Bill to Company with shown tariff")

    if data.PAYMENTMODE in ["Pay at Check-In", "Pay at check Out", "Prepaid"]:
        html_content = html_content.replace("GRAND TOTAL", "Total Amount to pay")
        html_content = html_content.replace(
            '''<p style="font-size:x-small; margin-bottom:10px; margin-top:0"><small>*Any extra expenses/meals apart from Room rent will be payable at the hotel</small></p>''',
            ""
        )

    for placeholder, value in replacements.items():
        if value:
            html_content = html_content.replace(placeholder, value)

    return HTMLResponse(content=html_content, status_code=200)

@app.get("/")
async def root():
    print(f"Test")
    return {"greeting": "Hello, Niyas!", "message": "Welcome to FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/test1")
async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/get")
    return response.json

@app.post("/create")
async def create_user(request: Request):
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        print(f"Request body: {body}")
        #return {"Testresponse": "Test"}
        # Make the request to the external API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://reqres.in/api/users",
                headers={"Content-Type": "application/json"},
                json=body
            )

        # Return the response from the external API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}

@app.post("/getprop")
async def get_prop(request: Request):
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        print(f"Request body: {body}")
        # Make the request to the Bakuun API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wsb.devbakuun.cloud/v2/getproperty/test/RDK64/139658",
                headers={"Content-Type": "application/json"},
                json=body
            )
        # Return the response from the Bakuun API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}

@app.post("/mps")
async def mps_check(request: Request):
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        print(f"Request body: {body}")
        #return {"Testresponse": "Test"}
        # Make the request to the Bakuun API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wspull.devbakuun.cloud/v1/mpsoccupancy/test/RDK64/615890",
                headers={"Content-Type": "application/json"},
                json=body
            )
        # Print raw response text for debugging
        raw_response_text = response.text
        print(f"Raw response text: {raw_response_text}")
        # Return the response from the external API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}


#mps search results
@app.post("/mpsoccupancy/{token}/results")
async def mps_search(token : str,request: Request):
    api_url ="https://wspull.devbakuun.cloud/v1/RDK64/mpsoccupancy/"+token+"/results"
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        print(f"Request body: {body}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        response = requests.get(api_url, json=body, headers={"Content-Type": "application/json","Accept": "application/json"})
        print(f"Response: {response}")

        # Return the response from the external API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}     

@app.post("/sps")
async def sps(request: Request):
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        print(f"Request body: {body}")
        #return {"Testresponse": "Test"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wspull.devbakuun.cloud/v1/spsoccupancy/test/RDK64/647936",
                headers={"Content-Type": "application/json"},
                json=body
            )

        # Return the response from the external API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}
    
@app.post("/spsoccupancy/{token}/results")
async def sps_token(token : str,request: Request):
    api_url = "https://wspull.devbakuun.cloud/v1/RDK64/spsoccupancy/" + token +"/results"
    print(f"API URL: {api_url}")
    try:
        if not await request.body():
            return {"error": "Request body is empty1:" +request}
        body = await request.json()
        print(f"Request body: {body}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    try:
        if not await request.body():
            return {"error": "Request body is empty2"+request}
        body = await request.json()
        print(f"Successfull Request body: {body}")
        #return {"Testresponse": "Test"}
        response = requests.get(api_url, json=body, headers={"Content-Type": "application/json","Accept": "application/json"})
        print(f"Response: {response.text}")
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         api_url,
        #         headers={"Content-Type": "application/json","Accept": "application/json"},
        #         json=body
        #     )

        # Return the response from the external API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}

@app.post("/booking")
async def booking(request: Request):
    try:
        if not await request.body():
            return {"error": "Request body is empty"}
        body = await request.json()
        print(f"Request body: {body}")
        #return {"Testresponse": "Test"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wspull.devbakuun.cloud/v1/booking/test/RDK64/965220",
                headers={"Content-Type": "application/json"},
                json=body
            )

        # Return the response from the external API
        return response.json()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "Unexpected error occurred"}

@app.post("/emtactivity/{action}")
async def emt_activity(action: str, request: Request):
    try:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Request body is empty or invalid JSON")
        print(f"Request body: {body}")
        async with httpx.AsyncClient() as client:
            upstream_response = await client.post(
                f"http://stagingactivityapi.easemytrip.com/Activity.svc/json/{action}",
                headers={"Content-Type": "application/json"},
                json=body
            )
        content = await upstream_response.aread()
        content_type = upstream_response.headers.get("content-type", "application/octet-stream")
        return Response(
            content=content,
            status_code=upstream_response.status_code,
            media_type=content_type
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")