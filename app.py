from flask import Flask, render_template, request, jsonify
from secure_info import SecureTicketSystem, TicketInfo
import os
import uuid
from datetime import datetime
import logging

app = Flask(__name__)
card_system = SecureTicketSystem()

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'static/qr_codes'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_ticket', methods=['POST'])
def generate_card():
    try:
        # Get form data
        card_info = TicketInfo(
            full_name=request.form['full_name'],
            email=request.form['email'],
            citizen_id=request.form['citizen_id'],
            birth_date=request.form['birth_date'],
            gender=request.form['gender'],
            district=request.form['district'],
            city=request.form['city'],
        )

        # Generate secure card with encryption
        card_data = card_system.create_secure_ticket(card_info)

        # Save QR code to static folder with a secure filename
        qr_filename = f"qr_{uuid.uuid4().hex}.png"
        qr_path = os.path.join(UPLOAD_FOLDER, qr_filename)
        os.rename(card_data['qr_code'], qr_path)

        # Decrypt public data for display
        public_info = card_system.decrypt_ticket_data(card_data['public_data'])

        # Store private data securely (simulate server-side storage)
        server_storage = {
            'ticket_id': qr_filename,
            'server_data': card_data['server_data']
        }
        logging.info(f"Card generated: {server_storage}")

        return render_template('ticket.html',
                               card_info=public_info,
                               qr_path=qr_path)

    except Exception as e:
        logging.error(f"Error generating card: {e}")
        return jsonify({'error': 'Failed to generate ticket.'}), 500


@app.route('/verify_card', methods=['POST'])
def verify_card():
    try:
        qr_data = request.form['qr_data']
        server_data = request.form['server_data']

        # Verify card authenticity
        is_valid = card_system.verify_ticket(qr_data, server_data)
        return jsonify({'valid': is_valid})

    except Exception as e:
        logging.error(f"Error verifying card: {e}")
        return jsonify({'error': 'Verification failed.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
