from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AffiliatePartner(db.Model):
    """Represents an affiliate platform/partner (e.g., Amazon Associates, ShareASale)"""
    __tablename__ = 'affiliate_partners'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100), nullable=False)  # e.g., "Amazon", "ShareASale"
    api_key = db.Column(db.String(255))  # Encrypted API key
    api_secret = db.Column(db.String(255))  # Encrypted API secret
    username = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    links = db.relationship('AffiliateLink', backref='partner', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'platform': self.platform,
            'username': self.username,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_links': len(self.links),
            'active_links': len([link for link in self.links if link.status == 'active'])
        }


class AffiliateLink(db.Model):
    """Represents an individual affiliate link for a brand/product"""
    __tablename__ = 'affiliate_links'

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('affiliate_partners.id'), nullable=False)
    brand_name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(200))
    affiliate_url = db.Column(db.Text, nullable=False)
    original_url = db.Column(db.Text)
    commission_rate = db.Column(db.Float, default=0.0)  # Percentage
    status = db.Column(db.String(20), default='active')  # active, inactive, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clicks = db.relationship('ClickEvent', backref='link', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='link', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        total_clicks = len(self.clicks)
        total_collected = sum(t.amount_collected for t in self.transactions)
        total_paid = sum(t.amount_paid for t in self.transactions if t.status == 'paid')
        pending_amount = sum(t.amount_collected for t in self.transactions if t.status == 'pending')

        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'brand_name': self.brand_name,
            'product_name': self.product_name,
            'affiliate_url': self.affiliate_url,
            'original_url': self.original_url,
            'commission_rate': self.commission_rate,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'stats': {
                'total_clicks': total_clicks,
                'total_collected': round(total_collected, 2),
                'total_paid': round(total_paid, 2),
                'pending_amount': round(pending_amount, 2),
                'conversion_rate': round((len(self.transactions) / total_clicks * 100), 2) if total_clicks > 0 else 0
            }
        }


class ClickEvent(db.Model):
    """Tracks individual clicks on affiliate links"""
    __tablename__ = 'click_events'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('affiliate_links.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.Text)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'link_id': self.link_id,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None
        }


class Transaction(db.Model):
    """Represents a conversion/sale from an affiliate link"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('affiliate_links.id'), nullable=False)
    order_id = db.Column(db.String(100))  # External order ID from platform
    amount_collected = db.Column(db.Float, default=0.0)  # Commission earned
    amount_paid = db.Column(db.Float, default=0.0)  # Amount actually paid out
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    payout_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'link_id': self.link_id,
            'brand_name': self.link.brand_name if self.link else None,
            'order_id': self.order_id,
            'amount_collected': round(self.amount_collected, 2),
            'amount_paid': round(self.amount_paid, 2),
            'currency': self.currency,
            'status': self.status,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'payout_date': self.payout_date.isoformat() if self.payout_date else None,
            'notes': self.notes
        }
