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
        print("\n⏳ Loading brand guidelines, please wait...\n")
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

        print("\n\n✅ All brand guidelines have been successfully loaded.")

        # Save the output to a text file
        company_name = user_inputs.get("company_name", "Unknown_Company").replace(" ", "_")
        filename = f"{company_name}_Brand_Guidelines.txt"

        with open(filename, "w") as file:
            file.write(output)

        print(f"\n📁 Brand guidelines saved to: {filename}")
        print("\n✅ File has been successfully uploaded.")

    except Exception as e:
        print(f"\n❌ Error streaming brand guidelines: {e}")

def main():
    """Main function to interactively collect user inputs and generate brand guidelines."""
    print("\n💬 Welcome to the Brand Guidelines Generator!\n")

    # Collect user inputs interactively
    print("Please provide the following details about your company:\n")
    company_name = input("User: 1. What is the name of your company? \nTHUTO: ").strip()
    industry = input("User: 2. What industry does your company operate in? \nTHUTO: ").strip()
    target_audience = input("User: 3. Who is your target audience? \nTHUTO: ").strip()
    core_values = input("User: 4. What are your company's core values? (e.g., Innovation, Accessibility) \nTHUTO: ").strip()
    brand_tone = input("User: 5. How would you describe your brand's tone? (e.g., Professional, Friendly) \nTHUTO: ").strip()

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
