from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, AffiliatePartner, AffiliateLink, ClickEvent, Transaction
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///affiliate_marketing.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


# ==================== PARTNER MANAGEMENT ====================

@app.route('/api/partners', methods=['GET'])
def get_partners():
    """Get all affiliate partners"""
    partners = AffiliatePartner.query.all()
    return jsonify([partner.to_dict() for partner in partners])


@app.route('/api/partners/<int:partner_id>', methods=['GET'])
def get_partner(partner_id):
    """Get a specific partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    return jsonify(partner.to_dict())


@app.route('/api/partners', methods=['POST'])
def create_partner():
    """Create a new affiliate partner"""
    data = request.get_json()

    if not data.get('name') or not data.get('platform'):
        return jsonify({'error': 'Name and platform are required'}), 400

    partner = AffiliatePartner(
        name=data['name'],
        platform=data['platform'],
        api_key=data.get('api_key'),
        api_secret=data.get('api_secret'),
        username=data.get('username'),
        status=data.get('status', 'active')
    )

    db.session.add(partner)
    db.session.commit()

    return jsonify(partner.to_dict()), 201


@app.route('/api/partners/<int:partner_id>', methods=['PUT'])
def update_partner(partner_id):
    """Update an affiliate partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    data = request.get_json()

    if 'name' in data:
        partner.name = data['name']
    if 'platform' in data:
        partner.platform = data['platform']
    if 'api_key' in data:
        partner.api_key = data['api_key']
    if 'api_secret' in data:
        partner.api_secret = data['api_secret']
    if 'username' in data:
        partner.username = data['username']
    if 'status' in data:
        partner.status = data['status']

    partner.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(partner.to_dict())


@app.route('/api/partners/<int:partner_id>', methods=['DELETE'])
def delete_partner(partner_id):
    """Delete an affiliate partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)
    db.session.delete(partner)
    db.session.commit()

    return jsonify({'message': 'Partner deleted successfully'})


# ==================== LINK MANAGEMENT ====================

@app.route('/api/links', methods=['GET'])
def get_links():
    """Get all affiliate links with optional filtering"""
    partner_id = request.args.get('partner_id', type=int)
    status = request.args.get('status')

    query = AffiliateLink.query

    if partner_id:
        query = query.filter_by(partner_id=partner_id)
    if status:
        query = query.filter_by(status=status)

    links = query.all()
    return jsonify([link.to_dict() for link in links])


@app.route('/api/links/<int:link_id>', methods=['GET'])
def get_link(link_id):
    """Get a specific link"""
    link = AffiliateLink.query.get_or_404(link_id)
    return jsonify(link.to_dict())


@app.route('/api/links', methods=['POST'])
def create_link():
    """Create a new affiliate link"""
    data = request.get_json()

    if not data.get('partner_id') or not data.get('brand_name') or not data.get('affiliate_url'):
        return jsonify({'error': 'partner_id, brand_name, and affiliate_url are required'}), 400

    link = AffiliateLink(
        partner_id=data['partner_id'],
        brand_name=data['brand_name'],
        product_name=data.get('product_name'),
        affiliate_url=data['affiliate_url'],
        original_url=data.get('original_url'),
        commission_rate=data.get('commission_rate', 0.0),
        status=data.get('status', 'active')
    )

    db.session.add(link)
    db.session.commit()

    return jsonify(link.to_dict()), 201


@app.route('/api/links/<int:link_id>', methods=['PUT'])
def update_link(link_id):
    """Update an affiliate link"""
    link = AffiliateLink.query.get_or_404(link_id)
    data = request.get_json()

    if 'brand_name' in data:
        link.brand_name = data['brand_name']
    if 'product_name' in data:
        link.product_name = data['product_name']
    if 'affiliate_url' in data:
        link.affiliate_url = data['affiliate_url']
    if 'original_url' in data:
        link.original_url = data['original_url']
    if 'commission_rate' in data:
        link.commission_rate = data['commission_rate']
    if 'status' in data:
        link.status = data['status']

    link.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(link.to_dict())


@app.route('/api/links/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    """Delete an affiliate link"""
    link = AffiliateLink.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()

    return jsonify({'message': 'Link deleted successfully'})


# ==================== CLICK TRACKING ====================

@app.route('/api/links/<int:link_id>/click', methods=['POST'])
def track_click(link_id):
    """Track a click on an affiliate link"""
    link = AffiliateLink.query.get_or_404(link_id)

    click = ClickEvent(
        link_id=link_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        referrer=request.headers.get('Referer')
    )

    db.session.add(click)
    db.session.commit()

    return jsonify({
        'message': 'Click tracked',
        'redirect_url': link.affiliate_url
    })


# ==================== TRANSACTION MANAGEMENT ====================

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional filtering"""
    link_id = request.args.get('link_id', type=int)
    status = request.args.get('status')

    query = Transaction.query

    if link_id:
        query = query.filter_by(link_id=link_id)
    if status:
        query = query.filter_by(status=status)

    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    return jsonify([transaction.to_dict() for transaction in transactions])


