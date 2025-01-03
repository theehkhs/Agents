import base64
from flask import Flask, request, jsonify,request
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
load_dotenv()
CORS(app, supports_credentials=True)

client = OpenAI()

def generate_brand_guidelines(user_inputs):
    """
    Generates professional brand guidelines based on user inputs.
    
    Args:
        user_inputs (dict): Dictionary containing brand information
        
    Returns:
        str: Generated brand guidelines
    """
    prompt = f"""
    You are an expert branding consultant. Generate professional brand guidelines based on the following inputs:
    Company Name: {user_inputs.get('brandName')}
    Mission: {user_inputs.get('brandMission')}
    Vision: {user_inputs.get('brandVision')}
    Values: {user_inputs.get('brandValues')}
    
    Include sections like typography, color palette, logo usage, and brand voice.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

@app.route('/api/generate-guidelines', methods=['POST'])
def create_guidelines():
    """API endpoint to generate brand guidelines"""
    print("we are printing the value.")
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['brandName', 'brandMission', 'brandVision', 'brandValues']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400

        # Generate guidelines
        guidelines = generate_brand_guidelines(data)
        
        # Save to file
        filename = f"{data['brandName'].replace(' ', '_')}_Brand_Guidelines.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(guidelines)
            
        return jsonify({
            'success': True,
            'message': 'Brand guidelines generated successfully',
            'guidelines': guidelines,
            'filename': filename
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Brand guidelines service is running'
    })


# Logo Designer Agent
UPLOAD_FOLDER = 'generated_logos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_logo_prompt(data):
    return f"""
    Design a high-quality, professional, standalone logo for a company:
    - **Company Name**: {data.get('brandName')}
    - **Preferred Style**: {data.get('preferredStyle')}
    - **Primary Colors**: {data.get('colorScheme')}
    - **Icon/Shape Preferences**: {data.get('iconTheme')}
    - **Additional Details**: {data.get('additionalNotes')}
    
    Important Requirements:
    1. Use a clean, modern design with high contrast
    2. Ensure the logo is scalable and professional
    3. Focus on minimalism while maintaining creativity
    4. Make it suitable for both digital and print use
    """

def save_logo(image_url, brand_name):
    response = requests.get(image_url)
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{brand_name.replace(' ', '_')}_{timestamp}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    return None

@app.route('/api/generate-logo', methods=['POST'])
def generate_logo():
    try:
        data = request.json
        
        if not data.get('brandName'):
            return jsonify({'error': 'Brand name is required'}), 400

        prompt = generate_logo_prompt(data)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )

        image_url = response.data[0].url
        
        # Save the generated logo
        saved_path = save_logo(image_url, data['brandName'])
        
        if not saved_path:
            return jsonify({'error': 'Failed to save logo'}), 500

        return jsonify({
            'status': 'success',
            'message': 'Logo generated successfully',
            'image_url': image_url,
            'saved_path': saved_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-logo/<filename>', methods=['GET'])
def download_logo(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
            
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        return jsonify({
            'status': 'success',
            'image_data': image_data,
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)