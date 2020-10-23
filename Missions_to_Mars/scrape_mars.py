# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd
import time

def scrape():
    #SCRAPE MARS NEWS
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    # Retrieve page with the requests module
    response = requests.get(url)
    time.sleep(1)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
    #find and store acticle title
    news_title = soup.find("div", class_="content_title").text.strip()
    #find and store article preview text
    news_p = soup.find("div", class_="rollover_description_inner").text.strip()
    #store results as dictionary
    news = {
            "news_title":news_title,
            "news_p":news_p
    }

    #SCRAPE JPL FEATURED IMAGE URL
    #intialize driver
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)
    #set url
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    #load url into automated browser
    browser.visit(jpl_url)
    #click "FULL IMAGE" link
    browser.links.find_by_partial_text('FULL IMAGE')
    #store html code
    html = browser.html
    #parse html code
    jpl_soup = BeautifulSoup(html, 'html.parser')
    #find and store anchor tag info
    link_details = jpl_soup.find_all("a",class_="button fancybox")
    #find and store image relative link
    relative_path = link_details[0]["data-fancybox-href"]
    #define image absolute path
    full_path = f"https://www.jpl.nasa.gov{relative_path}"

    #SCRAPE MARS FACTS
    #define url
    facts_url = "https://space-facts.com/mars/"
    #use pandas read_html to find all tables on the page
    tables = pd.read_html(facts_url)
    #make dataframe from the first (and only) table
    df = tables[0]
    #rename colums and set index
    df.columns=["Category","Value"]
    df = df.set_index("Category")
    #save table as html code
    html_table = df.to_html()
    html_table = html_table.replace("\n","")

    #SCRAPE HEMISPHERE IMAGE URLS
    #initialize driver
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)
    #define starting url
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    #create list of hemispeheres
    hemispheres = ["Valles Marineris","Cerberus","Schiaparelli","Syrtis Major"]
    #initialize list to hold urls
    img_urls = []
    #loop through each hemisphere name
    for x in range(4):    
        #go to stating age
        browser.visit(hemi_url)
        try:
            #click link containing hemisphere name
            browser.click_link_by_partial_text(f"{hemispheres[x]} Hemisphere Enhanced")
            time.sleep(1)
        except:
            print ('error')
        #store page text
        html = browser.html
        #parse page code
        hemi_soup = BeautifulSoup(html, 'html.parser')
        #store image url
        img_link = hemi_soup.find("div", class_="downloads").find("a")["href"]
        #add image url to url list 
        img_urls.append(img_link)
    #create list of dictionaries for each hemisphere and image link
    image_dict_list = [
                    {"title":f"{hemispheres[0]} Hemisphere", "img_url":img_urls[0]},
                    {"title":f"{hemispheres[1]} Hemisphere", "img_url":img_urls[1]},
                    {"title":f"{hemispheres[2]} Hemisphere", "img_url":img_urls[2]},
                    {"title":f"{hemispheres[3]} Hemisphere", "img_url":img_urls[3]}
                        ]

    #ASSEMBLE SCRAPING RESULTS
    scrape_results = {
        "news":news,
        "featured_image": full_path,
        "facts": html_table,
        "hemispheres": image_dict_list   
    }

    return scrape_results