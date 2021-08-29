import re
from bs4 import BeautifulSoup
from selenium import webdriver
import tkinter as tk
import time, pyperclip, os

words=0
index = 0
span_to_eng = {}
eng_to_span = {}
driver = webdriver.Chrome(executable_path='C:/webdrivers/chromedriver.exe')

# NOTE: lower and upper case understanding
def login(path=0):
    #global driver
    #driver = webdriver.Chrome(executable_path='C:/webdrivers/chromedriver.exe')
    if(path ==1):
        driver.get('https://wordplay.com/lesson/1101')
    else:
        driver.get('https://wordplay.com/login')
        time.sleep(1)
        username = driver.find_element_by_id("username")
        password = driver.find_element_by_id("password")

        username.send_keys("user")
        password.send_keys('pass')
        driver.find_elements_by_xpath("//button[@class=\"btn btn-primary center-block\"]")[0].click() # elements returns a list, and [0] uses first element in the list
        time.sleep(6)

def translate(): # Part of making a dictionary of spanish and english words from website
    web_data = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(web_data, 'html.parser')
    for i in soup.find_all(class_="tile-body"):
        span = i.find(class_="text-primary").text.encode().decode("latin1")
        eng = i.find(class_="hidden").text
        span_to_eng[span] = eng # NOTE: Very flawed, change it!
                                # Just check if span exists first, if it does then do multiple spanish with multiple enlgish
                                # But then when you find it in a dictionary, you have to factor in that fact
        for span, eng in span_to_eng.items():
            eng_to_span[eng] = span
        #eng_to_span = {eng:span for span, eng in span_to_eng.items()}
        #span_to_eng.get()

def get_translation_website():
    driver.get("https://wordplay.com/course/5743")
    num_lessons = len(driver.find_elements_by_xpath("//div[@class='list-group-item lesson-item']"))
    for i in range(num_lessons):
        all_lessons = driver.find_elements_by_xpath("//div[@class='list-group-item lesson-item']") # All the sessions change dynamically
        try:
            driver.execute_script("arguments[0].click()", all_lessons[i])
        except: # Temporary fix for the below Note
            time.sleep(5)
            all_lessons = driver.find_elements_by_xpath("//div[@class='list-group-item lesson-item']")
            driver.execute_script("arguments[0].click()", all_lessons[i])
        time.sleep(1.5) # NOTE: Make it so it waits for website to load before proceeding
        translate()
        driver.back()
        time.sleep(1)
    with open("translation.txt", "w") as f: # This may cause error in the future. Display warning before running reading
        for i, v in span_to_eng.items():
            f.write((i+"\n").encode().decode("latin1"))
            f.write((v+"\n").encode().decode("latin1"))

def temp_read(): # Just reads the current page, and nothing else. THis prevents the one english = mult spanish
    translate()

def get_trans_file(): # Doesn't work like I intended it too
    with open("translation.txt", "r") as f:
        content = f.readlines()
        for i in range(1, len(content), 2):
            span = (content[i-1].rstrip())
            span_to_eng[span] = content[i].rstrip()
            # The associated english word of the spanish word is equal to odd indexes of translation.txt

def mult_span_translate(): # because eng to span can have multiple translations
    for span, eng in span_to_eng.items():
        if eng_to_span.get(eng) != None: # If english has multiple spanish translations
            pass
        else:
            eng_to_span[eng] = span

def convert_accent(word, input_box): # Not multi-purpose
    all_accents = driver.find_elements_by_xpath("//button[@class='btn btn-primary input-key']")
    # Revamp convert accent so that it can work with text-pic and text
    actions = {b"\xa1":all_accents[0], #can make multi by changing actions to look for a tile that is equal to
               b"\xa9":all_accents[1],
               b"\xad":all_accents[2],
               b"\xb1":all_accents[3],
               b"\xb3":all_accents[4],
               b"\xba":all_accents[5]}
    accent_present = word.rfind(b"\xc3\x83\xc2") != -1 # Look for the highest occurence and work from the back just in case 2 accents
                                                       # This way, when the string shortens another occurence not affected
    while accent_present: # could be subject to errors if more than one accent
        occur = word.rfind(b"\xc3\x83\xc2")
        input_box.send_keys(word[0:occur].decode())
        actions[word[occur+3: occur+4]].click()
        accent_present = word.rfind(b"\xc3\x83\xc2", occur+5) != -1 # if == -1, it was not found
        if not accent_present:
            input_box.send_keys(word[occur+4:].decode())
            break
    else:
        input_box.send_keys(word.decode())

