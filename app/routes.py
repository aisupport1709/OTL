import os
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func, extract
from app import db
from app.models.invoice_booking import InvoiceBooking
from app.models.app_setting import AppSetting
from app.services.excel_import import import_invoice_booking_excel, import_invoice_booking_google_sheet
from app.routes_auth import login_required

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Pages ───────────────────────────────────────────────────────────

@main_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/import')
@login_required
def import_page():
    return render_template('import.html')


@main_bp.route('/data')
@login_required
def data_page():
    return render_template('data.html')


@main_bp.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html')


# ─── API: Upload & Import ────────────────────────────────────────────

@api_bp.route('/upload/invoice-booking', methods=['POST'])
def upload_invoice_booking():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .xlsx and .xls files are allowed'}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    try:
        success, errors_count, error_details = import_invoice_booking_excel(filepath, filename)
        return jsonify({
            'message': f'Import completed: {success} records imported, {errors_count} errors',
            'success_count': success,
            'error_count': errors_count,
            'errors': error_details[:20],
        })
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}'}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@api_bp.route('/upload/invoice-booking-google', methods=['POST'])
def upload_invoice_booking_google():
    data = request.get_json()
    url = (data or {}).get('url', '').strip()

    if not url:
        return jsonify({'error': 'No Google Sheets URL provided'}), 400

    if 'docs.google.com/spreadsheets' not in url:
        return jsonify({'error': 'Invalid Google Sheets URL'}), 400

    try:
        success, errors_count, error_details = import_invoice_booking_google_sheet(url)
        return jsonify({
            'message': f'Import completed: {success} records imported, {errors_count} errors',
            'success_count': success,
            'error_count': errors_count,
            'errors': error_details[:20],
        })
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}'}), 500


# ─── API: Data ────────────────────────────────────────────────────────

@api_bp.route('/invoice-bookings', methods=['GET'])
def get_invoice_bookings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '').strip()

    query = InvoiceBooking.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                InvoiceBooking.invoice_no.ilike(like),
                InvoiceBooking.customer_name.ilike(like),
                InvoiceBooking.booking_code.ilike(like),
                InvoiceBooking.booking_master_desc.ilike(like),
            )
        )

    query = query.order_by(InvoiceBooking.invoice_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'data': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': per_page,
    })


@api_bp.route('/invoice-bookings/delete-all', methods=['DELETE'])
def delete_all_invoice_bookings():
    count = InvoiceBooking.query.delete()
    db.session.commit()
    return jsonify({'message': f'Deleted {count} records'})


# ─── Filters ─────────────────────────────────────────────────────────

def apply_filters(query):
    """Apply month and category (FTL/LTL) filters from query params."""
    month = request.args.get('month', '').strip()
    category = request.args.get('category', '').strip()  # 'FTL' or 'LTL'

    if month:
        query = query.filter(InvoiceBooking.month == month)
    if category:
        query = query.filter(InvoiceBooking.booking_category.ilike(f'%{category}%'))

    return query


def get_currency_columns():
    """
    Determine which columns to use based on ?currency= param.
    If currency matches local currency setting -> use local_total, local_tax, local_total_with_tax
    If a foreign currency is selected -> filter by that currency, use foreign_total, foreign_tax, foreign_total_with_tax
    Returns (total_col, tax_col, total_with_tax_col, is_foreign, currency_value).
    """
    currency = request.args.get('currency', '').strip().upper()
    local_ccy = AppSetting.get('local_currency', 'VND')

    if not currency or currency == local_ccy:
        return (InvoiceBooking.local_total, InvoiceBooking.local_tax,
                InvoiceBooking.local_total_with_tax, False, local_ccy)
    else:
        return (InvoiceBooking.foreign_total, InvoiceBooking.foreign_tax,
                InvoiceBooking.foreign_total_with_tax, True, currency)


def apply_currency_filter(query, is_foreign, currency_value):
    """If a foreign currency is selected, filter rows to only that currency."""
    if is_foreign:
        query = query.filter(InvoiceBooking.currency == currency_value)
    return query


# ─── API: Filter Options ─────────────────────────────────────────────

@api_bp.route('/filters/months', methods=['GET'])
def get_available_months():
    """Get distinct months available in the data."""
    results = db.session.query(
        InvoiceBooking.month
    ).distinct().order_by(InvoiceBooking.month).all()
    return jsonify([r.month for r in results if r.month])


