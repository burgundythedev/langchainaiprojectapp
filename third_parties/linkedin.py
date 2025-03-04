import os
import requests
import json  # Import the json module for pretty-printing
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def clean_dict(d):
    """ Recursively remove empty values (None, "", [], {}, dicts with only count: 0) from a dictionary """
    if isinstance(d, dict):
        cleaned = {k: clean_dict(v) for k, v in d.items() if v not in [None, "", [], {}]}
        # Remove dicts that only have a 'Count' key with value 0
        if all(k.endswith("Count") and v == 0 for k, v in cleaned.items()):
            return None
        return cleaned if cleaned else None
    elif isinstance(d, list):
        return [clean_dict(v) for v in d if v not in [None, "", [], {}]]
    else:
        return d

def scrape_linkedin_profile(linkedin_profile_url: str, mock: bool = False):
    if mock:
        linkedin_profile_url = "https://gist.githubusercontent.com/burgundythedev/2776f755f7aead93109f18c5a7281af3/raw/967d46027ad19d7d6e6858708c8c38d19b46f91f/olivier-bourgogne-scrapin.json"
        response = requests.get(linkedin_profile_url, timeout=10)
        print(f"Mock Request Status Code: {response.status_code}")
        print(f"Mock Request Content: {response.text}")

    else:
        api_endpoint = "https://api.scrapin.io/enrichment/profile"
        params = {
            "apikey": os.environ["SCRAPIN_API_KEY"],
            "linkedInUrl": linkedin_profile_url,
        }
        try:
            response = requests.get(api_endpoint, params=params, timeout=10)
            response.raise_for_status()  # Raise error for bad responses

            # Pretty-print the raw JSON response for debugging
            print("Raw JSON Response:")
            print(json.dumps(response.json(), indent=2))

            data = response.json().get("person")

            if not data:
                print("No valid data found in response.")
                return None

            # Clean and filter data
            data = clean_dict(data)  # Remove empty values
            if not data:
                print("All data was empty after cleaning.")
                return None

            data = {k: v for k, v in data.items() if k not in ["certifications", "education", "experiences", "interests", "skills"]}

            return data
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching data: {e}")
            print(f"Response content: {response.text}")  # Debugging info
            return None
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return None

if __name__ == "__main__":
    linkedin_url = "https://www.linkedin.com/in/olivier-bourgogne/"
    profile_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_url)

    if profile_data:
        print("Cleaned and Filtered Data:")
        print(json.dumps(profile_data, indent=2))  # Pretty-print the final result
    else:
        print("Failed to fetch profile data.")