def complete_multi(): # Make try and except, and catch NoSuchElementException
    while driver.find_element_by_xpath("//div[@class='tile-body']"):

        if len(driver.find_elements_by_xpath("//div[@class='tile-body']")) == 4: # If spanish white text in mid, only 4 other tiles
            text = (driver.find_element_by_xpath("//div[@class='center-block center prompt text-white']").text).encode().decode("latin1").rstrip()
            translated = span_to_eng[text]
            for tile in driver.find_elements_by_xpath("//div[@class='tile-body']//h6"): # Figure out how to not get "text-success text-right".
                if tile.text == translated:
                    tile.click()
                    break
        else: # The photo in the middle is in english, but the tiles afterwards are spanish. 5 tiles in total
            text = driver.find_element_by_xpath("//div[@class='tile-body']//h6").text # Singles out main text in tile, so any subtext not included
            translated = eng_to_span[text]
            for tile in driver.find_elements_by_xpath("//div[@class='tile-body']")[1:]:
                if tile.text.encode().decode("latin1") == translated: # .encode().decode("latin1") changes any missing accents to accents
                                                                      # For example: d�bil to débil
                    tile.click()
                    break
        time.sleep(2)

def complete_tile():
    while driver.find_element_by_xpath("//div[@class='tile-body']"):

        text = driver.find_element_by_xpath("//div[@class='tile-body']//h6").text # Singles out main text in tile, so any subtext not included
        translated = eng_to_span[text]
        try:
            while(translated.index("(")!=-1):
                translated = translated[:translated.index("(")]+translated[translated.index(")")+1:]
        except:
            pass
        x = driver.find_elements_by_xpath("//button[@class='btn btn-primary btn-key med'] | //button[@class='btn btn-key med btn-primary']")# Another one for spaces
        #"""
        translated = translated.encode("latin1").decode() # Reset the encoding and decoding on translated to normal, bc when you take individual letters
                                                          # in a string and try to translate, they have many errors
        for i in translated.lstrip(): # error
            for j in x:
                if(j.text.encode().decode("latin1")==i.encode().decode("latin1") or (i==" " and j.text=="space")): # If letters = or if there needs to be a space
                    j.click()
                    x.remove(j)
                    break
            #driver.find_element_by_xpath("//div[@class='input-group input-group-lg center-block']//div[@class='center']//button[@class='btn btn-primary btn-key med']//*[contains(text(), '"+i+"')]").click()
            time.sleep(.05)
        #"""
        time.sleep(3)

def complete_type():
    while driver.find_element_by_xpath("//div[@class='input-group input-group-lg']//input[@type='text']"): # Add a failsafe, where if it doesn't find in dict, input random
        text_box = driver.find_element_by_xpath("//div[@class='input-group input-group-lg']//input[@type='text']")
        text = (driver.find_element_by_xpath("//div[@class='center-block center prompt']//h3[@class='text-white medium']").text).encode().decode("latin1") # I don't know if i actually need to do this

        if eng_to_span.get(text) is not None:
            translated = eng_to_span[text].encode()
            convert_accent(translated, text_box)
        else:
            translated = span_to_eng[text]
            text_box.send_keys(translated)
        driver.find_element_by_xpath("//button[@id='done-btn']").click()
        time.sleep(3)

try:
    login()
    #//*[@id="choice-block"]/div/div/div/button[6]
    get_trans_file()
    mult_span_translate()

    root = tk.Tk()
    canvas = tk.Canvas(root, height=6, width=60)
    canvas.pack()
    frame = tk.Frame(canvas, bg="white")
    frame.grid(row = 0, column = 0)
    frame_ = tk.Frame(canvas, bg="white")
    frame_.grid(row = 1, column = 0)

    info_label = tk.Label(frame, text = "Testing", width=42, height = 3)
    info_label.grid(row=0, column = 0)
    read_button = tk.Button(frame, text="Read", width = 20, height = 3, command=temp_read)
    read_button.grid(row = 0,column = 1)
    multi_choice = tk.Button(frame_, text="Multi", width = 20, height = 3, command=complete_multi)
    tile_type = tk.Button(frame_, text="Tile", width = 20, height = 3, command=complete_tile)
    free_type = tk.Button(frame_, text="Type", width = 20, height = 3, command=complete_type)
    multi_choice.grid(row = 1,column = 0)
    tile_type.grid(row = 1,column = 1)
    free_type.grid(row = 1,column = 2)

    root.mainloop()
finally:
    time.sleep(4)
    driver.quit()
