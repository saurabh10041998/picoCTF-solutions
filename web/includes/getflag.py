#! /usr/bin/python3
import requests
import re

# first part is in the css file

base_url = "http://saturn.picoctf.net:57833/"

def get_css_flag():
    locator = f"{base_url}/style.css"
    response = requests.get(locator)
    pattern = re.compile("picoCTF(.*)")
    flag_1 = pattern.search(response.text).group(0)
    flag_1 = flag_1.split("*/")[0].strip()                  # comment style in css
    return flag_1


def get_script_flag():
    locator = f"{base_url}/script.js"
    response = requests.get(locator)
    pattern = re.compile("//\s+(.*)")
    flag_2 = pattern.search(response.text).group(1)     # get everything except //
    return flag_2.strip()

flag = get_css_flag()
flag += get_script_flag()

print("\x1B[32m[*] Flag is : \x1B[0m", flag)
