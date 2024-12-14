import openai
from dotenv import load_dotenv

load_dotenv()

def generate_logos(user_inputs):
    """
    Generates three logo iterations as images using OpenAI's DALL·E model based on user inputs.

    Args:
        user_inputs (dict): A dictionary containing user input values such as company name,
                            industry, preferred style, and main color.

    Returns:
        None
    """
    prompt = f"""
    You are a professional logo designer. Create three distinct logo designs for a company with the following details:
    - Company Name: {user_inputs['company_name']}
    - Industry: {user_inputs['industry']}
    - Preferred Style: {user_inputs['preferred_style']}
    - Main Color: {user_inputs['main_color']}
    - Brand Tone: {user_inputs['brand_tone']}
    The logos should be minimalistic, modern, and visually appealing.
    """

    try:
        print("\n⏳ Generating logo designs, please wait...\n")
        
        # Generate 3 logo designs
        for i in range(1, 4):
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"  # Adjust size as needed
            )

            # Save the image to a file
            image_url = response['data'][0]['url']
            print(f"\n✅ Logo Iteration {i} generated: {image_url}")

    except Exception as e:
        print(f"\n❌ Error generating logo designs: {e}")

def main():
    """Main function to interactively collect user inputs and generate logos."""
    print("\n💬 Welcome to the Logo Design Generator!\n")

    # Collect user inputs interactively
    print("Please provide the following details for your logo design:\n")
    company_name = input("THUTO: What is the name of your company? (e.g., Mwanga Renewables, Thuto AI)\nUser: ").strip()
    industry = input("THUTO: What industry does your company operate in? (e.g., Renewable Energy, Technology)\nUser: ").strip()
    preferred_style = input("THUTO: What style do you prefer for the logo? (e.g., Minimalistic, Modern, Classic)\nUser: ").strip()
    main_color = input("THUTO: What is the main color for your logo? (e.g., Blue, Green, Red)\nUser: ").strip()
    brand_tone = input("THUTO: How would you describe your brand's tone? (e.g., Professional, Friendly, Approachable)\nUser: ").strip()

    # Organize inputs into a dictionary
    user_inputs = {
        "company_name": company_name,
        "industry": industry,
        "preferred_style": preferred_style,
        "main_color": main_color,
        "brand_tone": brand_tone,
    }

    # Generate logos
    generate_logos(user_inputs)

if __name__ == "__main__":
    main()