@api_bp.route('/filters/categories', methods=['GET'])
def get_available_categories():
    """Get distinct booking categories available in the data."""
    results = db.session.query(
        InvoiceBooking.booking_category
    ).distinct().order_by(InvoiceBooking.booking_category).all()
    return jsonify([r.booking_category for r in results if r.booking_category])


# ─── API: KPIs & Charts ──────────────────────────────────────────────

@api_bp.route('/kpi/summary', methods=['GET'])
def kpi_summary():
    """Key KPIs for the dashboard. Supports ?month=&category=&currency= filters."""
    total_col, tax_col, total_with_tax_col, is_foreign, ccy = get_currency_columns()
    base = apply_currency_filter(apply_filters(db.session.query(InvoiceBooking)), is_foreign, ccy)

    total_invoices = base.with_entities(func.count(func.distinct(InvoiceBooking.invoice_no))).scalar() or 0
    total_revenue = base.with_entities(func.sum(total_col)).scalar() or 0
    total_revenue_with_tax = base.with_entities(func.sum(total_with_tax_col)).scalar() or 0
    total_tax = base.with_entities(func.sum(tax_col)).scalar() or 0
    total_customers = base.with_entities(func.count(func.distinct(InvoiceBooking.customer_name))).scalar() or 0
    total_bookings = base.with_entities(func.count(func.distinct(InvoiceBooking.booking_code))).scalar() or 0
    total_records = base.with_entities(func.count(InvoiceBooking.id)).scalar() or 0

    return jsonify({
        'total_invoices': total_invoices,
        'total_revenue': round(total_revenue, 2),
        'total_revenue_with_tax': round(total_revenue_with_tax, 2),
        'total_tax': round(total_tax, 2),
        'total_customers': total_customers,
        'total_bookings': total_bookings,
        'total_records': total_records,
    })


@api_bp.route('/kpi/revenue-by-month', methods=['GET'])
def revenue_by_month():
    """Revenue grouped by month field. Supports ?category=&currency= filters."""
    total_col, tax_col, total_with_tax_col, is_foreign, ccy = get_currency_columns()
    query = db.session.query(
        InvoiceBooking.month,
        func.sum(total_col).label('revenue'),
        func.sum(tax_col).label('tax'),
        func.count(InvoiceBooking.id).label('count'),
    )
    query = apply_currency_filter(query, is_foreign, ccy)
    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(InvoiceBooking.booking_category.ilike(f'%{category}%'))
    results = query.group_by(InvoiceBooking.month).order_by(InvoiceBooking.month).all()

    return jsonify([{
        'month': r.month,
        'revenue': round(r.revenue or 0, 2),
        'tax': round(r.tax or 0, 2),
        'count': r.count,
    } for r in results])


@api_bp.route('/kpi/top-customers', methods=['GET'])
def top_customers():
    """Top 10 customers by revenue. Supports ?month=&category=&currency= filters."""
    total_col, tax_col, total_with_tax_col, is_foreign, ccy = get_currency_columns()
    limit = request.args.get('limit', 10, type=int)
    query = apply_currency_filter(apply_filters(db.session.query(
        InvoiceBooking.customer_name,
        func.sum(total_col).label('revenue'),
        func.count(InvoiceBooking.id).label('count'),
    )), is_foreign, ccy)
    results = query.group_by(InvoiceBooking.customer_name).order_by(
        func.sum(total_col).desc()
    ).limit(limit).all()

    return jsonify([{
        'customer_name': r.customer_name,
        'revenue': round(r.revenue or 0, 2),
        'count': r.count,
    } for r in results])


@api_bp.route('/kpi/revenue-by-category', methods=['GET'])
def revenue_by_category():
    """Revenue by booking category. Supports ?month=&currency= filters."""
    total_col, tax_col, total_with_tax_col, is_foreign, ccy = get_currency_columns()
    query = db.session.query(
        InvoiceBooking.booking_category,
        func.sum(total_col).label('revenue'),
        func.count(InvoiceBooking.id).label('count'),
    )
    query = apply_currency_filter(query, is_foreign, ccy)
    month = request.args.get('month', '').strip()
    if month:
        query = query.filter(InvoiceBooking.month == month)
    results = query.group_by(InvoiceBooking.booking_category).order_by(
        func.sum(total_col).desc()
    ).all()

    return jsonify([{
        'category': r.booking_category or 'Uncategorized',
        'revenue': round(r.revenue or 0, 2),
        'count': r.count,
    } for r in results])


