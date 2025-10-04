# Secure Software Systems - Assignment 3

## Running the Application

### Using Docker Compose (Recommended for Full Environment)

This setup runs the Flask app, MySQL database, and nginx WAF in containers.

1. Ensure Docker Desktop is installed and running.
2. Build and start the services:
   ```
   docker-compose up --build
   ```
3. Access the app at `http://localhost`.
4. To stop the services:
   ```
   docker-compose down
   ```

**Default Credentials:**
- Admin: `admin` / `admin123`
- Voter: `voter1` / `password123`

### Local Development with Python

For quick testing or development, you can run the app locally using SQLite.

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the demo:
   ```
   python run_demo.py
   ```
3. Access the app at `http://127.0.0.1:5000`.

**Note:** If you encounter database errors (e.g., "no such table" or schema mismatches), the local SQLite database (`instance/app.db`) may be out of sync. Delete the `instance` folder and rerun to recreate the database with the latest schema.

**Default Credentials:** Same as Docker setup above.