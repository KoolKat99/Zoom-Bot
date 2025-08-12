import time
import os



#https://docs.python.org/3/library/getpass.html
import getpass

#numpy installation might be broken due to installing easyocr that changed numpy to < 2
import numpy as np

import pathlib as Path

#https://github.com/asweigart/pyscreeze
import pyscreeze

#https://docs.python.org/3/library/subprocess.html
import subprocess

#use threading instead of ThreadPoolExecutor since we arent doing many tasks
#https://docs.python.org/3/library/threading.html
import threading

#https://docs.python.org/3/library/webbrowser.html
import webbrowser

#https://pyautogui.readthedocs.io/en/latest/
import pyautogui

#https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
import cv2

#https://pypi.org/project/pytesseract/
import pytesseract

#https://docs.python.org/3/library/re.html
import re

#https://pillow.readthedocs.io/en/stable/
from PIL import Image


#screen dimensions 1920x1080 pixels
#using linux mint cinnamon
#dark mode for zoom


#we can make the version for the browser after we finish the simple stuff listed below


#TO DO
#1) I need to set up threading so that the following list of things happens concurretnly
#   1.  Constantly checks for the number of people in the meeting
#   2.  Constantly check for event such as breakout rooms
#   If number of people in main meeting drops then that implies two things, either breakout rooms are active or the meeting is over so just check count

#   3.  Constantly save and check trasncript for info on meeting and how to respond to questions
#   


#2) Set up tests so we don't have to spend so much time manually testing everything

#3) Set up github for this and make it look nice

#4) Add a window connected to chat bot api that reads from the transcript and gives advice on what to say

#5) Make it so chatbot can recognize when its my turn to speak if necessary




#why would we even need an event trigger???
join_zoom_call_event_triggered = threading.Event()


brave_path = "/usr/bin/brave-browser"
cv2.ocl.setUseOpenCL(True)

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)


#joins zoom meeting at certain time
#returns a bool if succesfull so we have to ensure that it worked below
def join_meeting(meeting_url):
    webbrowser.register('brave',
                        None,
                        webbrowser.BackgroundBrowser(brave_path),
                        preferred=True)
    
    webbrowser.get('brave').open(meeting_url)


    time.sleep(5)

    #maximize browser tab so we can ensure that we actually joined the meeting
    maximize_tab("Join from Zoom Workplace app - Zoom - Brave")

    time.sleep(2)

    #look for open-zoom button if we cant find it, then user may have auto-join setup
    file_open_zoom_button = current_dir + "/button_images/open_zoom_button.png"

    try:
        x_pos, y_pos = find_image_location(file_open_zoom_button, center=True)
        #now just click on that location
        pyautogui.click(x=x_pos, y=y_pos)
        print("Succesfully opened zoom")
    except Exception as e:
        #implies there was a problem trying to join so we assume auto-join is setup
        print("Couldn't find open zoom button, auto join must have been selected in browser")
        

    #now we ensure that zoom is open
    time.sleep(5)


    #check if audio is on, then turn it off
    if check_mute_button():
        #now we look for audio button so we can mute ourselves
        file_audio_button = current_dir + "/button_images/audio_on_button.png"

        try:
            x_pos, y_pos = find_image_location(file_audio_button, center=True)
            #now just click on that location
            pyautogui.click(x=x_pos, y=y_pos)
            print("Succesfully muted")
        except Exception as e:
            #we werent able to open window originally, some serious error occured along the way
            print("Couldn't find audio button, auto join must have been selected in browser")
        

    time.sleep(3)


    #look for join button if we cant find it, then user may have auto-join setup
    file_join_zoom_button = current_dir + "/button_images/join_zoom_button.png"
    
    try:
        x_pos, y_pos = find_image_location(file_join_zoom_button, center=True)
        #now just click on that location
        pyautogui.click(x=x_pos, y=y_pos)
        print("Succesfully Joined Zoom Call/Waiting-Room")
    except Exception as e:
        #implies there was a problem trying to join so we assume auto-join is setup
        print("Couldn't find join zoom button, auto join must have been selected in browser")
        
        
    
    #ensure that we are in zoom call, if we are, then return true else false
    #we will look for the leave_button
    file = current_dir + "/button_images/leave_button.png"

    try:
        x_pos, y_pos = find_image_location(file, center=True)
        return True
    except Exception as e:
        return False





