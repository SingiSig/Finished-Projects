import requests
import json
import csv
import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
'''
initial function that specifies the required variables to get the online data.
'''
def cityAllowcation():                                                         
    api="7d43f39acfd1e7cb47c15585ff08511a"                                     #API key to give access to the data
    url="https://api.openweathermap.org/data/2.5/forecast"                     #The url to the web page where the data is
    city=["London", "Manchester", "Birmingham", "Leeds", "Glasgow", 
          "Southampton", "Liverpool", "Leicester", "Nottingham", "Sheffield", 
          "Bristol", "Belfast"]                                                #List of cities
    raining=[]                                                                 #Empty list for the cities classified as rain
    snowing=[]                                                                 #Empty list for the cities classified as snow
    ice=[]                                                                     #Empty list for the cities classified as ice
    other=[]                                                                   #Empty list for the cities not classified as any of the above
    for j in range(1,4):                                                       #This makes it so that you can look at miltiple days
        for i in range(len(city)):                                             #This is to loop through all the cities
            if (j<=1):                                                         #This is to prevent multi readings from the webpage and multi writing of files.
                readData(api,url,city[i])                                      #Calls the readData function and passes it the api, url and the city that the data should be about
            sortsData(raining, snowing, ice, other, city[i],j)                 #Function for sorting through the data and gathering only one day data
        multiOutput(raining, snowing, ice, other, j)                           #Calls the function that prints out the multi line output, and passing the weather lists
#TASK 1
'''
Function for reading the online data for the web page
'''
def readData(api, url, city): 
    p={"q":city, "appid":api}                                                  #Dictionary for the url parameters
    r=requests.get(url, params=p)                                              #The request fution that requests access to the web page
    if r.status_code==200:                                                     #If statement that checks if the status code is ok
        read_data=r.text                                                       #If the status code is ok then read the data
        jsonToPython=json.loads(read_data)                                     #Convert the json data to a python dictionary
        cityTemp=assignTemp(jsonToPython)                                      #Creates the cityTemp value from calling the assignTemp function and passes in the dictionary
        cityWeather=assignWeather(jsonToPython)                                #Creates the cityWeather value from calling the assignWeather function and passes in the dictionary
        cityDate=assignDate(jsonToPython)                                      #Creates the cityDate value from calling the assignDate function and passes in the dictionary
        writeCityFile(city, cityTemp, cityWeather, cityDate)                   #Calls the function to write the csv files and passes in the city and the lists of the data
    else:                                                                      #If the status code is not okay 
        print("Error")                                                         #Prints that there is an error
        print(r.status_code)                                                   #Prints the error code
    return                                                                     #Retuns and iterates through the next city

#TASK 2
'''
Extracts the temprature data
'''
def assignTemp(cityDict):                                                      #Takes in the city dictionary as a parameter
    temp=[]                                                                    #Creates an empty list
    for i in range(0,40):                                                      #iterates through the 40 values
        temp.append(convertFromKToC(cityDict["list"][i]["main"]["temp"]))      #Selects the specific data to extract and calls the convert function
    return temp                                                                #Returns the list
'''
Extracts the main weather condition data
'''
def assignWeather(cityDict):                                                   #Takes in the city dictionary as a parameter
    weather = []                                                               #Creates an empty list
    for i in range(0,40):                                                      #iterates through the 40 values
        weather.append(cityDict["list"][i]["weather"][0]["main"])              #Selects the specific data to extract
    return weather                                                             #Returns the list

'''
Extracts the date data
'''
def assignDate(cityDict):                                                      #Takes in the city dictionary as a parameter
    date = []                                                                  #Creates an empty list
    for i in range(0,40):                                                      #iterates through the 40 values
        date.append(cityDict["list"][i]["dt_txt"])                             #Selects the specific data to extract
    return date                                                                #Returns the list

'''
Converts from Kelvin to Celsius
'''
def convertFromKToC(k):                                                        #Takes in the kelvin value for convertion
    c=k-273.15                                                                 #Converts the kelvin value into celsius
    return round(c, 2)                                                         #returns the celsius value rounded to two decimals

