#!/usr/bin/env python3
"""Inspect HTML structure for Samehadaku and Sokuja"""

import requests
from bs4 import BeautifulSoup

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

# 1. Samehadaku S1
print("=== Samehadaku S1 Structure ===")
url = "https://v1.samehadaku.how/anime/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso-tensei-shite-shison-tachi-no-gakkou-e/"
try:
    resp = requests.get(url, headers=get_headers())
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Check lstepsiode
    lstepsiode = soup.find('div', class_='lstepsiode')
    if lstepsiode:
        print("Found div.lstepsiode")
        ul = lstepsiode.find('ul')
        if ul:
            print("Found ul inside lstepsiode")
            li = ul.find('li')
            if li:
                print(f"First li content: {li}")
                a = li.find('a')
                if a:
                    print(f"Link text: {a.get_text(strip=True)}")
                    print(f"Link href: {a['href']}")
                    
                    # Check for spans inside a
                    for child in a.children:
                        print(f"  Child: {child.name} -> {child}")
        else:
            print("No ul inside lstepsiode")
            # Maybe it's directly divs?
            print(lstepsiode.prettify()[:500])
    else:
        print("No div.lstepsiode found")
        # Check listeps
        listeps = soup.find('div', class_='listeps')
        if listeps:
            print("Found div.listeps")
            print(listeps.prettify()[:500])

except Exception as e:
    print(f"Error: {e}")

# 2. Sokuja
print("\n=== Sokuja Structure ===")
url = "https://x3.sokuja.uk/anime/maou-gakuin-no-futekigousha-season-2-part-2-shijou-saikyou-no-maou-no-shiso-tensei-shite-shison-tachi-no-gakkou-e-kayou-ii-subtitle-indonesia/"
try:
    resp = requests.get(url, headers=get_headers())
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    eplister = soup.find('div', class_='eplister')
    if eplister:
        print("Found div.eplister")
        li = eplister.find('li')
        if li:
            print(f"First li content: {li}")
            a = li.find('a')
            if a:
                print(f"Link text (raw): '{a.get_text()}'")
                print(f"Link text (stripped): '{a.get_text(strip=True)}'")
                
                # Check structure inside a
                for child in a.children:
                    if child.name:
                        print(f"  Child tag: <{child.name}> Text: '{child.get_text(strip=True)}'")
                    else:
                        print(f"  Child text: '{child}'")
    else:
        print("No div.eplister found")

except Exception as e:
    print(f"Error: {e}")
