import os
import re
import tempfile
import urllib.request
import pandas as pd
from datetime import datetime
from app import db
from app.models.invoice_booking import InvoiceBooking

# Column mapping: Excel header -> model field
COLUMN_MAP = {
    'Invoice No': 'invoice_no',
    'Invoice Date': 'invoice_date',
    'Revenue Date': 'revenue_date',
    'month': 'month',
    'Acc Code': 'acc_code',
    'Customer Name': 'customer_name',
    'Reference ID': 'reference_id',
    'Booking Code': 'booking_code',
    'Booking Master Desc': 'booking_master_desc',
    'Booking Departure': 'booking_departure',
    'Booking Category': 'booking_category',
    'Goods': 'goods',
    'Location From': 'location_from',
    'Location To': 'location_to',
    'Group Billing': 'group_billing',
    'Invoice Item Desc': 'invoice_item_desc',
    'Remarks': 'remarks',
    'Currency': 'currency',
    'Quantity': 'quantity',
    'Unit Price': 'unit_price',
    'Foreign Total': 'foreign_total',
    'Foreign Tax': 'foreign_tax',
    'Foreign Total With Tax': 'foreign_total_with_tax',
    'Local Total': 'local_total',
    'Local Tax': 'local_tax',
    'Local Total With Tax': 'local_total_with_tax',
    'Invoice Status': 'invoice_status',
    'Last Modified User': 'last_modified_user',
    'Last Modified Date Time': 'last_modified_date_time',
    'Created By': 'created_by',
    'Created Date Time': 'created_date_time',
    'Actual Departure': 'actual_departure',
    'Actual Arrival': 'actual_arrival',
    'Booking Requested Arrival': 'booking_requested_arrival',
    'Fast Invoice': 'fast_invoice',
    'TWB': 'twb',
}

DATE_FIELDS = {
    'invoice_date', 'revenue_date', 'last_modified_date_time',
    'created_date_time', 'actual_departure', 'actual_arrival',
    'booking_requested_arrival',
}

NUMERIC_FIELDS = {
    'quantity', 'unit_price', 'foreign_total', 'foreign_tax',
    'foreign_total_with_tax', 'local_total', 'local_tax', 'local_total_with_tax',
}


def parse_date(value):
    """Try to parse a date value from various formats."""
    if pd.isna(value) or value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%Y %H:%M:%S',
                     '%m/%d/%Y', '%m/%d/%Y %H:%M:%S', '%d-%m-%Y', '%d-%m-%Y %H:%M:%S'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def parse_numeric(value):
    """Parse numeric value, return 0 for invalid."""
    if pd.isna(value) or value is None:
        return 0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0


def _import_dataframe(df, source_name):
    """Import a DataFrame into the database. Returns (success, error_count, errors)."""
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    success_count = 0
    error_count = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            record = InvoiceBooking()
            record.source_file = source_name
            record.imported_at = datetime.utcnow()

            for excel_col, model_field in COLUMN_MAP.items():
                value = row.get(excel_col)

                if model_field in DATE_FIELDS:
                    value = parse_date(value)
                elif model_field in NUMERIC_FIELDS:
                    value = parse_numeric(value)
                else:
                    if pd.isna(value) or value is None:
                        value = None
                    else:
                        value = str(value).strip()

                setattr(record, model_field, value)

            db.session.add(record)
            success_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"Row {idx + 4}: {str(e)}")

    db.session.commit()

    return success_count, error_count, errors


def import_invoice_booking_excel(file_path, filename):
    """
    Import Invoice Booking data from an Excel file.
    Skips the first 3 rows, then reads the data using row 4 as header.
    Returns (success_count, error_count, errors).
    """
    df = pd.read_excel(file_path, skiprows=3, engine='openpyxl')
    return _import_dataframe(df, filename)


def extract_google_sheet_id(url):
    """Extract the spreadsheet ID from a Google Sheets URL."""
    # Matches /spreadsheets/d/SPREADSHEET_ID
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None


def import_invoice_booking_google_sheet(url):
    """
    Import Invoice Booking data from a public Google Sheets link.
    Downloads as xlsx, skips the first 3 rows, then imports.
    Returns (success_count, error_count, errors).
    """
    sheet_id = extract_google_sheet_id(url)
    if not sheet_id:
        raise ValueError('Invalid Google Sheets URL. Expected format: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/...')

    # Build the export URL for xlsx format
    export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'

    # Download to a temp file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.xlsx')
    try:
        urllib.request.urlretrieve(export_url, tmp_path)
        df = pd.read_excel(tmp_path, skiprows=3, engine='openpyxl')
        source_name = f'google-sheet:{sheet_id}'
        return _import_dataframe(df, source_name)
    finally:
        os.close(tmp_fd)
        os.unlink(tmp_path)
