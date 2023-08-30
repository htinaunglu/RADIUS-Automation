from requests.sessions import urljoin, Session
import hashlib
import hmac
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed, thread
from tqdm import tqdm
import argparse

session = Session()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Autoupdate radius user expire date.")
    parser.add_argument("--url", required=True, default="http://localhost", help="URL of the target server.")
    parser.add_argument("--username", required=True, default="admin", help="Username for logging in.")
    parser.add_argument("--password", required=True, default="1111", help="Password for logging in.")
    parser.add_argument("--date", required=True, help="The date to set for users. Formet 'YYYY-MM-DD'")
    parser.add_argument("--userfile", required=False, default="users.csv", help="User List csv file path. You can export from web portal")
    parser.add_argument("--thread", type=int, required=False, default=10, help="Multithread count.")
    parser.add_argument("--userfield", required=False, default="User name", help="User field in the csv file")
    parser.add_argument("--delim", required=False, default=";", help="delimiter to separate csv file")
    return parser.parse_args()

def admin_login(BASE_URL, user,passwd):
    hex_hmac_md5 = hmac.new(user.encode(), hashlib.md5(passwd.encode()).hexdigest().encode(), digestmod='MD5').hexdigest()
    login_url = urljoin(BASE_URL , "/admin.php?cont=login")
    login_data = {"managername": user, "password": passwd, "lang": "English", "Submit": "Login", "md5": hex_hmac_md5, "url": ''}
    try:
        session.post(login_url, data=login_data)
    except:
        raise "Can't login. Please check the url path and credential."


def update_user_info(BASE_URL, username,date):
    # Get userinfo
    getinfo_url = urljoin(BASE_URL , f"/admin.php?cont=edit_user&username={username}")
    resp = session.get(getinfo_url)
    soup = BeautifulSoup(resp.text,'html.parser')
    form_soup = soup.select_one('form')

    # text input without disable
    data = {e['name']: e.get('value', '') for e in form_soup.find_all('input', {'name': True, 'type':'text', 'disabled': False,})}

    # Selected option
    for e in form_soup.find_all('option', selected=True):
        data[e.parent['name']] = e.get('value', '')

    # Selection with default select
    data['lang'] = form_soup.select_one('#lang > option').get('value', '')
    data['groupid'] = form_soup.select_one('#groupid > option').get('value', '')
    data['owner'] = form_soup.select_one('#owner > option').get('value', '')

    # textarea
    for e in form_soup.find_all('textarea'):
        if e.contents:
            data[e['name']] = e.contents[0]

    # for checkbox
    for e in form_soup.find_all('input', {'name': True, 'type':'checkbox' ,'disabled': False, 'checked': True}):
        data[e['name']] = e.get('value', '')

    # for radio
    for e in form_soup.find_all('input', {'name': True, 'type':'radio' ,'disabled': False, 'checked': True}):
        data[e['name']] = e.get('value', '')

    # Change the expiration date
    data['expiration'] = date

    update_url = urljoin(BASE_URL , f"/admin.php?cont=update_user&username={username}")
    resp = session.post(update_url , data=data,)
    if resp.status_code == 200:
        if 'Account updated' in resp.text:
            return f"{username} Success"
    return f"{username} Failed"


def read_csv_users(filename="users.csv",UserFieldName="User name",delim=";"):
    users_list = []
    with open(filename, 'r', encoding='UTF8', newline='') as f:
        csvReader = csv.DictReader(f,delimiter=delim)
        for rows in csvReader:
            users_list.append(rows[UserFieldName])
    return users_list
        

def main():
    args = parse_arguments()
    # Admin login
    admin_login(args.url, args.username,args.password)
    # Read users list 
    users = read_csv_users(args.userfile, args.userfield, args.delim)
    users_count = len(users)
    print(f"Total users: {users_count}")
    # expire date
    exp_date = args.date

    with tqdm(total=users_count, desc="Processing Users", unit="user") as pbar:
        with ThreadPoolExecutor(max_workers=args.thread) as ex:
            futures = [ex.submit(update_user_info, args.url, user, exp_date) for user in users]
            try:
                for future in as_completed(futures):
                    result = future.result()
                    pbar.update(1)
            except KeyboardInterrupt:
                    ex._threads.clear()
                    thread._threads_queues.clear()
                    ex.shutdown(wait=False, cancel_futures=True)
    print("----------------------------------")
    print("Automation completed successfully!")

if __name__ == '__main__':
    main()

