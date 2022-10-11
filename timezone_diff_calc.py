#-------------------------------------------------------------------------------
# This program calculates and displays the time difference between two 
# geographic locations (cities, towns, etc)
#
#
# Changelog
#
# Version 1.0
# 10/11/2022
# + New Features
#   - Wrote the program
#------------------------------------------------------------------------------

import datetime
import geopy
import math
import timezonefinder
import zoneinfo


#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class DateTime:
    def __init__(self, input_datetime):
        self.datetime = input_datetime
        self.date = self.datetime.date()
        self.time = self.datetime.timetz().strftime("%H:%M:%S")
        self.tz = self.datetime.strftime("%z")
        self.dst_offset = self.datetime.dst()

    def calc_elapsed_time(self):
        current_time = datetime.datetime.now().astimezone()
        return (current_time - self.datetime)

    def print_elapsed_time(self):
        time_data = self.calc_elapsed_time()
        weeks = math.floor(time_data.days/7)
        days = time_data.days - (weeks*7)
        hours = math.floor(time_data.seconds/3600)
        minutes = math.floor((time_data.seconds - (hours*3600))/60)
        seconds = time_data.seconds - (hours*3600) - (minutes*60)
        return (f'{weeks} Weeks, {days} Days, {hours} Hours, '
                f'{minutes} Minutes, {seconds} Seconds')


#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

def find_time_diff_between_two_locations():
    #Find time difference between two cities/towns/villages/hamlets
    loc1 = input('\nEnter first city/town/village/hamlet name: ')
    loc2 = input('Enter second city/town/village/hamlet name: ')

    #Confirm input
    print(f'\nConfirmation: \nLocation #1: {loc1} \nLocation #2: {loc2}')
    choice = input('\nProceed? y/n ')

    if choice == 'n':
        print('Input cancelled')
    elif choice == 'y':
        #Initialize objects, one for each location
        tz1 = zoneinfo.ZoneInfo(find_timezone_from_location_name(loc1))
        tz2 = zoneinfo.ZoneInfo(find_timezone_from_location_name(loc2))

        if tz1 != None and tz2 != None:
            #Print the date and time at both locations
            loc1_time = DateTime(datetime.datetime.now().astimezone(tz1))
            loc2_time = DateTime(datetime.datetime.now().astimezone(tz2))
            print(f'\nCurrent Time in {loc1}:'
                f'\n\t{loc1_time.date} {loc1_time.time}')
            print(f'Current Time in {loc2}:'
                f'\n\t{loc2_time.date} {loc2_time.time}')     

            #Calculate time difference
            print('\nCalculating time difference...')
            loc1_offset = int(loc1_time.tz)/100
            loc2_offset = int(loc2_time.tz)/100
            time_difference = (loc1_offset - loc2_offset)

            #Print time difference
            if time_difference > 0:
                print(f'{loc1} is {time_difference:.2f} hour(s) ahead of '
                      f'{loc2}')
            elif time_difference < 0:
                print(f'{loc1} is {time_difference:.2f} hour(s) behind {loc2}')
            else:
                print(f'There is no time difference between {loc1} and {loc2}')

def find_timezone_from_location_name(input_loc):
    #Set up geolocation service
    geolocator = geopy.geocoders.Nominatim(
                    user_agent='personal_timezone_project')

    #Pull location data of the input city/town/village/hamlet
    loc_data = geolocator.geocode(input_loc)

    if loc_data == None:
        print(f'ERROR: {input_loc} does not exist!')
    else:
        #Find timezone based on latitude and longitude coordinates
        tz_finder = timezonefinder.TimezoneFinder()
        tz_result = tz_finder.timezone_at(
                        lng = loc_data.longitude, lat=loc_data.latitude)
        
        print(f'\nLocation Search Result:\n{loc_data}\nLat: {loc_data.latitude} Long: {loc_data.longitude}\nTime Zone: {tz_result}')

        return tz_result


#-------------------------------------------------------------------------------
# Driver Code - Uncomment below to run directly
#-------------------------------------------------------------------------------

find_time_diff_between_two_locations()