#goal is to ensure that mic is muted, returns (True = muted), (False = unmuted)
def check_mute_button():
    file_audio_on = current_dir + "/button_images/audio_on_button.png"
    file_audio_off = current_dir + "/button_images/audio_off_button.png"
    

    #now we have a PIL image that we then turn into an ndarray
    image_output_on = np.array(pyautogui.screenshot(region=find_image_location(file_audio_on)))
    image_output_off = np.array(pyautogui.screenshot(region=find_image_location(file_audio_off)))

    cv_image_output_on = cv2.cvtColor(image_output_on, cv2.COLOR_RGB2GRAY)
    cv_image_output_off = cv2.cvtColor(image_output_off, cv2.COLOR_RGB2GRAY)


    image_audio_on = cv2.imread(file_audio_on, cv2.IMREAD_GRAYSCALE)
    image_audio_off = cv2.imread(file_audio_off, cv2.IMREAD_GRAYSCALE)



    #compare image differences between source image
    if cv2.absdiff(cv_image_output_on, image_audio_on) < cv2.absdiff(cv_image_output_off, image_audio_off):
        return False
    else:
        return True
    

    





#securely unlock computer
def unlock_computer():



    pass






# If number of people in main meeting drops then that implies two things, 
# either breakout rooms are active or the meeting is over so we will check
# member count till we reach one of these events
def breakout_room_or_leave_meeting_logic(min_member_count):
    member_count = check_meeting_member_amount()
    if(member_count < min_member_count):
        #An event is occuring so first look for breakout rooms
        file = current_dir + "/button_images/breakout_room_window.png"
        breakout_room_image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        width = breakout_room_image.shape[1]
        height = breakout_room_image.shape[0]

        image_region = find_image_location(file, width, height)
        if image_region:
            #go to breakout room
            join_breakout_room()
            return True
        else:
            #leave room
            leave_meeting()
            return False
        


#find join button and press
def join_breakout_room():
    file = current_dir + "/button_images/breakout_room_join_button.png"

    x_pos, y_pos = find_image_location(file, center=True)
    #now just click on that location
    pyautogui.click(x=x_pos, y=y_pos)



#find join button and press
def leave_meeting():
    file = current_dir + "/button_images/leave_button.png"
    
    x_pos, y_pos = find_image_location(file, center=True)
    #now just click on that location
    pyautogui.click(x=x_pos, y=y_pos)



#executes find member count picture, then does processing on image, then reads image using OCR
def check_meeting_member_amount():
    file = current_dir + "/button_images/participants_button.png"

    image_region = None
    try:
        image_region = find_image_location(file)
    except Exception as e:
        print(e)
        print("Unable to find Member Count")
        return
    
    participants_image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    number_image = get_image_difference_and_preprocess(participants_image, image_region)
    #get rid of excess white space


    #cv2.imwrite(os.path.splitext(file)[0] + "_number.png", number_image)

    return extract_numbers_from_image(number_image)



#Looks for our specific picture file on our screen, then returns its coordinates
#If you choose center=True then function returns just x and y cordinates of center
def find_image_location(file, center=False):

    image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    width = image.shape[1]
    height = image.shape[0]

    x_pos, y_pos = find_image_location(file, width, height, center=True)
    #now just click on that location
    pyautogui.click(x=x_pos, y=y_pos)

    
    #start with a high confidence interval and slowing decrease it
    confidence_interval = 0.999
    min_confidence_interval = 0.7
    image_region = None

    for _ in range(20):
        try:
            if center:
                x, y = pyautogui.locateCenterOnScreen(file, confidence=confidence_interval, grayscale=True)
                return (x, y)
            else:
                image_location = pyautogui.locateOnScreen(file, confidence=confidence_interval, grayscale=True)

            #Ensure that the width and height are the same for when we do subtraction of images
            if width != image_location.width or height != image_location.height:
                continue
            else:
                image_region = (int(image_location.left), int(image_location.top), int(width), int(height))
                break

        except pyscreeze.ImageNotFoundException and pyautogui.ImageNotFoundException:
            pass

        time.sleep(2)
        confidence_interval -= confidence_interval*0.03

        if confidence_interval < min_confidence_interval:
            break

    return image_region



#takes difference between image we are looking for and image we find by subtracting images
#then we do preprocessing on the image so our OCR can read the text
def get_image_difference_and_preprocess(image, image_region):

    temp_image = pyautogui.screenshot(region=image_region)
    new_image = np.array(temp_image)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2GRAY)
    #cv2.imwrite(os.path.splitext(file)[0] + "_new.png", new_image)

    difference_image = cv2.subtract(new_image, image)
    #cv2.imwrite(os.path.splitext(file)[0] + "_difference_image.png", difference_image)

    #threshold the difference image make it all white
    threshold_value_1 = 50
    _, thresholded_img = cv2.threshold(difference_image, threshold_value_1, 255, cv2.THRESH_BINARY_INV)

    #lastly resize the image
    resized_thresholded_img = cv2.resize(thresholded_img, (int(12*new_image.shape[1]),int(12*new_image.shape[0])))
    
    blurred_resized_img = cv2.GaussianBlur(resized_thresholded_img, (3,3), 0)

    threshold_value_2 = 90
    _, blurred_resized_binary_img = cv2.threshold(blurred_resized_img, threshold_value_2, 255, cv2.THRESH_BINARY)


    return auto_crop_image(blurred_resized_binary_img)



