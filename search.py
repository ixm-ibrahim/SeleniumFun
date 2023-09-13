import os
import time
import json
import win32api
import winsound
import threading
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

DIR = r"common absolute dir"

URLS = ["url to custom page results"]
DESTS = [DIR + "Subfolder"]
PREFIX = "File Prefix - "

lock = threading.Lock()

def GetPDFs(URL, DEST, i):
    if not os.path.exists(DEST):
        os.makedirs(DEST)

    settings = {
           "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
    prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings), 
        "savefile.default_directory": DEST}


    opts = Options()
    opts.add_argument("user-agent=whatever you want")
    opts.add_experimental_option('prefs', prefs)
    opts.add_argument('--kiosk-printing')
    # Hopefully get rid of captchas (google.com is bookmarked)
    #opts.add_argument(r"--user-data-dir=C:\Users\ixmib\AppData\Local\Google\Chrome\User Data") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    #opts.add_argument(r'--profile-directory=Profile ' + str(i+1)) #e.g. Profile 3
    opts.add_argument(r'--profile-directory=Default') #e.g. Profile 3
    #opts.add_argument(r'--profile-directory=Guest Profile') #e.g. Profile 3


    # Open the website in Chromium, hopefully getting rid of captchas
    driver = webdriver.Chrome(options=opts)
    #driver.maximize_window()
    #time.sleep(10)
    driver.get(URL)


    # Repeat until there are no more pages
    nextPage = True
    while nextPage:
        # Extract the search results from the URL
        search_results = driver.find_elements(By.CLASS_NAME, 'text-content')
        
        # Create a list to store the links
        links = []
        '''
        for r in search_results:
            print(r);
        '''
        # For each search result
        for search_result in search_results:
            # Get the link
            link = search_result.find_element(By.TAG_NAME, "a")

            # Add the link to the list
            links.append(link.get_attribute("href"))
        
        print(links)

        # Open a new tab to do all the printing
        #driver.find_elements(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
        driver.execute_script("window.open('about:blank', 'secondtab');")
        driver.switch_to.window("secondtab")

        # For each link
        for link in links:
        #while False:
            # Continue untile the Captcha has been dealt with
            with lock:
                captcha = True
                while captcha:
                    # Open a new tab and direct it to site:<link> on Google
                    driver.get("https://www.google.com/search?q=site:" + link)
                    #time.sleep(10)
                    #driver.execute_script("window.open('https://www.google.com/search?q=site:'" + link + ", 'new_tab');")
                    #driver.switch_to.window("new_tab")
                    
                    captcha = "google.com/sorry" in driver.current_url
                    if captcha:
                        '''frequency = 2500  # Set Frequency To 2500 Hertz
                        duration = 1000  # Set Duration To 1000 ms == 1 second
                        winsound.Beep(frequency, duration)'''
                        print('\a')
                        win32api.MessageBox(0, 'Complete Captcha', 'Error')
            #continue
                # Click on Google result
                click_elem = driver.find_element("xpath", "//body/div[@id='main']/div[3]/div[1]/div[1]/a")
                click_elem.click()
            
            # Get the title of the page
            title = driver.title.partition("|")[0]
            title = title.replace(":", "_")
            title = title.replace("?", ",")
            title = title.replace("\"", "'")
            title = title.replace("–", "-")
            title = title.replace("—", "-")
            
            # Save the page to PDF using Microsoft Print to PDF
            count = len(os.listdir(DEST))
            driver.execute_script('window.print();')
            
            # Wait until the new file is created
            while count == len(os.listdir(DEST)):
                pass
            
            #files = filter(lambda f: f.endswith(('.pdf','.PDF')), os.listdir(DEST)))
            files = os.listdir(DEST)
            files = [DEST + "/" + file for file in files]
            #files.sort(key=os.path.getmtime, reverse=True)
            files.sort(key=os.path.getctime, reverse=True)
            latest_file = files[0]
            new_file_name = PREFIX + title + ".pdf"
            try:
                os.rename(os.path.join(DEST,latest_file), os.path.join(DEST,new_file_name))
            except:
                pass
        
        # Close new tab
        #driver.find_elements(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'w')
        with lock:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        #time.sleep(4)
        
        # See if there is another page to scan
        test_pager = driver.find_elements(By.CLASS_NAME, 'pager-next')
        print(len(test_pager))
        try:
            test_link = test_pager[0].find_element(By.TAG_NAME, 'a')
            with lock:
                test_link.click()
            time.sleep(2)
            nextPage = True
        except:
            nextPage = False
        
    driver.quit()

# Create several threads
threads = []
for i in range(len(URLS)):
#for i in range(1):
    thread = threading.Thread(target=GetPDFs, args=(URLS[i],DESTS[i], i))
    threads.append(thread)

# Start the threads
for thread in threads:
    thread.start()

