from flask import Flask, jsonify, request
from cursor_signup_service import CursorSignupService
from logger import logging

app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        signup_service = CursorSignupService()
        result = signup_service.sign_up_account()
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': {
                    'email': result['email'],
                    'password': result['password'],
                    'token': result['token'],
                    'usage_limit': result['usage_limit']
                },
                'message': 'Account created successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 400
            
    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 