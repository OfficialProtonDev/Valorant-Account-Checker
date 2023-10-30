# Valorant-Account-Checker

![image](https://github.com/OfficialProtonDev/Valorant-Account-Checker/assets/98558514/d10f123f-08d1-4cf1-9be1-377770576ed3)

# Contents:

**combo.txt** - This is where you put your combolist in the user:pass format.

**checker-proxyless.py** - This is the main checker script.

**data.py** - This is just storage for some constant variables we need to reference.

**display_summary.py** - This script displays a summary of the current checked accounts, including skin count & rank.

**filter.py** - This script allows you  to filter all the checked account data by a couple of categories, like ban status and region.

**all_accounts_data.json** - This is where all the checked account data is stored.

**results** - This is where the filter saves filtered account data.

**skins.json** - This is more storage for some data we need to reference regarding skin ids, etc.

# How To Use:

**Checker** - Simply enter a combolist into the combo.txt file and run the main checker script, it should begin to display results.

**Filter** - Run the filter script and enter your region and ban type, then look in the results folder for the results.

**Summary** - Run the display_summary and expand the window so you can see all the info, the info updates every few seconds 
		     so you can run it alongside the checker. (There needs to be checked account data for this to work).

# IMPORTANT NOTES:

- This is a **PROXYLESS** checker, therefore it will be slower than other checkers that you need paid proxies for.
- Even though it's proxyless, it is setup so you should never run into rate limits. But you can also use a VPN.
- If you are having problems with the summary or filtering, please ensure that there is a "[" on line 1 of all_accounts_data.json.
- These scripts are for EDUCATIONAL PURPOSES ONLY, I do not condone the use of these to check leaked hacked accounts, but rather for reference on how to perform web scraping with python.

# Credits:

Thanks to liljaba for some reference code.
