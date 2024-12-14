"""This script generates brand guidelines documents for users by collecting their 
brand details (name, tone of voice, colors, typography, logo usage, etc.) and 
using OpenAI's API to create a professional and cohesive brand guidelines document."""

import openai
import os

# Set up OpenAI API key
openai.api_key = "your_openai_api_key"

def get_user_inputs():
    """Prompt the user for brand information."""
    print("\n✨ Welcome to the Brand Guidelines Generator! ✨\n")
    brand_name = input("📛 Enter your brand name: ")
    tagline = input("🎯 Enter your brand's tagline or slogan: ")
    tone_of_voice = input("🗣️ Describe the tone of voice for your brand (e.g., friendly, professional, fun): ")
    primary_colors = input("🎨 Enter your brand's primary colors (e.g., Red, Blue, Green): ")
    typography_style = input("🔤 Describe your typography style (e.g., modern, classic, bold): ")
    logo_usage_guidelines = input("📐 Describe how your logo should be used (e.g., spacing, placement, color variations): ")

    return {
        "brand_name": brand_name,
        "tagline": tagline,
        "tone_of_voice": tone_of_voice,
        "primary_colors": primary_colors,
        "typography_style": typography_style,
        "logo_usage_guidelines": logo_usage_guidelines,
    }

def generate_brand_guidelines(user_inputs):
    """Use OpenAI API to generate brand guidelines."""
    print("\n⏳ Generating your brand guidelines... Please wait...\n")
    prompt = (
        f"Generate a brand guidelines document based on the following information:\n"
        f"Brand Name: {user_inputs['brand_name']}\n"
        f"Tagline: {user_inputs['tagline']}\n"
        f"Tone of Voice: {user_inputs['tone_of_voice']}\n"
        f"Primary Colors: {user_inputs['primary_colors']}\n"
        f"Typography Style: {user_inputs['typography_style']}\n"
        f"Logo Usage Guidelines: {user_inputs['logo_usage_guidelines']}\n\n"
        f"The document should include sections on tone of voice, logo usage, typography, and color schemes."
    )

    response = openai.Completion.create(
        engine="text-davinci-003",  # Using the Davinci engine for better quality
        prompt=prompt,
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].text.strip()

def main():
    """Main function to run the script."""
    user_inputs = get_user_inputs()
    brand_guidelines = generate_brand_guidelines(user_inputs)
    print("\n🎉 Here are your brand guidelines: 🎉\n")
    print(brand_guidelines)

    # Optionally save to a file
    save_option = input("\n💾 Would you like to save the guidelines to a file? (yes/no): ").strip().lower()
    if save_option == "yes":
        filename = f"{user_inputs['brand_name'].replace(' ', '_')}_Brand_Guidelines.txt"
        with open(filename, "w") as file:
            file.write(brand_guidelines)
        print(f"✅ Brand guidelines saved as {filename}")

if __name__ == "__main__":
    main()
