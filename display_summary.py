from colorama import init, Fore
import time
import os
import re
import json

# Initialize Colorama
init(autoreset=True)

# Initialize counters for different categories
valid_accounts = 0
banned_accounts = 0
temporary_bans = 0
fa_accounts = 0
nfa_accounts = 0

eu_accounts = 0
ap_accounts = 0
kr_accounts = 0
na_accounts = 0
br_accounts = 0
latam_accounts = 0
other_accounts = 0

unranked_accounts = 0
locked_accounts = 0
iron_accounts = 0
bronze_accounts = 0
silver_accounts = 0
gold_accounts = 0
plat_accounts = 0
diamond_accounts = 0
ascendant_accounts = 0
immortal_accounts = 0
radiant_accounts = 0

no_skins = 0
skins_1_10 = 0
skins_10_20 = 0
skins_20_40 = 0
skins_40_80 = 0
skins_80_plus = 0

# Define color constants
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW

data_source = 'all_accounts_data.json'

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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Create a function to format the output in a table
def print_stat(label, count, color=Fore.WHITE):
    print(f"{label:<20}:", color + f"{count}" + Fore.RESET)

def clear_stats():
    global valid_accounts, banned_accounts, temporary_bans, fa_accounts, nfa_accounts
    global eu_accounts, ap_accounts, kr_accounts, na_accounts, br_accounts, latam_accounts, other_accounts
    global unranked_accounts, locked_accounts, iron_accounts, bronze_accounts, silver_accounts, gold_accounts, plat_accounts
    global diamond_accounts, ascendant_accounts, immortal_accounts, radiant_accounts
    global no_skins, skins_1_10, skins_10_20, skins_20_40, skins_40_80, skins_80_plus

    valid_accounts = 0
    banned_accounts = 0
    temporary_bans = 0
    fa_accounts = 0
    nfa_accounts = 0
    eu_accounts = 0
    ap_accounts = 0
    kr_accounts = 0
    na_accounts = 0
    br_accounts = 0
    latam_accounts = 0
    other_accounts = 0
    unranked_accounts = 0
    locked_accounts = 0
    iron_accounts = 0
    bronze_accounts = 0
    silver_accounts = 0
    gold_accounts = 0
    plat_accounts = 0
    diamond_accounts = 0
    ascendant_accounts = 0
    immortal_accounts = 0
    radiant_accounts = 0
    no_skins = 0
    skins_1_10 = 0
    skins_10_20 = 0
    skins_20_40 = 0
    skins_40_80 = 0
    skins_80_plus = 0

# Function to read and parse statistics from the file
def read_stats():
    global valid_accounts, banned_accounts, temporary_bans, fa_accounts, nfa_accounts
    global eu_accounts, ap_accounts, kr_accounts, na_accounts, br_accounts, latam_accounts, other_accounts
    global unranked_accounts, locked_accounts, iron_accounts, bronze_accounts, silver_accounts, gold_accounts, plat_accounts
    global diamond_accounts, ascendant_accounts, immortal_accounts, radiant_accounts
    global no_skins, skins_1_10, skins_10_20, skins_20_40, skins_40_80, skins_80_plus

    with open(data_source, "r") as json_file:
        accounts = json.load(json_file)

    for account in accounts:
        # Ban Status
        if account["Ban_Status"] == "N/A":
            valid_accounts += 1
        elif account["Ban_Status"] == "PERMANENT_BAN" or account['Ban_Status'] == "PBE_LOGIN_TIME_BAN":
            banned_accounts += 1
        else:
            temporary_bans += 1

        # Mail Verified
        if account["Mail Verified"]:
            nfa_accounts += 1
        elif not account['Mail Verified']:
            fa_accounts += 1
        else:
            nfa_accounts += 1

        # Region
        if account["Region"] == "eu":
            eu_accounts += 1
        elif account["Region"] == "ap":
            ap_accounts += 1
        elif account["Region"] == "kr":
            kr_accounts += 1
        elif account["Region"] == "na":
            na_accounts += 1
        elif account["Region"] == "br":
            br_accounts += 1
        elif account["Region"] == "latam":
            latam_accounts += 1
        else:
            other_accounts += 1

        # Rank
        rank = account["Rank"]

        if rank is not None:
            if rank == "Unranked":
                unranked_accounts += 1
            elif account["Level"] < 20:
                locked_accounts += 1
            elif "Iron" in rank:
                iron_accounts += 1
            elif "Bronze" in rank:
                bronze_accounts += 1
            elif "Silver" in rank:
                silver_accounts += 1
            elif "Gold" in rank:
                gold_accounts += 1
            elif "Platinum" in rank:
                plat_accounts += 1
            elif "Diamond" in rank:
                diamond_accounts += 1
            elif "Ascendant" in rank:
                ascendant_accounts += 1
            elif "Immortal" in rank:
                immortal_accounts += 1
            elif "Radiant" in rank:
                radiant_accounts += 1
        else: 
            locked_accounts += 1

        # Skins
        skin_count = account["Skins_Count"]

        if skin_count is not None:
            if skin_count == 0:
                no_skins += 1
            elif 1 <= skin_count <= 10:
                skins_1_10 += 1
            elif 10 < skin_count <= 20:
                skins_10_20 += 1
            elif 20 < skin_count <= 40:
                skins_20_40 += 1
            elif 40 < skin_count <= 80:
                skins_40_80 += 1
            else:
                skins_80_plus += 1
        else:
            no_skins += 1

while True:
    clean_data()

    clear_stats()

    # Read and parse the statistics
    parsed_stats = read_stats()

    clear_screen()

    # Display the results in a table format with colors
    print("Accounts:")
    print_stat("Valid", valid_accounts, GREEN)
    print_stat("Banned", banned_accounts, RED)
    print_stat("Temporary Bans", temporary_bans, YELLOW)
    print_stat("FA", fa_accounts, GREEN)
    print_stat("NFA", nfa_accounts, RED)

    print("\nRegions:")
    print_stat("EU", eu_accounts, YELLOW)
    print_stat("AP", ap_accounts, YELLOW)
    print_stat("KR", kr_accounts, YELLOW)
    print_stat("NA", na_accounts, YELLOW)
    print_stat("BR", br_accounts, YELLOW)
    print_stat("LT", latam_accounts, YELLOW)
    print_stat("??", other_accounts, RED)

    print("\nRanks:")
    print_stat("Unranked", unranked_accounts, RED)
    print_stat("Locked", locked_accounts, RED)
    print_stat("Iron", iron_accounts, RED)
    print_stat("Bronze", bronze_accounts, RED)
    print_stat("Silver", silver_accounts, YELLOW)
    print_stat("Gold", gold_accounts, YELLOW)
    print_stat("Plat", plat_accounts, YELLOW)
    print_stat("Diamond", diamond_accounts, GREEN)
    print_stat("Ascendant", ascendant_accounts, GREEN)
    print_stat("Immortal", immortal_accounts, GREEN)
    print_stat("Radiant", radiant_accounts, GREEN)

    print("\nSkins:")
    print_stat("None", no_skins, RED)
    print_stat("1-10", skins_1_10, YELLOW)
    print_stat("10-20", skins_10_20, YELLOW)
    print_stat("20-40", skins_20_40, GREEN)
    print_stat("40-80", skins_40_80, GREEN)
    print_stat("80+", skins_80_plus, GREEN)

    time.sleep(5)

