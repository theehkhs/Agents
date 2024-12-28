from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
from flask_cors import CORS

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

if __name__ == '__main__':
    app.run(debug=True)