# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 11:13:54 2020

@author: Ucif
"""
import cv2
import os
import requests


#maximum count from the bing API is 150, it could be changed to a lower number
GROUP_SIZE = 150
MAX_RESULTS = 200
OUTPUT_FILE= "E:\P_PROJECTS\BING_IMAGE_API\DATASET"

#set subscription key and search term
subscription_key = "d7f24ea30bd447518e147de13e15ee6b"
search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
search_term = "barack obama"

#add Ocp-Apim-Subscription-Key to the headers by creating a dictionary
headers = {"Ocp-Apim-Subscription-Key" : subscription_key}

#Create a dictionary for the search request's parameters
params  = {"q": search_term, "license": "public", "imageType": "photo" , "offset": 0, "count": GROUP_SIZE}

#call the bing api with the request library. add headers and parameters and obtain response as 
#jason format. get url of thumbnails from the thumbnailUrl field.

response = requests.get(search_url, headers=headers, params=params)
response.raise_for_status()
search_results = response.json()

#get the total number of search results or the total number of results we want

num_results = min(search_results["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] {} search results for request for '{}'".format(num_results, search_term))

#create directory path to store image
path = os.path.join(OUTPUT_FILE,search_term)
try:
    # Create target Directory
    os.mkdir(path )
    print("Directory " , path ,  " Created ") 
except FileExistsError:
    print("Directory " , path  ,  " already exists")

# looping through the content urls to save the images from the request 
count=0
# A maximum of 150 counts are displayed so a loop is needed to download a lot of images
for offset in range(0, num_results, GROUP_SIZE):
    print("[INFO] making request for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, num_results))
    params["offset"] = offset
    search = requests.get(search_url, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print("[INFO] saving images for group {}-{} of {}...".format(
		offset, offset + GROUP_SIZE, num_results))
    
    for img in results["value"]:
        try:
            image = requests.get(img["contentUrl"], timeout=30 )
            #get the file type
            file_type = img["contentUrl"].split('.')[-1]
            #remove special characters from file type. some of the file extensions have special 
            #characters
            
            file_type = [letter for letter in file_type if letter.isalnum()]
            file_type = "".join(file_type)
    
            #create image file path
            image_path = os.path.join(path,"{}{}".format(str(count).zfill(8),'.'+file_type))
            
            #write the image to disk
            f = open(image_path, "wb")
            f.write(image.content)
            f.close()
        #catch errors that will prevent us from downloading the image    
        except:
            print("[INFO] skipping: {}".format(img["contentUrl"]))
            continue
        image = cv2.imread(image_path)
        
        if image is None:
            print("[INFO] deleting: {}".format(image_path))
            os.remove(image_path)
            count-=1
            continue
            
        count+=1
    print("[INFO] {} images saved to {} folder".format(count, search_term))