@api_bp.route('/kpi/revenue-by-location', methods=['GET'])
def revenue_by_location():
    """Top 10 routes by revenue. Supports ?month=&category=&currency= filters."""
    total_col, tax_col, total_with_tax_col, is_foreign, ccy = get_currency_columns()
    query = apply_currency_filter(apply_filters(db.session.query(
        InvoiceBooking.location_from,
        InvoiceBooking.location_to,
        func.sum(total_col).label('revenue'),
        func.count(InvoiceBooking.id).label('count'),
    )), is_foreign, ccy)
    results = query.group_by(
        InvoiceBooking.location_from, InvoiceBooking.location_to
    ).order_by(
        func.sum(total_col).desc()
    ).limit(10).all()

    return jsonify([{
        'route': f"{r.location_from or '?'} → {r.location_to or '?'}",
        'location_from': r.location_from,
        'location_to': r.location_to,
        'revenue': round(r.revenue or 0, 2),
        'count': r.count,
    } for r in results])


@api_bp.route('/kpi/ftl-ltl-comparison', methods=['GET'])
def ftl_ltl_comparison():
    """Compare FTL vs LTL revenue by month. Supports ?currency= filter."""
    total_col, tax_col, total_with_tax_col, is_foreign, ccy = get_currency_columns()
    month = request.args.get('month', '').strip()

    results = []
    for cat in ['FTL', 'LTL']:
        query = db.session.query(
            InvoiceBooking.month,
            func.sum(total_col).label('revenue'),
            func.sum(tax_col).label('tax'),
            func.count(InvoiceBooking.id).label('count'),
        ).filter(InvoiceBooking.booking_category.ilike(f'%{cat}%'))
        query = apply_currency_filter(query, is_foreign, ccy)
        if month:
            query = query.filter(InvoiceBooking.month == month)
        rows = query.group_by(InvoiceBooking.month).order_by(InvoiceBooking.month).all()
        for r in rows:
            results.append({
                'category': cat,
                'month': r.month,
                'revenue': round(r.revenue or 0, 2),
                'tax': round(r.tax or 0, 2),
                'count': r.count,
            })

    return jsonify(results)


@api_bp.route('/kpi/invoice-status', methods=['GET'])
def invoice_status_breakdown():
    """Invoice count by status. Supports ?month=&category= filters."""
    query = apply_filters(db.session.query(
        InvoiceBooking.invoice_status,
        func.count(InvoiceBooking.id).label('count'),
        func.sum(InvoiceBooking.local_total).label('revenue'),
    ))
    results = query.group_by(InvoiceBooking.invoice_status).all()

    return jsonify([{
        'status': r.invoice_status or 'Unknown',
        'count': r.count,
        'revenue': round(r.revenue or 0, 2),
    } for r in results])


@api_bp.route('/kpi/currency-breakdown', methods=['GET'])
def currency_breakdown():
    """Revenue by currency. Supports ?month=&category= filters."""
    query = apply_filters(db.session.query(
        InvoiceBooking.currency,
        func.sum(InvoiceBooking.foreign_total).label('foreign_total'),
        func.sum(InvoiceBooking.local_total).label('local_total'),
        func.count(InvoiceBooking.id).label('count'),
    ))
    results = query.group_by(InvoiceBooking.currency).order_by(
        func.sum(InvoiceBooking.local_total).desc()
    ).all()

    return jsonify([{
        'currency': r.currency or 'Unknown',
        'foreign_total': round(r.foreign_total or 0, 2),
        'local_total': round(r.local_total or 0, 2),
        'count': r.count,
    } for r in results])


# ─── API: Settings ──────────────────────────────────────────────────

@api_bp.route('/settings', methods=['GET'])
def get_settings():
    return jsonify({
        'local_currency': AppSetting.get('local_currency', 'VND'),
    })


@api_bp.route('/settings', methods=['PUT'])
def update_settings():
    data = request.get_json()
    if 'local_currency' in data:
        AppSetting.set('local_currency', data['local_currency'].strip().upper())
    return jsonify({
        'message': 'Settings updated',
        'local_currency': AppSetting.get('local_currency', 'VND'),
    })