#takes cv2 binary white background and black foreground image and we autocrop it with padding around it
def auto_crop_image(image):
    width = image.shape[1]
    height = image.shape[0]

    #we will find right, left, up, and down maximums
    right = 0
    left = width - 1
    up = height - 1
    down = 0
    for i, _ in enumerate(image):
        for j, pixel in enumerate(_):
            #check for most extremes
            if pixel == 0:
                if j > right:
                    right = j
                
                if j < left:
                    left = j
                
                if i < up:
                    up = i
                
                if i > down:
                    down = i

    
    #We also want to pad our crop a litle bit
    padded = 20
    right = min(right + padded, width - 1)
    left = max(left - padded, 0)
    down = min(down + padded, height - 1)
    up = max(up - padded, 0)


    #Then we will just crop around these 4 values [y,x]
    return image[up:down, left:right]



#used to maximize the zoom tab
# #in linux mint cinnamon run (wmctrl -l) in terminal to see what src_tab should be
# src_tab = "Meeting"
def maximize_tab(src_tab):
    try:
        subprocess.run(["wmctrl", "-r", src_tab, "-b", "add,maximized_vert,maximized_horz"], capture_output=True)
    except Exception as e:
        print(e)



#Pytesseract wants black text over white
def extract_numbers_from_image(image):
    # Load and preprocess image

    # OCR
    text = pytesseract.image_to_string(image, config='--oem 3 --psm 8 digits')
    print("Pytesseract read text: ", text)

    # Extract numbers using regex
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]



#ensures that we can even read the zoom transcript
#returns true if its active or we can turn it on
#returns false if its we cant turn it on
def is_zoom_transcript_active():
    pass



#the zoom transcript is saved in our zoom file, so find users zoom file then start saving and reading
def save_zoom_trascript():
    file = current_dir + "/button_images/save_transcript_button.png"

    x_pos, y_pos = find_image_location(file, center=True)
    #now just click on that location
    pyautogui.click(x=x_pos, y=y_pos)



#use this to init which zoom transcript we will use
#The file we want will be (directory + "/meeting_saved_closed_caption.txt")
def newest_directory(path):
    path = Path(path)
    dirs = [d for d in path.iterdir() if d.is_dir()]
    if not dirs:
        return None
    directory = max(dirs, key=lambda d: d.stat().st_ctime)
    return directory



#reads from zoom directory, in the future we should make it so the user configures where this directory is
#this functions will return text aswell as a pointer to the last place it read
def read_zoom_trascript(file, pointer):
    #
    with open(file, "r")  as transcript:
        #it needs to go to the pointer
        transcript.seek(pointer)
        line = transcript.readline()




#time.struct_time((d.year, d.month, d.day,
#                  d.hour, d.minute, d.second,
#                  d.weekday(), yday, dst))

#we will return hour, minute, and weekday
def get_local_time_to_int_array():
    #so just call time.struct_time
    current_time = time.localtime()
    return (current_time.tm_hour, current_time.tm_min, current_time.tm_wday)



#TO DO 
#Reinstall pip3 since pysched seems to have broke it

#I would recommend not running this script 24/7 every day of the week since if you are using the unlock feature your password will be exposed
if __name__ == '__main__':

    #program has started and global variables are already declared above
    #now we want to schedule a meeting loop
    #I created my own primitive scheduler since sched doesn't seem to install with pip and i really
    #don't need a lot of functions from a scheduler

    #we need an array that contains everydate when we should run this script
    #date = (hour, minute, weekday)
    date_1 = (8, 54, 0)
    date_2 = (8, 54, 2)
    dates_without_padding = []
    dates_without_padding.append(date_1)
    dates_without_padding.append(date_2)


    dates = []
    for date in dates_without_padding:
        for i in range(0,5):
            padding_dates = (dates_without_padding[0],dates_without_padding[1] + i,dates_without_padding[2])
            dates.append(padding_dates)
            

    zoom_meeting_url = "https://us06web.zoom.us/j/81963591023?pwd=7U6tuBGKWf1eZSM3K3BBZhv9y9NaXQ.1"

    in_meeting = False
    member_threshold = 5

    while True:
        
        ############Join Meeting Loop############
        while not in_meeting:
            curr_time = get_local_time_to_int_array()
            
            #we should be handling a larger range since its possible we don't get it first try
            #TO DO make it so there a range of 2 minutes where we can join meeting
            for date in dates:
                if date == curr_time:
                    try:
                        unlock_computer()
                        in_meeting = join_meeting(zoom_meeting_url)
                    except Exception as e:
                        print(e)
                        #try again later
            time.sleep(30)
        ########################################


        ###########Meeting Count Loop############
        while in_meeting:
            in_meeting = breakout_room_or_leave_meeting_logic(member_threshold)
            time.sleep(20)
        #########################################
                


    



    

    

    