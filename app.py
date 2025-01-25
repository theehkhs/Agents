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

#==========================================================================================================================================================================
# 1. Brand Agent

# 1.1 BrandGuidline Agent
def generate_brand_guidelines_content(data):
    """Generate structured brand guidelines content using OpenAI."""
    prompt = f"""
    Create comprehensive brand guidelines for {data['brandName']} with strict formatting:

    BRAND OVERVIEW:
    - Mission: {data['brandMission']}
    - Vision: {data['brandVision']}
    - Core Values: {data['brandValues']}

    Include these sections with exact formatting:
    
    SECTION: Brand Identity
    ** Logo Usage
    - Primary logo specifications
    - Clear space requirements
    - Minimum size limits
    - Incorrect usage examples
    
    SECTION: Visual Guidelines
    ** Color Palette
    - Primary brand colors (HEX/RGB/CMYK)
    - Secondary colors
    - Color combinations
    ** Typography
    - Primary typeface
    - Secondary typeface
    - Heading styles
    - Body text styles
    
    SECTION: Tone of Voice
    ** Brand Personality
    - Key characteristics
    - Communication style
    ** Messaging
    - Tagline usage
    - Value propositions
    - Customer communication
    
    SECTION: Brand Application
    ** Digital
    - Website guidelines
    - Social media rules
    ** Print
    - Business card specs
    - Letterhead design
    ** Environmental
    - Signage standards
    - Packaging design
    
    SECTION: Governance
    ** Approval Process
    - Asset request workflow
    - Review timeline
    ** Compliance
    - Monitoring process
    - Violation reporting

    Formatting rules:
    - Use SECTION: for main headers
    - Use ** ** for subheaders
    - Use - for bullet points
    - Empty line between paragraphs
    - No markdown formatting
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API Error: {str(e)}")

def create_pdf(content, brand_name):
    """Create professionally formatted PDF with enhanced styling"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=40
    )

    # Custom styles
    styles = getSampleStyleSheet()
    
    # Title Page Style
    styles.add(ParagraphStyle(
        name='TitlePage',
        parent=styles['Title'],
        fontSize=28,
        leading=32,
        spaceAfter=20,
        alignment=1,
        textColor='#2B3856',
        fontName='Helvetica-Bold'
    ))
    
    # Section Header
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor='#2B3856',
        spaceBefore=30,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    ))
    
    # Subsection Header
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor='#4F628E',
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    # Body Text
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        spaceAfter=8,
        textColor='#333333'
    ))
    
    # Bullet Style
    styles.add(ParagraphStyle(
        name='BulletText',
        parent=styles['BodyText'],
        firstLineIndent=-12,
        leftIndent=12,
        bulletIndent=0,
        spaceBefore=4
    ))

    elements = []
    
    # Title Page
    elements.append(Paragraph(brand_name, styles['TitlePage']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Brand Guidelines", styles['TitlePage']))
    elements.append(Spacer(1, inch))
    elements.append(Paragraph(f"Effective Date: {datetime.now().strftime('%B %d, %Y')}", styles['BodyText']))
    elements.append(PageBreak())
    
    # Process Content
    sections = content.split("SECTION:")[1:]  # Skip empty first element
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        section_title = lines[0].strip()
        
        # Add section header
        elements.append(Paragraph(section_title, styles['SectionHeader']))
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Handle subsections
            if line.startswith("**"):
                subsection = line.strip('*').strip()
                elements.append(Paragraph(subsection, styles['SubsectionHeader']))
            # Handle bullet points
            elif line.startswith("- "):
                elements.append(Paragraph(
                    f"<bullet>&bull;</bullet> {line[2:]}", 
                    styles['BulletText']
                ))
            # Handle regular paragraphs
            else:
                elements.append(Paragraph(line, styles['BodyText']))
        
        elements.append(Spacer(1, 15))
        elements.append(PageBreak())

    # Footer with page numbers
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(40, 30, f"{brand_name} Brand Guidelines")
        canvas.drawRightString(letter[0]-40, 30, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer

@app.route('/api/generate-brand-guidelines', methods=['POST'])
def generate_brand_guidelines():
    """Endpoint to generate brand guidelines PDF"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['brandName', 'brandMission', 'brandVision', 'brandValues']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Generate content
        guidelines_content = generate_brand_guidelines_content(data)
        
        # Create PDF
        pdf_buffer = create_pdf(guidelines_content, data['brandName'])
        
        # Return PDF
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{data['brandName'].replace(' ', '_')}_Brand_Guidelines.pdf"
        )

    except Exception as e:
        app.logger.error(f"Generation Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# 1.2 Logo Designer Agent
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
# 2. Business Agent

# 2.1 Business Plan
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
            model="gpt-3.5-turbo",
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


# 2.2 Pitch Plan
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
            model="gpt-3.5-turbo",
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

#==========================================================================================================================================================================
# 3. Lawyer Agent

# 3.1 Contract Generator
def generate_contract_content(data):
    """Generate professional legal contract content using OpenAI"""
    print("\n[DEBUG] Starting contract content generation")
    print(f"[DEBUG] Received data: {data}")
    
    prompt = f"""
    Create a comprehensive legal contract document with strict formatting:

    PARTIES:
    First Party: {data['firstPartyName']}
    Address: {data['firstPartyAddress']}
    Contact: {data['firstPartyContact']}

    Second Party: {data['secondPartyName']}
    Address: {data['secondPartyAddress']}
    Contact: {data['secondPartyContact']}

    TERMS:
    Effective Date: {data['effectiveDate']}
    Jurisdiction: {data['jurisdiction']}
    Contract Title: {data['contractTitle']}

    STRUCTURE THE DOCUMENT WITH THESE SECTIONS:

    SECTION: Purpose & Scope
    ** Contract Purpose
    - Detailed description of agreement purpose
    - Business objectives
    ** Scope of Work
    - Clear boundaries of work
    - Included/excluded services

    SECTION: Terms & Obligations
    ** First Party Responsibilities
    - Key obligations
    - Performance expectations
    ** Second Party Responsibilities
    - Key obligations
    - Delivery requirements

    SECTION: Financial Provisions
    ** Payment Terms
    - Payment schedule
    - Late payment penalties
    - Accepted payment methods
    ** Taxes & Fees
    - Responsibility allocation
    - Reporting requirements

    SECTION: Legal Clauses
    ** Confidentiality
    - Definition of confidential information
    - Non-disclosure obligations
    ** Termination
    - Conditions for termination
    - Notice requirements
    ** Dispute Resolution
    - Mediation/arbitration process
    - Governing law reference

    SECTION: General Provisions
    ** Amendments
    - Process for making changes
    - Required approvals
    ** Entire Agreement
    - Supersedes prior agreements
    - Modification requirements

    FORMATTING RULES:
    - Use SECTION: for main headers
    - Use ** ** for subheaders
    - Use - for bullet points
    - Include relevant legal terminology
    - Maintain professional contract structure
    """

    try:
        print("[DEBUG] Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4000
        )
        print("[DEBUG] Received response from OpenAI API")
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenAI API Error: {str(e)}")
        raise Exception(f"OpenAI API Error: {str(e)}")

def create_contract_pdf(content, contract_title):
    """Create professional contract PDF with legal formatting"""
    print("\n[DEBUG] Starting PDF creation")
    print(f"[DEBUG] Contract title: {contract_title}")
    print(f"[DEBUG] Content length: {len(content)} characters")
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=60,
            bottomMargin=40
        )

        # Get default styles
        styles = getSampleStyleSheet()
        
        # Modify existing styles instead of creating new ones
        styles['Title'].fontSize = 22
        styles['Title'].leading = 26
        styles['Title'].alignment = 1
        styles['Title'].textColor = '#2B3856'
        styles['Title'].spaceAfter = 20

        # Create new style names that don't conflict with defaults
        styles.add(ParagraphStyle(
            name='ContractSectionHeader',
            parent=styles['Heading1'],
            fontSize=14,
            leading=18,
            textColor='#2B3856',
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='ContractSubsectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor='#4F628E',
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Modify existing BodyText style instead of redefining
        styles['BodyText'].fontSize = 10
        styles['BodyText'].leading = 13
        styles['BodyText'].spaceAfter = 10
        styles['BodyText'].textColor = '#333333'

        elements = []
        
        # Title Page (using modified Title style)
        elements.append(Paragraph("CONTRACT AGREEMENT", styles['Title']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(contract_title, styles['Title']))
        elements.append(PageBreak())
        
        # Process Content
        sections = content.split("SECTION:")[1:]  # Skip empty first element
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            section_title = lines[0].strip()
            
            elements.append(Paragraph(section_title, styles['ContractSectionHeader']))
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("**"):
                    subsection = line.strip('*').strip()
                    elements.append(Paragraph(subsection, styles['ContractSubsectionHeader']))
                elif line.startswith("- "):
                    elements.append(Paragraph(
                        f"<bullet>&bull;</bullet> {line[2:]}", 
                        styles['BodyText']
                    ))
                else:
                    elements.append(Paragraph(line, styles['BodyText']))
            
            elements.append(PageBreak())

        # Add signature blocks
        elements.append(Paragraph("IN WITNESS WHEREOF", styles['ContractSectionHeader']))
        elements.append(Spacer(1, 40))
        elements.append(Paragraph(
            f"_________________________<br/>First Party Signature<br/>{contract_title}",
            styles['BodyText']
        ))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            f"_________________________<br/>Second Party Signature<br/>{contract_title}",
            styles['BodyText']
        ))

        # Footer with page numbers
        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            canvas.drawString(40, 30, f"{contract_title} - Confidential")
            canvas.drawRightString(letter[0]-40, 30, f"Page {doc.page}")
            canvas.restoreState()

        print("[DEBUG] Building PDF document")
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        buffer.seek(0)
        
        # Verify PDF content
        pdf_content = buffer.getvalue()
        if not pdf_content.startswith(b'%PDF'):
            print("[ERROR] Invalid PDF content generated")
            raise Exception("Failed to generate valid PDF content")
            
        print("[DEBUG] PDF created successfully")
        return buffer
    except Exception as e:
        print(f"[ERROR] PDF creation failed: {str(e)}")
        raise
@app.route('/api/generate-contract', methods=['POST'])
def generate_contract():
    """Endpoint to generate legal contract PDF"""
    print("\n[DEBUG] Received request to generate contract")
    try:
        data = request.json
        print(f"[DEBUG] Request data: {data}")
        
        # Validate required fields
        required_fields = [
            'firstPartyName', 'firstPartyAddress', 'secondPartyName', 'secondPartyAddress',
            'contractTitle', 'effectiveDate', 'jurisdiction'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            print(f"[ERROR] {error_msg}")
            return jsonify({'error': error_msg}), 400

        # Generate contract content
        print("[DEBUG] Generating contract content")
        contract_content = generate_contract_content(data)
        print("[DEBUG] Contract content generated successfully")
        
        # Create PDF
        print("[DEBUG] Creating PDF")
        pdf_buffer = create_contract_pdf(contract_content, data['contractTitle'])
        print("[DEBUG] PDF created successfully")
        
        # Return PDF
        filename = f"{data['contractTitle'].replace(' ', '_')}_Contract.pdf"
        print(f"[DEBUG] Returning PDF with filename: {filename}")
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        import traceback
        print(f"[ERROR] Exception occurred: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    
# 3.2 NDA Generator 
def generate_nda_content(data):
    """Generate professional NDA content using OpenAI"""
    prompt = f"""
    Create a comprehensive Non-Disclosure Agreement (NDA) with strict formatting:

    PARTIES:
    Disclosing Party: {data['disclosingPartyName']}
    Address: {data['disclosingPartyAddress']}
    Contact: {data['disclosingPartyContact']}

    Receiving Party: {data['receivingPartyName']}
    Address: {data['receivingPartyAddress']}
    Contact: {data['receivingPartyContact']}

    CORE DETAILS:
    Effective Date: {data['effectiveDate']}
    Duration: {data['duration']}
    Purpose: {data['purpose']}
    Jurisdiction: {data['jurisdiction']}

    STRUCTURE THE NDA WITH THESE SECTIONS:

    SECTION: Confidential Information Definition
    ** Scope of Confidential Information
    - Precise definition
    - Types of protected information
    ** Exclusions
    - Information not considered confidential

    SECTION: Obligations of Receiving Party
    ** Confidentiality Commitments
    - Protection standards
    - Non-disclosure requirements
    ** Permitted Disclosures
    - Exceptions to confidentiality
    - Legal or regulatory requirements

    SECTION: Use and Protection
    ** Permitted Uses
    - Specific allowed purposes
    - Limitations on use
    ** Security Measures
    - Required protection standards
    - Access restrictions

    SECTION: Term and Termination
    ** Agreement Duration
    - Effective period
    - Renewal conditions
    ** Post-Termination Obligations
    - Information return/destruction
    - Continuing confidentiality

    SECTION: Legal Provisions
    ** Remedies
    - Breach consequences
    - Injunctive relief
    ** Dispute Resolution
    - Mediation/arbitration process
    - Governing law

    FORMATTING RULES:
    - Use SECTION: for main headers
    - Use ** ** for subheaders
    - Use - for bullet points
    - Include precise legal terminology
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API Error: {str(e)}")

def create_nda_pdf(content, nda_title):
    """Create professional NDA PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )

    # Styles (similar to contract PDF creation)
    styles = getSampleStyleSheet()
    styles['Title'].fontSize = 22
    styles['Title'].alignment = 1
    
    styles.add(ParagraphStyle(
        name='NDASectionHeader',
        parent=styles['Heading1'],
        fontSize=14,
        textColor='#2B3856',
        spaceBefore=20,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='NDASubsectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='#4F628E',
        spaceBefore=15,
        spaceAfter=8
    ))
    
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 13

    elements = []
    
    # Title Page
    elements.append(Paragraph("NON-DISCLOSURE AGREEMENT", styles['Title']))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(nda_title, styles['Title']))
    elements.append(PageBreak())
    
    # Process Content
    sections = content.split("SECTION:")[1:]
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        section_title = lines[0].strip()
        
        elements.append(Paragraph(section_title, styles['NDASectionHeader']))
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("**"):
                subsection = line.strip('*').strip()
                elements.append(Paragraph(subsection, styles['NDASubsectionHeader']))
            elif line.startswith("- "):
                elements.append(Paragraph(
                    f"<bullet>&bull;</bullet> {line[2:]}", 
                    styles['BodyText']
                ))
            else:
                elements.append(Paragraph(line, styles['BodyText']))
        
        elements.append(PageBreak())

    # Signature Blocks
    elements.append(Paragraph("SIGNATURES", styles['NDASectionHeader']))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(
        "_________________________<br/>Disclosing Party Signature<br/>Date: ________________",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "_________________________<br/>Receiving Party Signature<br/>Date: ________________",
        styles['BodyText']
    ))

    # Footer with page numbers
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(40, 30, f"{nda_title} - Confidential")
        canvas.drawRightString(letter[0]-40, 30, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer

@app.route('/api/generate-nda', methods=['POST'])
def generate_nda():
    """Endpoint to generate NDA PDF"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = [
            'disclosingPartyName', 'disclosingPartyAddress', 'disclosingPartyContact',
            'receivingPartyName', 'receivingPartyAddress', 'receivingPartyContact',
            'effectiveDate', 'duration', 'purpose', 'jurisdiction'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Generate NDA content
        nda_content = generate_nda_content(data)
        
        # Create PDF
        pdf_buffer = create_nda_pdf(nda_content, "Non-Disclosure Agreement")
        
        # Return PDF
        filename = "Non_Disclosure_Agreement.pdf"
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=5000)