import json
import re

region = None
user_profiles = None
ban_type = None

# Initialize an empty list to store filtered profiles
filtered_profiles = []

data_source = 'all_accounts_data.json'

def get_region():
    global region
    region = input("Enter the region you wish to check (eu, na, ap, etc.): ")
    if region != "eu" and region != "na" and region != "kr" and region != "ap" and region != "latam" and region != "br":
        print("Invalid region.")
        get_region()

def get_type():
    global ban_type
    ban_type = input("Enter the ban type you wish to check (unbanned / nonpermbanned / all): ")
    if  ban_type != "unbanned" and ban_type != "nonpermbanned" and ban_type != "all":
        print("Invalid ban type.")
        get_type()

def clean_data():
    with open(data_source, 'r') as infile:
        incorrect_json = infile.read()

    corrected_json = incorrect_json.strip()
    
    # Define the regular expression pattern to match the specific pattern `}\n]`
    pattern = r'}\n\]'

    # Check if the closing square bracket is not at the end of the text and fix it
    if corrected_json.strip().endswith('},'):
        modified_text = re.sub(pattern, '},', corrected_json)
        modified_text = modified_text.strip()[:-1] + '\n]'

        # Load the formatted JSON data
        data = json.loads(modified_text)

        # Write the corrected JSON data to a new JSON file
        with open(data_source, "w") as outfile:
            outfile.truncate(0)
            json.dump(data, outfile, indent=4)

def load_data():
    global user_profiles
    # Read user profiles from the JSON file
    with open(data_source, "r") as json_file:
        user_profiles = json.load(json_file)

def filter_profiles():
    # Loop through the user profiles and filter based on criteria
    for profile in user_profiles:
        if profile["Region"] == region:
            if ban_type == "unbanned" and profile["Ban_Status"] != "PERMANENT_BAN" and profile["Ban_Status"] != "PBE_LOGIN_TIME_BAN" and profile["Ban_Status"] != "TIME_BAN":
                filtered_profiles.append(profile)
            elif ban_type == "nonpermbanned" and profile["Ban_Status"] != "PERMANENT_BAN" and profile["Ban_Status"] != "PBE_LOGIN_TIME_BAN":
                filtered_profiles.append(profile)
            elif ban_type == "all":
                filtered_profiles.append(profile)

def save_profiles():
    with open(f"./results/filtered_profiles_{region}.json", "w") as json_file:
        json_file.truncate(0)
        json.dump(filtered_profiles, json_file, indent=4)

    print(f"Filtered profiles saved to results.")
    x = input("Press Enter to exit.")

def main():
    clean_data()
    get_region()
    get_type()
    load_data()
    filter_profiles()
    save_profiles()

main()
