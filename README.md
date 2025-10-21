# Affiliate Marketing Hub

A comprehensive affiliate marketing platform to manage all your affiliate links, partners, and earnings in one place.

## Features

### Core Functionality
- **Partner Management**: Add and manage multiple affiliate partners (Amazon, ShareASale, CJ, etc.)
- **Link Aggregation**: Centralize all your affiliate links from different platforms
- **Click Tracking**: Monitor clicks on your affiliate links
- **Transaction Management**: Track earnings, payouts, and pending commissions
- **Analytics Dashboard**: View comprehensive stats including:
  - Total clicks across all links
  - Amount collected (commissions earned)
  - Amount paid out
  - Pending amounts
  - Conversion rates
  - Top performing links

### User Interface
- Intuitive, modern design
- Easy navigation between Partners, Links, Transactions, and Dashboard
- Quick actions for common tasks
- Real-time data updates
- Responsive layout

## Technology Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM)
- SQLite database

**Frontend:**
- Vanilla JavaScript
- Modern CSS with responsive design
- No framework dependencies - lightweight and fast

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the repository**
   ```bash
   cd /home/user/bentomation
   ```

2. **Install dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the application**

   Option A - Use the startup script (recommended):
   ```bash
   ./start.sh
   ```

   Option B - Run directly:
   ```bash
   python3 app.py
   ```

5. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage Guide

### Adding Your First Partner

1. Click on **Partners** in the sidebar
2. Click **+ Add Partner** button
3. Fill in the partner details:
   - **Partner Name**: e.g., "Amazon Associates"
   - **Platform**: Select from dropdown or choose "Other"
   - **Username**: Your account username
   - **API Key/Secret**: (Optional) For future automatic link fetching

### Adding Affiliate Links

1. Navigate to **Affiliate Links**
2. Click **+ Add Link**
3. Enter link details:
   - **Partner**: Select the partner this link belongs to
   - **Brand Name**: e.g., "Nike"
   - **Product Name**: e.g., "Running Shoes"
   - **Affiliate URL**: Your tracking link
   - **Commission Rate**: Percentage you earn

### Tracking Transactions

1. Go to **Transactions**
2. Click **+ Add Transaction**
3. Record the sale:
   - **Link**: Which affiliate link generated this sale
   - **Amount Collected**: Commission earned
   - **Order ID**: Reference number from the platform
   - **Status**: Pending, Paid, or Cancelled

### Viewing Analytics

The **Dashboard** provides a comprehensive overview:
- Total partners and active links
- Cumulative clicks across all links
- Financial summary (collected, paid, pending)
- Top performing links by revenue
- Recent transaction history

## API Endpoints

### Partners
- `GET /api/partners` - List all partners
- `POST /api/partners` - Create new partner
- `GET /api/partners/{id}` - Get partner details
- `PUT /api/partners/{id}` - Update partner
- `DELETE /api/partners/{id}` - Delete partner

### Links
- `GET /api/links` - List all links (filterable by partner, status)
- `POST /api/links` - Create new link
- `GET /api/links/{id}` - Get link details
- `PUT /api/links/{id}` - Update link
- `DELETE /api/links/{id}` - Delete link
- `POST /api/links/{id}/click` - Track a click

### Transactions
- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create transaction
- `PUT /api/transactions/{id}` - Update transaction (mark as paid)

### Analytics
- `GET /api/analytics/overview` - Dashboard overview
- `GET /api/analytics/partner/{id}` - Partner-specific analytics

## Database Schema

### AffiliatePartner
- id, name, platform, api_key, api_secret, username, status, timestamps

### AffiliateLink
- id, partner_id, brand_name, product_name, affiliate_url, original_url, commission_rate, status, timestamps

### ClickEvent
- id, link_id, ip_address, user_agent, referrer, clicked_at

### Transaction
- id, link_id, order_id, amount_collected, amount_paid, currency, status, transaction_date, payout_date, notes

## Future Enhancements

### Platform Integrations
The application includes a placeholder endpoint for fetching links automatically from affiliate platforms:
- Amazon Associates API
- ShareASale API
- CJ Affiliate API
- Impact Radius API
- Rakuten API

To implement, add platform-specific API clients in the `fetch_partner_links()` function in app.py:362.

### Additional Features
- Email notifications for new transactions
- CSV export functionality
- Advanced filtering and search
- Charts and graphs for analytics
- Mobile app
- Multi-user support with authentication

## Development

### Project Structure
```
bentomation/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── static/               # Frontend files
│   ├── index.html       # Main HTML
│   ├── style.css        # Styles
│   └── app.js           # JavaScript
└── README.md            # This file
```

### Running in Development Mode
```bash
export FLASK_ENV=development
python3 app.py
```

### Running in Production
For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Notes

- API keys and secrets are stored in the database (consider encryption for production)
- No authentication is implemented (add user authentication for production)
- CORS is enabled for all origins (restrict in production)
- Use environment variables for sensitive configuration

## Contributing

This is a starter template. Feel free to extend it with:
- User authentication
- More detailed analytics
- Platform-specific integrations
- Export/import functionality
- Automated reporting

## License

Open source - use as you wish!

## Support

For issues or questions, please check the code comments or create an issue in the repository.
