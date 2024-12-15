from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_html_landing_page(user_inputs):
    """
    Generates an HTML, CSS, and JavaScript landing page based on user inputs.

    Args:
        user_inputs (dict): A dictionary containing user input values such as company name,
                           industry, target audience, and more.

    Returns:
        None
    """
    html_prompt = f"""
    You are a skilled web developer. Generate the following components for a professional landing page based on these inputs:

    Company Name: {user_inputs['company_name']}
    Industry: {user_inputs['industry']}
    Target Audience: {user_inputs['target_audience']}
    Core Values: {user_inputs['core_values']}
    Brand Tone: {user_inputs['brand_tone']}

    1. HTML structure for the landing page (including sections for hero, about, services, and contact).
    2. CSS styles to make the page visually appealing and responsive.
    3. JavaScript to add interactivity (e.g., smooth scrolling, form validation).
    Ensure the HTML imports the CSS and JavaScript correctly.
    """

    client = OpenAI()  # Initialize the OpenAI client

    try:
        print("\n⏳ Generating landing page code, please wait...\n")

        # Generate the response from the AI
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": html_prompt}],
            stream=True,
        )

        output = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                output += chunk.choices[0].delta.content

        # Parse and save the HTML, CSS, and JavaScript
        company_name = user_inputs.get("company_name", "Unknown_Company").replace(" ", "_")

        html_file = f"{company_name}_landing_page.html"
        css_file = f"{company_name}_styles.css"
        js_file = f"{company_name}_scripts.js"

        # Separate the output into components and save them
        with open(html_file, "w") as file:
            file.write(output.split("<!-- CSS START -->")[0].strip())

        with open(css_file, "w") as file:
            file.write(output.split("<!-- CSS START -->")[1].split("<!-- CSS END -->")[0].strip())

        with open(js_file, "w") as file:
            file.write(output.split("<!-- JS START -->")[1].split("<!-- JS END -->")[0].strip())

        print(f"\n✅ Landing page files generated:\nHTML: {html_file}\nCSS: {css_file}\nJS: {js_file}")

    except Exception as e:
        print(f"\n❌ Error generating landing page: {e}")

def main():
    """Main function to interactively collect user inputs and generate a landing page."""
    print("\n💬 Welcome to the Landing Page Generator!\n")

    # Collect user inputs interactively
    print("Please provide the following details about your company:\n")
    company_name = input("THUTO: What is the name of your company? (e.g., Mwanga Renewables, Thuto AI)\nUser: ").strip()
    industry = input("THUTO: What industry does your company operate in? (e.g., Renewable Energy, Technology)\nUser: ").strip()
    target_audience = input("THUTO: Who is your target audience? (e.g., Homeowners, Small Businesses)\nUser: ").strip()
    core_values = input("THUTO: What are your company's core values? (e.g., Innovation, Accessibility, Sustainability)\nUser: ").strip()
    brand_tone = input("THUTO: How would you describe your brand's tone? (e.g., Professional, Friendly, Approachable)\nUser: ").strip()

    # Organize inputs into a dictionary
    user_inputs = {
        "company_name": company_name,
        "industry": industry,
        "target_audience": target_audience,
        "core_values": core_values,
        "brand_tone": brand_tone,
    }

    # Generate the landing page
    generate_html_landing_page(user_inputs)

if __name__ == "__main__":
    main()
