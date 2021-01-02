# Import Splinter and BeautifulSoup 
from splinter import Browser 
from bs4 import BeautifulSoup as soup 
import pandas as pd 
import datetime as dt 

def scrape_all():

    # Set the executable path and intitialize the chrome browser in splinter 
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path)

    
    news_title, news_paragraph = mars_news(browser)
    img_url = featured_image
    facts = mars_facts(browser)
    hemisphere_image_urls = hemisphere(browser)
    timestamp = dt.datetime.now()

    # Run all scraping function and store results in dictionary 
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": facts,
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data 
    browser.quit()
    return data 


### Latest Mars News ###

def mars_news(browser):
    # Visit the mars nasa news site 
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)

    # Optional delay for loading the page
    # Accomplishing 2 things here
    # 1. we're searching for elements with a specific combination of tag (ul and li) and attribute(item_list and slide)
    # 2. we're also telling browser to wait one second before searching for components. Good for dynamic websites to 
    # give it time to load - especially if image heavy 
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Set up HTML parser
    html = browser.html 
    news_soup = soup(html, 'html.parser')

    # Add try/ except for error handling 
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text 
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Mars Images ###

def featured_image(browser):

    # Visit the url
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find the click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that 
    # useful Splinter func is the ability to search for HTML elements by text
    # 1.uses is_element_present_by_text() method-once executed it will return a boolean T or F to let us know if there
    browser.is_element_present_by_text('more info', wait_time=1)
    # 2. create variable where we employ the browser.links.find method - this will take our string 'more info' to find
    # the link associated with the "more info" text 
    more_info_elem = browser.links.find_by_partial_text('more info')
    # 3. tell splinter to click it 
    more_info_elem.click()

    # Parse the resulting html with soup 
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    try:
        # Find the relative image url 
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None 

    # Use the base URL to create an absolute URL 
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

### Mars Facts ### 

def mars_facts(browser):
    url = 'http://space-facts.com/mars/'
    browser.visit(url)

    # add try/except for error handling 
    try:
        # use 'read_html' to scrape the facs table into a datframe 
        facts_df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe 
    facts_df.columns=['description', 'value']
    facts_df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap 
    return facts_df.to_html(classes=["table-bordered", "table-striped", "table-hover"])


### Mars hemispheres 

def hemisphere(browser):

    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    # Get a List of All the Hemispheres
    hemi_links = browser.find_by_css("a.product-item h3")

    for link in range(len(hemi_links)):
        hemisphere = {}
        
        # Click into link
        browser.find_by_css("a.product-item h3")[link].click()
        
        # Find Sample & Extract href
        sample_element = browser.links.find_by_text("Sample").first
        hemisphere["img_url"] = sample_element["href"]
        
        # Get Hemisphere Title
        hemisphere["title"] = browser.find_by_css("h2.title").text
        
        # Append Hemisphere Object to List
        hemisphere_image_urls.append(hemisphere)
        
        # Navigate Backwards
        browser.back()

    return hemisphere_image_urls

# Helper Function
def scrape_hemisphere(html_text):
    hemisphere_soup = soup(html_text, "html.parser")
    try: 
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_element = None
        sample_element = None 
    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemisphere



if __name__ == "__main__":

    # If running as script, print scraped data 
    print(scrape_all())

