import base64
from flask import Flask, request, jsonify,request, send_file
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
from flask_cors import CORS
import requests
from datetime import datetime
import pdfkit
from jinja2 import Template
import os
from datetime import datetime
# from weasyprint import HTML
import tempfile
from io import BytesIO

from flask import jsonify, request, send_file
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
import os
from datetime import datetime


app = Flask(__name__)
load_dotenv()
CORS(app, supports_credentials=True)

client = OpenAI()

# Brand Guidleine Agent
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

#==========================================================================================================================================================================

# Business Plan Agent
def generate_business_plan_content(data, client):
    """Generate detailed business plan content using OpenAI."""
    prompt = f"""
    Create a professional business plan based on the following information:
    
    COMPANY OVERVIEW:
    Business Name: {data['businessName']}
    Industry: {data['industryType']}
    Structure: {data['businessStructure']}
    Description: {data['companyDescription']}

    MARKET ANALYSIS:
    Target Market: {data['targetMarket']}
    Competitors: {data['competitors']}
    Market Size: {data['marketSize']}
    Market Trends: {data['marketTrends']}

    FINANCIAL PROJECTIONS:
    Startup Costs: {data['startupCosts']}
    Monthly Expenses: {data['monthlyExpenses']}
    Revenue Streams: {data['revenueStreams']}
    Break Even Analysis: {data['breakEvenPoint']}

    OPERATIONS:
    Location Strategy: {data['locationStrategy']}
    Equipment: {data['equipmentNeeded']}
    Staffing: {data['staffingRequirements']}
    Supply Chain: {data['supplyChain']}

    Format the business plan professionally with detailed sections, analysis, and recommendations.
    Include section headers with "SECTION:" prefix.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error generating business plan content: {str(e)}")

def create_pdf(content, business_name):
    """Create PDF using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=16
    ))
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12
    ))

    # Document content
    elements = []
    
    # Title
    elements.append(Paragraph(f"{business_name} - Business Plan", styles['CustomTitle']))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['CustomBody']))
    elements.append(Spacer(1, 30))

    # Process content
    sections = content.split("SECTION:")
    for section in sections:
        if section.strip():
            # Split into title and content
            parts = section.strip().split('\n', 1)
            if len(parts) == 2:
                title, content = parts
                elements.append(Paragraph(title.strip(), styles['CustomHeading']))
                elements.append(Paragraph(content.strip(), styles['CustomBody']))
                elements.append(Spacer(1, 20))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        f"Confidential Business Plan - {business_name}",
        styles['CustomBody']
    ))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/api/generate-business-plan', methods=['POST'])
def generate_business_plan():
    """Endpoint to generate business plan PDF."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = [
            'businessName', 'industryType', 'businessStructure', 'companyDescription',
            'targetMarket', 'competitors', 'marketSize', 'marketTrends',
            'startupCosts', 'monthlyExpenses', 'revenueStreams', 'breakEvenPoint',
            'locationStrategy', 'equipmentNeeded', 'staffingRequirements', 'supplyChain'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Generate business plan content using OpenAI
        plan_content = generate_business_plan_content(data, client)
        
        # Create PDF
        pdf_file = create_pdf(plan_content, data['businessName'])
        
        # Generate filename
        filename = f"{data['businessName'].replace(' ', '_')}_Business_Plan.pdf"
        
        # Send file
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


#==========================================================================================================================================================================
# Pitch Deck Agent
def generate_pitch_deck_content(data, client):
    """Generate detailed pitch deck content using OpenAI."""
    prompt = f"""
    Create a professional pitch deck based on the following information:
    
    PROBLEM & SOLUTION:
    Problem: {data['problem']}
    Solution: {data['solution']}
    Unique Value Proposition: {data['uniqueValueProposition']}
    Why Now: {data['whyNow']}

    MARKET & BUSINESS:
    Market Size: {data['marketSize']}
    Target Customers: {data['targetCustomers']}
    Business Model: {data['businessModel']}
    Revenue Streams: {data['revenueStreams']}

    TRACTION & COMPETITION:
    Key Metrics: {data['keyMetrics']}
    Competitors: {data['competitors']}
    Competitive Advantage: {data['competitiveAdvantage']}
    Current Traction: {data['currentTraction']}

    TEAM & FUNDING:
    Team Members: {data['teamMembers']}
    Advisors: {data['advisors']}
    Funding Needed: {data['fundingNeeded']}
    Use of Funds: {data['useOfFunds']}

    FINANCIALS & ROADMAP:
    Revenue Projections: {data['revenueProjections']}
    Marketing Strategy: {data['marketingStrategy']}
    Go-to-Market: {data['goToMarket']}
    Milestones: {data['milestones']}

    Format the pitch deck with compelling slides, focusing on visual appeal and investor relevance.
    Include section headers with "SLIDE:" prefix.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error generating pitch deck content: {str(e)}")

def create_pitch_deck_pdf(content, company_name):
    """Create PDF pitch deck using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    # Enhanced styles for pitch deck
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='SlideTitle',
        parent=styles['Title'],
        fontSize=28,
        spaceAfter=30,
        textColor=colors.HexColor('#2563EB')  # Blue color for titles
    ))
    styles.add(ParagraphStyle(
        name='SlideContent',
        parent=styles['Normal'],
        fontSize=18,
        spaceAfter=20,
        leading=24  # Line height
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray
    ))

    # Document content
    elements = []

    # Cover slide
    elements.append(Paragraph(company_name, styles['SlideTitle']))
    elements.append(Paragraph("Pitch Deck", styles['SlideContent']))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['SlideContent']))
    elements.append(PageBreak())

    # Process content
    slides = content.split("SLIDE:")
    for slide in slides[1:]:  # Skip empty first split
        if slide.strip():
            # Split into title and content
            parts = slide.strip().split('\n', 1)
            if len(parts) == 2:
                title, content = parts
                elements.append(Paragraph(title.strip(), styles['SlideTitle']))
                elements.append(Paragraph(content.strip(), styles['SlideContent']))
                elements.append(Paragraph(
                    f"{company_name} | Confidential",
                    styles['Footer']
                ))
                elements.append(PageBreak())

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/api/generate-pitch-deck', methods=['POST'])
def generate_pitch_deck():
    """Endpoint to generate pitch deck PDF."""
    try:
        data = request.json
        
        # Validate required fields based on the 5 sections
        required_fields = [
            'problem', 'solution', 'uniqueValueProposition', 'whyNow',
            'marketSize', 'targetCustomers', 'businessModel', 'revenueStreams',
            'keyMetrics', 'competitors', 'competitiveAdvantage', 'currentTraction',
            'teamMembers', 'advisors', 'fundingNeeded', 'useOfFunds',
            'revenueProjections', 'marketingStrategy', 'goToMarket', 'milestones'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Generate pitch deck content using OpenAI
        deck_content = generate_pitch_deck_content(data, client)
        
        # Create PDF
        company_name = data.get('companyName', 'Company')  # Fallback to 'Company' if name not provided
        pdf_file = create_pitch_deck_pdf(deck_content, company_name)
        
        # Generate filename
        filename = f"{company_name.replace(' ', '_')}_Pitch_Deck.pdf"
        
        # Send file
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True,port=5000)