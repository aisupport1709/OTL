from app import db
from datetime import datetime


class InvoiceBooking(db.Model):
    __tablename__ = 'invoice_booking'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    invoice_no = db.Column(db.String(100), index=True)
    invoice_date = db.Column(db.DateTime)
    revenue_date = db.Column(db.DateTime)
    month = db.Column(db.String(50))
    acc_code = db.Column(db.String(100))
    customer_name = db.Column(db.String(500), index=True)
    reference_id = db.Column(db.String(200))
    booking_code = db.Column(db.String(100), index=True)
    booking_master_desc = db.Column(db.String(500))
    booking_departure = db.Column(db.String(200))
    booking_category = db.Column(db.String(200))
    goods = db.Column(db.String(500))
    location_from = db.Column(db.String(200))
    location_to = db.Column(db.String(200))
    group_billing = db.Column(db.String(200))
    invoice_item_desc = db.Column(db.Text)
    remarks = db.Column(db.Text)
    currency = db.Column(db.String(10))
    quantity = db.Column(db.Float, default=0)
    unit_price = db.Column(db.Float, default=0)
    foreign_total = db.Column(db.Float, default=0)
    foreign_tax = db.Column(db.Float, default=0)
    foreign_total_with_tax = db.Column(db.Float, default=0)
    local_total = db.Column(db.Float, default=0)
    local_tax = db.Column(db.Float, default=0)
    local_total_with_tax = db.Column(db.Float, default=0)
    invoice_status = db.Column(db.String(50))
    last_modified_user = db.Column(db.String(200))
    last_modified_date_time = db.Column(db.DateTime)
    created_by = db.Column(db.String(200))
    created_date_time = db.Column(db.DateTime)
    actual_departure = db.Column(db.DateTime)
    actual_arrival = db.Column(db.DateTime)
    booking_requested_arrival = db.Column(db.DateTime)
    fast_invoice = db.Column(db.String(50))
    twb = db.Column(db.String(100))

    # Metadata
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    source_file = db.Column(db.String(500))

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_no': self.invoice_no,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'revenue_date': self.revenue_date.isoformat() if self.revenue_date else None,
            'month': self.month,
            'acc_code': self.acc_code,
            'customer_name': self.customer_name,
            'reference_id': self.reference_id,
            'booking_code': self.booking_code,
            'booking_master_desc': self.booking_master_desc,
            'booking_departure': self.booking_departure,
            'booking_category': self.booking_category,
            'goods': self.goods,
            'location_from': self.location_from,
            'location_to': self.location_to,
            'group_billing': self.group_billing,
            'invoice_item_desc': self.invoice_item_desc,
            'remarks': self.remarks,
            'currency': self.currency,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'foreign_total': self.foreign_total,
            'foreign_tax': self.foreign_tax,
            'foreign_total_with_tax': self.foreign_total_with_tax,
            'local_total': self.local_total,
            'local_tax': self.local_tax,
            'local_total_with_tax': self.local_total_with_tax,
            'invoice_status': self.invoice_status,
            'last_modified_user': self.last_modified_user,
            'last_modified_date_time': self.last_modified_date_time.isoformat() if self.last_modified_date_time else None,
            'created_by': self.created_by,
            'created_date_time': self.created_date_time.isoformat() if self.created_date_time else None,
            'actual_departure': self.actual_departure.isoformat() if self.actual_departure else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'booking_requested_arrival': self.booking_requested_arrival.isoformat() if self.booking_requested_arrival else None,
            'fast_invoice': self.fast_invoice,
            'twb': self.twb,
        }