@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    data = request.get_json()

    if not data.get('link_id') or not data.get('amount_collected'):
        return jsonify({'error': 'link_id and amount_collected are required'}), 400

    transaction = Transaction(
        link_id=data['link_id'],
        order_id=data.get('order_id'),
        amount_collected=data['amount_collected'],
        amount_paid=data.get('amount_paid', 0.0),
        currency=data.get('currency', 'USD'),
        status=data.get('status', 'pending'),
        notes=data.get('notes')
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify(transaction.to_dict()), 201


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update a transaction (e.g., mark as paid)"""
    transaction = Transaction.query.get_or_404(transaction_id)
    data = request.get_json()

    if 'amount_paid' in data:
        transaction.amount_paid = data['amount_paid']
    if 'status' in data:
        transaction.status = data['status']
        if data['status'] == 'paid' and not transaction.payout_date:
            transaction.payout_date = datetime.utcnow()
    if 'notes' in data:
        transaction.notes = data['notes']

    db.session.commit()

    return jsonify(transaction.to_dict())


# ==================== ANALYTICS & DASHBOARD ====================

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get overall analytics dashboard data"""

    # Total stats
    total_partners = AffiliatePartner.query.count()
    active_partners = AffiliatePartner.query.filter_by(status='active').count()
    total_links = AffiliateLink.query.count()
    active_links = AffiliateLink.query.filter_by(status='active').count()
    total_clicks = ClickEvent.query.count()

    # Financial stats
    all_transactions = Transaction.query.all()
    total_collected = sum(t.amount_collected for t in all_transactions)
    total_paid = sum(t.amount_paid for t in all_transactions if t.status == 'paid')
    pending_amount = sum(t.amount_collected for t in all_transactions if t.status == 'pending')

    # Recent activity
    recent_clicks = ClickEvent.query.order_by(ClickEvent.clicked_at.desc()).limit(10).all()
    recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(10).all()

    # Top performing links
    links = AffiliateLink.query.all()
    links_with_revenue = [
        {
            'link': link.to_dict(),
            'revenue': sum(t.amount_collected for t in link.transactions)
        }
        for link in links
    ]
    top_links = sorted(links_with_revenue, key=lambda x: x['revenue'], reverse=True)[:5]

    return jsonify({
        'overview': {
            'total_partners': total_partners,
            'active_partners': active_partners,
            'total_links': total_links,
            'active_links': active_links,
            'total_clicks': total_clicks,
            'total_collected': round(total_collected, 2),
            'total_paid': round(total_paid, 2),
            'pending_amount': round(pending_amount, 2),
            'conversion_rate': round((len(all_transactions) / total_clicks * 100), 2) if total_clicks > 0 else 0
        },
        'recent_clicks': [click.to_dict() for click in recent_clicks],
        'recent_transactions': [t.to_dict() for t in recent_transactions],
        'top_links': top_links
    })


@app.route('/api/analytics/partner/<int:partner_id>', methods=['GET'])
def get_partner_analytics(partner_id):
    """Get analytics for a specific partner"""
    partner = AffiliatePartner.query.get_or_404(partner_id)

    # Get all links for this partner
    links = partner.links
    total_clicks = sum(len(link.clicks) for link in links)

    # Financial stats
    all_transactions = []
    for link in links:
        all_transactions.extend(link.transactions)

    total_collected = sum(t.amount_collected for t in all_transactions)
    total_paid = sum(t.amount_paid for t in all_transactions if t.status == 'paid')
    pending_amount = sum(t.amount_collected for t in all_transactions if t.status == 'pending')

    return jsonify({
        'partner': partner.to_dict(),
        'stats': {
            'total_links': len(links),
            'active_links': len([l for l in links if l.status == 'active']),
            'total_clicks': total_clicks,
            'total_transactions': len(all_transactions),
            'total_collected': round(total_collected, 2),
            'total_paid': round(total_paid, 2),
            'pending_amount': round(pending_amount, 2),
            'conversion_rate': round((len(all_transactions) / total_clicks * 100), 2) if total_clicks > 0 else 0
        },
        'links': [link.to_dict() for link in links]
    })


# ==================== PLATFORM INTEGRATION (PLACEHOLDER) ====================

@app.route('/api/partners/<int:partner_id>/fetch-links', methods=['POST'])
def fetch_partner_links(partner_id):
    """
    Fetch active links from the partner's platform API.
    This is a placeholder - implementation depends on each platform's API.
    """
    partner = AffiliatePartner.query.get_or_404(partner_id)

    # TODO: Implement platform-specific API integrations
    # Examples:
    # - Amazon Associates API
    # - ShareASale API
    # - CJ Affiliate API
    # - Impact Radius API

    return jsonify({
        'message': 'Platform integration coming soon',
        'partner': partner.name,
        'platform': partner.platform,
        'note': 'This endpoint will fetch active links from the partner platform API'
    }), 501


# ==================== STATIC FILES & ROOT ====================

@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    print(f"🚀 Affiliate Marketing Platform running on http://localhost:{port}")
    app.run(debug=debug, port=port, host='0.0.0.0')
