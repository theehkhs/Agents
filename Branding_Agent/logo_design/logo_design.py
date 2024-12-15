import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_logos(user_inputs):
    """
    Generates logo images using OpenAI's image generation API.

    Args:
        user_inputs (dict): A dictionary containing user input values such as company name,
                           industry, preferred style, and main color.

    Returns:
        None
    """
    client = OpenAI()

    prompt = f"""
    Create a visually stunning logo for the following company:
    Company Name: {user_inputs['company_name']}
    Industry: {user_inputs['industry']}
    Mission: {user_inputs['mission_statement']}
    Style: {user_inputs['preferred_style']}
    Color Palette: {user_inputs['main_color']}
    Shapes/Icons: {user_inputs['preferred_shapes']}
    Font Style: {user_inputs['preferred_font_style']}
    Brand Tone: {user_inputs['brand_tone']}
    Ensure the design reflects innovation and professionalism.
    """

    try:
        print("\n⏳ Generating logo designs, please wait...\n")
        
        # Generate image using OpenAI's image generation API
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        print("\n✅ Logo has been successfully generated.")
        print(f"\n🌐 Image URL: {image_url}")

        # Save image URL to a file
        with open("generated_logo_url.txt", "w") as file:
            file.write(image_url)

        print(f"\n📁 Logo image URL saved to 'generated_logo_url.txt'.")

    except Exception as e:
        print(f"\n❌ Error generating logo: {e}")

def main():
    """Main function to interactively collect user inputs and generate logos."""
    print("\n💬 Welcome to the Logo Design Generator!\n")

    # Collect user inputs interactively
    print("Please provide the following details for your logo design:\n")
    company_name = input("THUTO: What is the name of your company? (e.g., Mwanga Renewables, Thuto AI)\nUser: ").strip()
    industry = input("THUTO: What industry does your company operate in? (e.g., Renewable Energy, Technology)\nUser: ").strip()
    mission_statement = input("THUTO: What is your company’s mission or core purpose? (e.g., Empowering small businesses with AI, Making renewable energy accessible)\nUser: ").strip()
    preferred_style = input("THUTO: What style do you prefer for the logo? (e.g., Minimalistic, Bold, Playful)\nUser: ").strip()
    main_color = input("THUTO: What is the primary color or color palette for your logo? (e.g., Blue, Green, Pastel shades)\nUser: ").strip()
    preferred_shapes = input("THUTO: Are there any specific shapes or icons you’d like to include? (e.g., Circle, Triangle, Abstract patterns)\nUser: ").strip()
    preferred_font_style = input("THUTO: Do you have a preferred font style for the company name? (e.g., Serif, Sans-serif, Handwritten)\nUser: ").strip()
    brand_tone = input("THUTO: How would you describe your brand’s tone or personality? (e.g., Professional, Friendly, Innovative)\nUser: ").strip()

    # Organize inputs into a dictionary
    user_inputs = {
        "company_name": company_name,
        "industry": industry,
        "mission_statement": mission_statement,
        "preferred_style": preferred_style,
        "main_color": main_color,
        "preferred_shapes": preferred_shapes,
        "preferred_font_style": preferred_font_style,
        "brand_tone": brand_tone,
    }

    # Generate logos
    generate_logos(user_inputs)

if __name__ == "__main__":
    main()
