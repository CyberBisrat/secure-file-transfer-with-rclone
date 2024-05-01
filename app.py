from flask import Flask, Response, jsonify, request, send_file
import logging 
from rclone_python import rclone
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
from functools import wraps
import subprocess
import json


app = Flask(__name__)

def require_token(view_func):
    @wraps(view_func)
    def decorated(*args, **kwargs):
        # Get the token from the Authorization header
        token = request.headers.get('Authorization')
        
        # Check if the token is provided and has the correct format
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Invalid Authorization header format'}), 401
        
        # Extract the access token from the Authorization header
        token = token.split(' ', 1)[1]
        
        # Get the fixed token from the environment variable
        expected_token = os.environ.get('RCLONE_API_BEARER_TOKEN')
        
        # Compare the tokens

        if token != expected_token:
            return jsonify({'error': 'Invalid token'}), 401
        
        return view_func(*args, **kwargs)
    
    return decorated

@app.route('/upload_encrypted', methods=['POST']) 
@require_token
def upload_encrypted_data():
     try:
        data = request.get_json()  # Get JSON data from request body
        
        # Check if 'source' and 'destination' are present in the JSON payload
        if 'source' in data and 'destination' in data:
            src = data['source']
            dest_path = data['destination']  # Get the destination path from JSON payload
            
            # Construct the full destination path by appending to 'encrypted:'
            dest = f'encrypted:{dest_path}'
            
            logging.debug(f"Source Path is: {src}")
            logging.debug(f"Destination Path is: {dest}")
            
            result = rclone.copy(src, dest)
            
            if not result:
                logging.debug("Copy successful")
                return 'Encrypted Copy Complete!'
            else:
                error_message = "\n".join(result)
                logging.error("Copy failed: %s", error_message)
                return 'Failed to copy data.', 500
        else:
            return 'Invalid JSON payload. Please provide "source" and "destination" paths.', 400

     except Exception as e:
        logging.error("Exception occurred: %s", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/delete_file', methods=['POST'])  
@require_token
def delete_file():
    try:
        data = request.get_json()  
        
        if 'remote_path' in data:
            remote_path = data['remote_path']  # Get the remote path from JSON payload
            full_remote_path = f'encrypted:{remote_path}'
            
            try:
                rclone.delete(full_remote_path)
                logging.info('File "%s" deleted successfully.', full_remote_path)
                return jsonify({'message': f'File "{full_remote_path}" deleted successfully.'}), 200
            except Exception as e:
                logging.error('Failed to delete the file. Error: %s', str(e))
                return jsonify({'error': f'Failed to delete the file. Error: {str(e)}'}), 500
        else:
            return 'Invalid JSON payload. Please provide "remote_path" for the file to delete.', 400
        
    except Exception as e:
        logging.error("Exception occurred: %s", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/list_encrypted_files', methods=['GET'])
@require_token
def list_encrypted_synced_files():
    try:
        remote_dest = 'encrypted:'
        
        # Use subprocess to run the rclone command to list subdirectories recursively
        cmd = ['rclone', 'lsjson', remote_dest, '--recursive']
        result = subprocess.run(cmd, text=True, capture_output=True)

        # Check the return code to determine success or failure
        if result.returncode == 0:
            # Parse the JSON result
            file_info = json.loads(result.stdout)
            
            if len(file_info) > 0:
                # Extract only the file names, filtering out directories
                file_names = [item['Name'] for item in file_info if not item['IsDir']]
                
                return jsonify({'files': file_names})
            else:
                logging.error("Listing failed: No files found.")
                return jsonify({'error': 'Failed to list synced files. No files found.'}), 500
        else:
            # Handle the case where the rclone command failed
            logging.error("Rclone command failed with return code:", result.returncode)
            logging.error("Standard Error:", result.stderr)
            return jsonify({'error': 'Failed to list synced files. Rclone command failed.'}), 500
    except Exception as e:
        logging.error("Exception occurred: %s", str(e))
        return jsonify({'error': str(e)}), 500


    
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5002)

