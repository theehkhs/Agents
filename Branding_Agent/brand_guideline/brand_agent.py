import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_streamed_guidelines(user_inputs):
    """
    Streams professional brand guidelines based on user inputs.

    Args:
        user_inputs (dict): A dictionary containing user input values such as company name,
                           industry, target audience, and more.

    Returns:
        None
    """
    prompt = f"""
    You are an expert branding consultant. Generate professional brand guidelines based on the following inputs:
    {user_inputs}
    Include sections like mission, vision, typography, color palette, logo usage, and brand voice.
    """

    client = OpenAI()
    output = ""

    try:
        # Stream the response
        print("\nLoading brand guidelines, please wait...\n")
        stream = client.chat.completions.create(
            model="gpt-4",  # Adjust the model as needed
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # Append streamed chunks to output
        for chunk in stream:
            content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, 'content') else ""
            if content is None:
                content = ""
            output += content

        print("\n\nAll brand guidelines have been successfully loaded.")

        # Save the output to a text file
        company_name = user_inputs.get("company_name", "Unknown_Company").replace(" ", "_")
        filename = f"{company_name}_Brand_Guidelines.txt"

        with open(filename, "w", encoding='utf-8') as file:
            file.write(output)

        print(f"\nBrand guidelines saved to: {filename}")
        print("\nFile has been successfully uploaded.")

    except Exception as e:
        print(f"\nError streaming brand guidelines: {e}")

def main():
    """Main function to interactively collect user inputs and generate brand guidelines."""
    print("\nWelcome to the Brand Guidelines Generator!\n")

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

    # Stream brand guidelines
    generate_streamed_guidelines(user_inputs)

if __name__ == "__main__":
    main()