import urllib.request
import re
from bs4 import BeautifulSoup
import os
from time import sleep
from random import random


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("zipcodes", help="file containing zipcodes to scrape")
parser.add_argument("-r", "--rentals", dest='rentals', action='store_true',
                     help="boolen to indicate whether to scrape rentals")

parser.set_defaults(rentals=False)

args = parser.parse_args()


def scrape(zipcodes, filename=None, rentals=False):
    if rentals:
        base_url = "http://www.zillow.com/homes/for_rent/"
        if filename is None:
            filename = "rentals.txt"
    else:
        base_url = "http://www.zillow.com/homes/New-Jersey_rb/"
        # next: /homes/New-Jersey_rb/2_p/
        if filename is None:
            filename = "sales.txt"
    
    file = open(filename, 'a')
    
    tags = ['^/homedetails/.?']
    tags_compiled = re.compile("|".join(tags))

    added_so_far = set()
    zipcodes = open(zipcodes).read().split()

    for zipcode in zipcodes:
        url = base_url + zipcode + "_rb/"
        
        html = None

        current_page = 1
        current_url = url
        
        while True:
            
            try:
                html = urllib.request.urlopen(current_url, timeout = 1).read().decode('utf-8')
            except:
                print("Something went wrong...")
                sleep(5)
                continue
                
            soup = BeautifulSoup(html, "lxml")

            try:
                num_results = int(re.search('"totalResultCount":[0-9]+', html).group(0).split(":")[-1])
            except:
                print("No results for zipcode {}".format(zipcode))
                
            items = soup.findAll('a', attrs={"href": tags_compiled})
    
            if len(items) == 0 or set(items).issubset(added_so_far) or num_results == 0:
                break
            
            file.writelines([item['href'] + '\n' for item in items])
            print(current_url + "\tItems added: " + str(len(items)))
            
            current_page += 1
            current_url = url + str(current_page) + "_p/"
    
            added_so_far = added_so_far.union(items)
            sleep(random() * 5)
            
    file.close()
    return filename

def delete_dups(in_file_name, out_file_name):
    seen = set()
    out_file = open(out_file_name, 'w')
    for line in open(in_file_name, 'r'):
        if line not in seen:
            out_file.write(line)
            seen.add(line)
    out_file.close()

if __name__ == "__main__":
    print("Scraping {}".format(args.zipcodes))
    filename = scrape(args.zipcodes, rentals=args.rentals)
    delete_dups(filename, "{}_no_dups.".format(filename))
    