# Wait for the threads to finish
for thread in threads:
    thread.join()

'''
for i in range(len(URLS)):
    GetPDFs(URLS[i],DESTS[i], i)
    '''

'''
import os
import time
import json
import win32api
import winsound
import threading
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'
    
def force_captcha():
    driver = webdriver.Chrome()
    driver.get("https://www.girlschase.com/articles/fractionation")
    
    driver.execute_script("window.open('about:blank', 'secondtab');")
    driver.switch_to.window("secondtab")
    
    breakout = False
    
    while not breakout:
        captcha = True
        while captcha:
            driver.get("https://www.google.com/search?q=site:" + "https://www.google.com")
            #time.sleep(2)
            
            captcha = "google.com/sorry" in driver.current_url
            if captcha:
                \'''frequency = 2500  # Set Frequency To 2500 Hertz
                duration = 1000  # Set Duration To 1000 ms == 1 second
                winsound.Beep(frequency, duration)\'''
                print('\a')
                win32api.MessageBox(0, 'Complete Captcha', 'Error')
                breakout = True
            
    driver.quit();
    

DIR = r"common absolute dir"

URLS = ["url to custom page results"]
DESTS = [DIR + "Subfolder"]
PREFIX = "File Prefix - "

lock = threading.Lock()

def GetPDFs(URL, DEST, i):
    if not os.path.exists(DEST):
        os.makedirs(DEST)

    settings = {
           "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
    prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings), 
        "savefile.default_directory": DEST}


    opts = Options()
    opts.add_argument("user-agent=whatever you want")
    opts.add_experimental_option('prefs', prefs)
    opts.add_argument('--kiosk-printing')
    opts.add_argument(r'--profile-directory=Default') #e.g. Profile 3


    # Open the website in Chromium, hopefully getting rid of captchas
    driver = webdriver.Chrome(options=opts)
    driver.get(URL)
                
    search_results = driver.find_elements(By.CLASS_NAME, 'specific element')
    search_links = search_results[0].find_elements(By.TAG_NAME, "a")
    links = []
    
    for search_link in search_links:
        # Add the link to the list
        try:
            url = search_link.get_attribute("href")
            print(url)
            if "/specific kind of link" in url:
                links.append(url)
        except:
            pass
    links = list(set(links))
    print(links)
    
    # Open a new tab to do all the printing
    #driver.find_elements(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
    driver.execute_script("window.open('about:blank', 'secondtab');")
    driver.switch_to.window("secondtab")
    
    for link in links:
        #while False:
        # Continue untile the Captcha has been dealt with
        with lock:
            captcha = True
            while captcha:
                # Open a new tab and direct it to site:<link> on Google
                time.sleep(1)
                driver.get("https://www.google.com/search?q=site:" + link)
                
                captcha = "google.com/sorry" in driver.current_url
                if captcha:
                    \'''frequency = 2500  # Set Frequency To 2500 Hertz
                    duration = 1000  # Set Duration To 1000 ms == 1 second
                    winsound.Beep(frequency, duration)\'''
                    print('\a')
                    win32api.MessageBox(0, 'Complete Captcha', 'Error')
        #continue
            # Click on Google result
            click_elem = driver.find_element("xpath", "//body/div[@id='main']/div[3]/div[1]/div[1]/a")
            click_elem.click()
        
        # Get the title of the page
        title = driver.title.partition("|")[0]
        title = title.replace(":", "_")
        title = title.replace("?", ",")
        title = title.replace("\"", "'")
        title = title.replace("–", "-")
        title = title.replace("—", "-")
        
        # Save the page to PDF using Microsoft Print to PDF
        count = len(os.listdir(DEST))
        driver.execute_script('window.print();')
        
        # Wait until the new file is created
        while count == len(os.listdir(DEST)):
            pass
        
        #files = filter(lambda f: f.endswith(('.pdf','.PDF')), os.listdir(DEST)))
        files = os.listdir(DEST)
        files = [DEST + "/" + file for file in files]
        #files.sort(key=os.path.getmtime, reverse=True)
        files.sort(key=os.path.getctime, reverse=True)
        latest_file = files[0]
        new_file_name = PREFIX + title + ".pdf"
        try:
            os.rename(os.path.join(DEST,latest_file), os.path.join(DEST,new_file_name))
        except:
            pass
        
    driver.quit()

#force_captcha()
\'''
# Create several threads
threads = []
for i in range(len(URLS)):
#for i in range(1):
    thread = threading.Thread(target=GetPDFs, args=(URLS[i],DESTS[i], i))
    threads.append(thread)

# Start the threads
for thread in threads:
    thread.start()

# Wait for the threads to finish
for thread in threads:
    thread.join()

\'''
for i in range(len(URLS)):
    GetPDFs(URLS[i],DESTS[i], i)
    
'''
