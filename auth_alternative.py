from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
# It's assumed your main app/__init__.py initializes 'db', so we don't need to import it here.

import os
import logging
import geoip2.database

# --- Blueprint Setup ---
auth = Blueprint('auth', __name__)
# updated the auth.py with addition of geoip2 as a Geolocation filter.
# --- GEO-FILTERING CONFIGURATION ---
# Best practice is to place the GeoLite2 database in the 'instance' folder, which is not committed to git.
# The path is relative to the application's root directory.
GEOIP_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'GeoLite2-Country.mmdb')

# Load allowed countries from an environment variable.
# The format should be a comma-separated list of ISO 3166-1 alpha-2 country codes (e.g., "AU,NZ,US").
# We provide a sensible default ('AU') for development if the variable is not set.
ALLOWED_COUNTRIES = os.getenv('ALLOWED_COUNTRIES', 'AU').split(',')

# --- LOGIN ROUTE ---
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 1. If user is already logged in, redirect them to the dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # 2. Get the user's real IP address, correctly handling proxies (like Nginx or a load balancer).
    # This is crucial for getting the true client IP in a production environment.
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # The X-Forwarded-For header can contain a comma-separated list of IPs. The first one is the original client.
        user_ip = forwarded_for.split(',')[0].strip()
    else:
        # Fallback to remote_addr if the header is not present.
        user_ip = request.remote_addr

    # 3. Perform the Geo-Filtering Check
    try:
        # Initialize the GeoIP database reader.
        reader = geoip2.database.Reader(GEOIP_DB_PATH)
        
        # Look up the country associated with the user's IP address.
        response = reader.country(user_ip)
        user_country_code = response.country.iso_code  # e.g., 'AU', 'US', 'GB'

        # Check if the user's country is in our list of allowed countries.
        if user_country_code not in ALLOWED_COUNTRIES:
            logging.warning(f"Geo-filter block: Denied login attempt from IP {user_ip} in country {user_country_code}.")
            flash('Access from your current region is not permitted.')
            return render_template('login.html'), 403 # Return a 403 Forbidden status code

    except geoip2.errors.AddressNotFoundError:
        # This error occurs for private or reserved IP ranges (e.g., 127.0.0.1, 192.168.x.x).
        # We can log this for information but should allow it for local development.
        logging.info(f"Login attempt from a local/private IP address: {user_ip}. Geo-check skipped.")
        pass # Allow the request to proceed
        
    except FileNotFoundError:
        # This is a critical server configuration error. The database file is missing.
        # For security, we should fail closed (deny access) if we cannot perform the check.
        logging.error(f"CRITICAL: GeoIP database not found at '{GEOIP_DB_PATH}'. Denying all login attempts.")
        flash('A server security configuration error occurred. Please contact an administrator.')
        return render_template('login.html'), 500 # Return a 500 Internal Server Error status code

    # 4. Handle the form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # Verify the user exists and the password is correct.
        if user and user.check_password(password):
            login_user(user)
            # Redirect to the page the user was trying to access, or the dashboard.
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            logging.warning(f"Failed login attempt for username: '{username}' from IP: {user_ip}")
            flash('Invalid username or password.')
    
    return render_template('login.html')

# --- LOGOUT ROUTE ---
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.')
    return redirect(url_for('auth.login'))
