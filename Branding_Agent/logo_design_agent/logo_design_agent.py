import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

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
    Design a high-quality, professional, standalone logo for a company:
    - **Company Name**: {user_inputs['company_name']}
    - **Industry**: {user_inputs['industry']}
    - **Mission**: {user_inputs['mission_statement']}
    - **Preferred Style**: {user_inputs['preferred_style']}
    - **Primary Colors**: {user_inputs['main_color']}
    - **Icon/Shape Preferences**: {user_inputs['preferred_shapes']}
    - **Font Style**: {user_inputs['preferred_font_style']}
    - **Brand Tone**: {user_inputs['brand_tone']}
    - **Important Details**:
    1. Use a clean, modern, and sharp design with high contrast and clarity.
    2. Incorporate unique iconography that reflects the company’s mission.
    3. Ensure balance and alignment for a professional, polished appearance.
    4. Avoid excessive details—focus on minimalism while maintaining a creative flair.
    5. The logo should look scalable and usable on digital platforms and print.

    Create a logo that communicates innovation, professionalism, and trust.
    """

    try:
        print("\n⏳ Generating logo designs, please wait...\n")
        
        # Generate image using OpenAI's image generation API
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,  # Request 3 variations
        )

        image_url = response.data[0].url
        print("\n✅ Logo has been successfully generated.")
        print(f"\n🌐 Image URL: {image_url}")

        # Create folder "logos" if it doesn't exist
        folder_path = "logos"
        os.makedirs(folder_path, exist_ok=True)

        # Save image URL to a file named after the company name
        file_name = f"{user_inputs['company_name'].replace(' ', '_')}_logo_url.txt"
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "w") as file:
            file.write(image_url)

        print(f"\n📁 Logo image URL saved to '{file_path}'.")

    except Exception as e:
        print(f"\n❌ Error generating logo: {e}")



def save_to_memory(user_inputs):
    """
    Saves user inputs to a JSON file for memory.

    Args:
        user_inputs (dict): A dictionary of user inputs.

    Returns:
        str: Path to the saved JSON file.
    """
    company_name = user_inputs.get("company_name", "Unknown_Company").replace(" ", "_")
    memory_file = f"{company_name}_memory.json"

    with open(memory_file, "w") as file:
        json.dump(user_inputs, file, indent=4)

    print(f"\n📁 User inputs saved to memory: {memory_file}")
    return memory_file


def main():
    """Main function to interactively collect user inputs and generate logos."""
    print("\n💬 Welcome to the Logo Design Generator!\n")

    # Collect user inputs interactively
    print("Please provide the following details for your logo design:\n")
    company_name = input("THUTO: What is the name of your company?\nUser: ").strip()
    industry = input("THUTO: What industry does your company operate in?\nUser: ").strip()
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

    # Save to memory
    save_to_memory(user_inputs)

if __name__ == "__main__":
    main()
