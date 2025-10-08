from flask import Blueprint, jsonify, request, render_template_string, current_app
from flask_login import login_required, current_user
from app.security import signing_service
import json

results = Blueprint('results', __name__)

# --- Mock Data Store ---
# In a real app, this would come from your database.
ELECTION_RESULTS = {
    "election_id": "FED2025",
    "results": {
        "PartyA": 5000000,
        "PartyB": 4500000,
        "PartyC": 1500000
    }
}
SIGNED_RESULTS = {
    "data": None,
    "signature": None
}

@results.route('/results/sign', methods=['POST'])
@login_required
def sign_election_results():
    """
    ADMIN-ONLY ENDPOINT.
    Signs the final election results and stores the signature.
    """
    # In a real app, you would add a check here to ensure current_user is an admin.
    # if not current_user.is_admin:
    #     return jsonify({"error": "Forbidden"}), 403

    # Convert results dictionary to a consistent JSON string (bytes)
    results_json = json.dumps(ELECTION_RESULTS, sort_keys=True, separators=(',', ':')).encode('utf-8')
    
    # Use the service to sign the data
    signature = signing_service.sign_data(results_json)
    
    # Store the signed data and signature (hex-encoded for easy transport)
    SIGNED_RESULTS['data'] = ELECTION_RESULTS
    SIGNED_RESULTS['signature'] = signature.hex()
    
    return jsonify({"status": "success", "message": "Results have been digitally signed."})


@results.route('/results/latest', methods=['GET'])
def get_latest_results():
    """
    PUBLIC ENDPOINT.
    Provides the latest signed election results for download.
    """
    if not SIGNED_RESULTS.get('signature'):
        return jsonify({"error": "Results have not been signed yet."}), 404
        
    return jsonify(SIGNED_RESULTS)


@results.route('/results/verify', methods=['POST'])
def verify_election_results():
    """
    PUBLIC ENDPOINT.
    Allows anyone to submit data and a signature to verify its authenticity.
    """
    data = request.json.get('data')
    signature_hex = request.json.get('signature')

    if not all([data, signature_hex]):
        return jsonify({"error": "Missing 'data' or 'signature' in request."}), 400

    # Convert incoming data to the same consistent format before verification
    data_bytes = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
    signature_bytes = bytes.fromhex(signature_hex)
    
    is_valid = signing_service.verify_signature(data_bytes, signature_bytes)
    
    return jsonify({
        "status": "Verification complete",
        "is_valid": is_valid
    })