'''
Creates and writes the data to csv files
'''
def writeCityFile(city, cityTemp, cityWeather, cityDate):                      #Takes in the current city and the lists of data
    with open(city+".csv", "w",newline="")as myfile:                           #Creates/opens a file with the city as a name
        csvwriter = csv.writer(myfile, dialect="excel")                        #specifies the writer for the csv file and what dialect it is
        row=["Date and time","Main weather conditions","Temprature"]           #initialises the firts row
        csvwriter.writerow(row)                                                #Writes the first row
        for i in range(len(cityTemp)):                                         #Loops through all values in one of the lists
            row=[cityDate[i], cityWeather[i], cityTemp[i]]                     #specifies the row to write with the lists all indexed the same to have the data match
            csvwriter.writerow(row)                                            #Writes the previus row to the file
    message = "File created for "+city                                         #Creates a message specifying that the file has been created
    return message                                                             #Returns the message

#TASK 3
'''
gathers the data for the one day and the date and then calls to sort 
the cities.
'''
def sortsData(raining, snowing, ice, other, city, j):                          #Function for sorting the data and taking in the lists for the classifications the city and the amount of days that the program needs to look ahead
    tomorrow=getDate(j)                                                        #Assigns the tomorrow variable to the returned value from getDate
    dayData=oneDayData(tomorrow, city)                                         #Creates the dayData variable with the returned data from odeDayData passing in the date and city to look at
    return decodeData(dayData, city, raining, snowing, ice, other)             #Returns the value returned from decodeData while passing in the dayData the city and the classifications lists

'''
Gets the current day and adds the disired amount to it (be it 1, 2 or 3 days)
'''
def getDate(i):                                                                #The date function that gets in how far ahead it needs to have the date
    now=datetime.datetime.now() + datetime.timedelta(days=i)                   #Increments the date by the specified amount
    date=now.strftime("%Y-%m-%d")                                              #converts the date to just the date and removes the time
    return date                                                                #Returns the date 

'''
Reads the data from the csv files and splits the data by date and gathers 
only the desired data
'''

def oneDayData(day, city): 
    dayData=[]                                                                 #Creates an empty list for the specific day data
    for line in open(city+".csv", "r"):                                        #Opens and reads the data from the csv file for the specific city
        data = line.replace('\n', '').split(',')                               #Initialises the data as the line from the for loop with the "\n" replaced as nothing and splits it based on the comma
        if (data[0].split(' ')[0] == day):                                     #Checks if the data (which should be the date from the online data, split by the spcae) mathses the day specified 
            dayData.append(data)                                               #If the day mathces then add the data (the line from the csv file) to the dayData variable
    return dayData                                                             #Once finished return the list
    
'''
Creates lists with the city names that fall into the specified categories
'''
def decodeData(dayData, city, raining, snowing, ice, other): 
    for i in range(0,8):                                                       #Loops through the eight readings from one day
        if (float(dayData[i][2])<0.0):                                         #Checks if the temprature is below zero
            if city not in ice:                                                #Checks if the city is not already in the list for ice
                if city.count(city)<=2:                                        #If the city appears twice then add the city to ice to fufill the requirement for at least six hours of snow
                    ice.append(city)                                           #Adds the city to the ice list
        elif(dayData[i][1]=="Snow"):                                           #Cehcks if the main forecast is snow
            if city not in snowing:                                            #Checks if the city is not already in there 
                snowing.append(city)                                           #Adds the city to the snow list
        elif((dayData[i][1]=="Rain") and (i>=2) and (i<=7)):                   #Checks if the main forecast is rain and if the rain happend after 06 and before 21
            if city not in raining:                                            #Checks if the city is not already in there
                raining.append(city)                                           #Adds the city to the rain list
        else:                                                                  #If the city does not classify for any of the lists then it ends up here 
            if city not in other:                                              #Checks if the city is not already in there
                other.append(city)                                             #Adds the city to the other list
    return other, raining, snowing, ice                                        #Returns the lists filled with cities

