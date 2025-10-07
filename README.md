# Secure Software Systems - Assignment 3

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

   # or
   python -m pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python run_demo.py
   ```

3. **Access:** `http://localhost:5000`

**Credentials:**
- Admin: `admin` / `admin123`
- Voter: `voter1` / `password123`

## Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and adjust as needed.

Key variables:
- `SECRET_KEY`: Flask secret key for sessions (use a secure random key in production)
- `DATABASE_URL`: Database connection string (leave unset for SQLite in development, set for MySQL in Docker)
- `GEO_FILTER_ENABLED`: Enable/disable geo-filtering based on IP country (default: True)
- `ALLOWED_COUNTRIES`: Comma-separated list of allowed country codes (default: AU)
- `ALLOWED_IPS`: Comma-separated list of allowed IP addresses/ranges for authentication
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `ENABLE_MFA`: Enable/disable multi-factor authentication with OTP emails (default: False)
- `MAIL_SERVER`: SMTP server for sending OTP emails (default: smtp.gmail.com)
- `MAIL_PORT`: SMTP port for email server (default: 587)
- `MAIL_USE_TLS`: Use TLS encryption for email (default: True)
- `MAIL_USE_SSL`: Use SSL encryption for email (default: False)
- `MAIL_USERNAME`: Email account username for sending OTP emails
- `MAIL_PASSWORD`: Email account password/app password for sending OTP emails
- `MAIL_DEFAULT_SENDER`: Default sender email address (defaults to MAIL_USERNAME)

For geo-filtering to work, download the GeoLite2-Country.mmdb database from MaxMind and place it in the `data/` directory.

### OTP/MFA Setup

To enable multi-factor authentication with email-based OTP:

1. Set `ENABLE_MFA=True` in your `.env` file
2. Configure email settings:
   - `MAIL_USERNAME`: Your email address
   - `MAIL_PASSWORD`: Your email password or app-specific password
   - `MAIL_SERVER`: Your email provider's SMTP server (gmail.com, outlook.com, etc.)
   - `MAIL_PORT`: SMTP port (587 for TLS, 465 for SSL)

**Gmail example:**
```bash
# Windows
setx MAIL_USERNAME "youraccount@gmail.com"
setx MAIL_PASSWORD "your-app-password"
setx ENABLE_MFA "True"

# Linux/macOS
export MAIL_USERNAME="youraccount@gmail.com"
export MAIL_PASSWORD="your-app-password"
export ENABLE_MFA="True"
```

**Note:** For Gmail, use an "App Password" instead of your regular password. Enable 2FA first, then generate an app password in your Google Account settings.
## Docker Setup

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

2. **Access:** `http://localhost`

3. **Stop:**
   ```bash
   docker-compose down
   ```

**Credentials:** Same as local setup.

## Testing

1. **Install test dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests:**
   ```bash
   python run_tests.py
   ```

**Note:** All 13 smoke tests should pass.