'''
Prints the data into the console as a multiline output
'''
def multiOutput(raining, snowing, ice, other, j): 
    date=getDate(j)                                                            #Gets the date
    print("\nDate:"+date)                                                      #Prints the date for the data
    print("Enjoy the weather if you are living in these cities")               #Prints the message for the list other
    for i in range(len(other)):                                                #Loops though the other list
        print(other[i])                                                        #Prints the cities in other
    print("\nBring an umberella if you live in these cities:")                 #Prints the message for the list rain
    for i in range(len(raining)):                                              #Loops though the rain list
        print(raining[i])                                                      #Prints the cities in rain
    print("\nMind your step if you live in these cities")                      #Prints the message for the list snow
    for i in range(len(snowing)):                                              #Loops though the snow list
        print(snowing[i])                                                      #Prints the cities in snow
    print("\nPlan your journey well if you are in these cities")               #Prints the message for the list ice
    for i in range(len(ice)):                                                  #Loops though the ice list
        print(ice[i])                                                          #Prints the cities in ice

    return writeXMLFile(raining, snowing, ice, other, date)                    #Returns the call to write the xml file passing the lists and the date

#TASK 4 & 5
'''
Creates the xml file for each day
'''
def writeXMLFile(raining, snowing, ice, other, date):  
    root=ET.Element("WeatherForcast")                                          #Initialises the root element in the xml file 
    day=ET.SubElement(root, "date")                                            #Intiialises the date as a sub element of root
    day.set('date',date)                                                       #Sets the date
    A="GoodWeather"                                                            #Assigns the GoodWeather brand to A
    inp=ET.SubElement(root, A)                                                 #Initialises the sub element of the date as the weather of A
    B="cities"                                                                 #Assigns the cities brand to B
    inp1=ET.SubElement(inp, B)                                                 #Initialises the sub element of the weather as cities
    C="CityName"                                                               #Assigns the CityName brand to C
    for i in range(len(other)):                                                #Loops though the classification list
        inp2=ET.SubElement(inp1, C)                                            #Initialises the sub element of cityName
        inp2.set('name',other[i])                                              #Sets the name of the city 
        mydata=ET.tostring(root)                                               #Creates the data object
    myfile = open(date+".xml", "w")                                            #Opens the file with the date as the name of it
    myfile.write(str(BeautifulSoup(mydata, "xml").prettify()))                 #Writes the data into it and prettifyes it

#The process repeates so the comments are unecacery
    A="RainWeather"                                                            #Assigns the RainWeather brand to A
    inp=ET.SubElement(root, A)
    B="cities"
    inp1=ET.SubElement(inp, B)
    C="CityName"
    for i in range(len(raining)):
        inp2=ET.SubElement(inp1, C)
        inp2.set('name',raining[i])
        mydata=ET.tostring(root)
    myfile = open(date+".xml", "w")
    myfile.write(str(BeautifulSoup(mydata, "xml").prettify())) 

#The process repeates so the comments are unecacery
    A="SnowWeather"                                                            #Assigns the SnowWeather brand to A
    inp=ET.SubElement(root, A)
    B="cities"
    inp1=ET.SubElement(inp, B)
    C="CityName"
    for i in range(len(snowing)):
        inp2=ET.SubElement(inp1, C)
        inp2.set('name',snowing[i])
        mydata=ET.tostring(root)
    myfile = open(date+".xml", "w")
    myfile.write(str(BeautifulSoup(mydata, "xml").prettify()))
    
#The process repeates so the comments are unecacery
    A="IceWeather"                                                             #Assigns the IceWeather brand to A
    inp=ET.SubElement(root, A)
    B="cities"
    inp1=ET.SubElement(inp, B)
    C="CityName"
    for i in range(len(ice)):
        inp2=ET.SubElement(inp1, C)
        inp2.set('name',ice[i])
        mydata=ET.tostring(root)
    myfile = open(date+".xml", "w")
    myfile.write(str(BeautifulSoup(mydata, "xml").prettify()))  

    myfile.close()                                                             #Closes and saves the file

    message = "File created for "+date                                         #Creates a "done" message
    return message                                                             #Returns the message

'''
Main function to allow functions in this program
'''
if __name__ == "__main__":
    cityAllowcation()                                                           #Calls the initial function to start the program
