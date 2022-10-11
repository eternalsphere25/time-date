#------------------------------------------------------------------------------
# List of IANA time zones can be found at the following link:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
#------------------------------------------------------------------------------


import datetime
import holidays
import zoneinfo
import pyexcel_ods3
import math
import pycountry
from general_functions import *
import geopy
import timezonefinder


class DateTime:
    def __init__(self, input_datetime):
        self.datetime = input_datetime
        self.date = self.datetime.date()
        self.time = self.datetime.timetz().strftime("%H:%M:%S")
        self.tz = self.datetime.strftime("%z")
        self.dst_offset = self.datetime.dst()

    def get_tz_abbrv(self, input_timezone):
        if self.dst_offset.seconds == 0:
            return self.tz_abbrv_dict[str(input_timezone)][0]
        else:
            return self.tz_abbrv_dict[str(input_timezone)][1]

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

    tz_abbrv_dict = {
    "America/New_York": ('EST', 'EDT'),
    "America/Los_Angeles": ('PST', 'PDT'),
    "Asia/Tokyo": ('JST', 'JST'),
    "Asia/Manila": ('PST', 'PST'),
    "Asia/Ulaanbaatar": ('MST', 'MST'),
    "Europe/Amsterdam": ('CET', 'CEST'),
    "Asia/Singapore": ('SST', 'SST'),
    "Asia/Shanghai": ('CST', 'CST'),
    "Australia/Sydney": ('AEST', 'AEDT'),
    }

class WorldTimeZoneInfo:
    def __init__(self):
        self.local = self.tz_IATA[
                        str(datetime.datetime.now().astimezone().tzinfo)]
        self.new_york = zoneinfo.ZoneInfo("America/New_York")
        self.los_angeles = zoneinfo.ZoneInfo("America/Los_Angeles")
        self.tokyo = zoneinfo.ZoneInfo("Asia/Tokyo")
        self.manila = zoneinfo.ZoneInfo("Asia/Manila")
        self.ulaanbaatar = zoneinfo.ZoneInfo("Asia/Ulaanbaatar")
        self.amsterdam = zoneinfo.ZoneInfo("Europe/Amsterdam")
        self.singapore = zoneinfo.ZoneInfo("Asia/Singapore")
        self.shanghai = zoneinfo.ZoneInfo("Asia/Shanghai")
        self.sydney = zoneinfo.ZoneInfo("Australia/Sydney")

    tz_IATA = {"Tokyo Standard Time": 'Asia/Tokyo'}



def build_datetime_object_from_components(input_list):
    date = datetime.datetime.strptime(input_list[1], f"%Y/%m/%d").date()
    time = input_list[2]
    tz = zoneinfo.ZoneInfo(input_list[3])
    return datetime.datetime.combine(date, time, tzinfo=tz)

def extract_single_event_data(input_data, search_str):
    for x in range(len(input_data)):
        selected_row = input_data[x]
        if selected_row[0] == search_str:
            output_list = selected_row
    return output_list

def find_holiday_date_from_name(country, year, name):
    list_of_holidays = holidays.country_holidays(country, years=year)
    if len(list_of_holidays.get_named(name)) == 0:
        country_info = pycountry.countries.get(alpha_2=country)
        print(f'\nWARNING: "{name}" is not celebrated in {country_info.name}'
              f'\n\t  Perhaps it goes by a different local name?'
              f'\n\t  Did you make sure you spelled "{name}" correctly?')
        return None
    else:
        holiday_date = list_of_holidays.get_named(name)
        if len(holiday_date) > 1:
            for x in range(len(holiday_date)):
                holiday_name = list_of_holidays.get(holiday_date[x])
                if 'Observed' not in holiday_name:
                    return holiday_date[x]
        else:
            return holiday_date[0]

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

def format_timedelta_to_readable_string(input_timedelta):
    time_data = input_timedelta
    weeks = math.floor(time_data.days/7)
    days = time_data.days - (weeks*7)
    hours = math.floor(time_data.seconds/3600)
    minutes = math.floor((time_data.seconds - (hours*3600))/60)
    seconds = time_data.seconds - (hours*3600) - (minutes*60)
    return (f'{weeks} Weeks, {days} Days, {hours} Hours, '
            f'{minutes} Minutes, {seconds} Seconds')    

def print_all_saved_locations():
    #Get system time zone
    print_current_time('Local Time', zoneinfo.ZoneInfo(tz.local))
    print_current_time('Tokyo, JP', tz.tokyo)
    print_current_time('New York, NY', tz.new_york)
    print_current_time('Los Angeles, CA', tz.los_angeles)
    print_current_time('Ulaanbaatar, MN', tz.ulaanbaatar)
    print_current_time('Manila, PH', tz.manila)
    print_current_time('Amsterdam, NL', tz.amsterdam)
    print_current_time('Singapore, SG', tz.singapore)
    print_current_time('Shanghai, CN', tz.shanghai)
    print_current_time('Sydney, NSW', tz.sydney)

def print_country_holidays(country, year):
    holiday_dict = holidays.country_holidays(country, years=year)
    country_info = pycountry.countries.get(alpha_2=country)
    print(f'\n{country_info.name} Holidays in {year}:')
    print_dict_line_by_line(holiday_dict)

def print_current_time(location, timezone):
    #Get current time
    current_datetime = DateTime(datetime.datetime.now().astimezone(timezone))

    #Print out location, date, time, and DST offset
    print(f'\nLocation: {location}')
    print(f'Today\'s date is: '
        f'{current_datetime.date}')
    if current_datetime.dst_offset.seconds == 0:
        print(f'The time right now is: '
            f'{current_datetime.time} {current_datetime.tz} '
            f'({current_datetime.get_tz_abbrv(timezone)})')
        print('DST currently not in effect')
    else:
        print(f'The time right now is: '
            f'{current_datetime.time} {current_datetime.tz} '
            f'({current_datetime.get_tz_abbrv(timezone)})')
        print(f'DST offset: {current_datetime.dst_offset}')

def print_elapsed_time_multiple(input_data_list):
    for x in range(len(input_data_list)):
        if x == 0:
            pass
        else:
            selected_row = input_data_list[x]
            event = DateTime(
                build_datetime_object_from_components(selected_row))
            print(f'\nTime elapsed since {selected_row[0]}: '
                f'\n{event.print_elapsed_time()}')

def print_elapsed_time_single(input_data_list):
    event = DateTime(
        build_datetime_object_from_components(input_data_list))
    print(f'\nTime elapsed since {input_data_list[0]}: '
        f'\n{event.print_elapsed_time()}')

def print_time_have_been_for(input_data_list, input_str):
    event = DateTime(
        build_datetime_object_from_components(input_data_list))
    print(f'\n{input_str[0]} have been {input_str[1]} for: '
        f'\n{event.print_elapsed_time()}')

def print_time_until_holiday(locale, year, name):
    event_date = find_holiday_date_from_name(locale, year, name)
    if event_date != None:
        event_datetime = datetime.datetime.combine(
                            event_date, datetime.time(0,0,0))
        difference = event_datetime - datetime.datetime.now()
        print(f'\nTime until {name}: '
              f'\n{format_timedelta_to_readable_string(difference)}')
    else:
        pass

#-------------------------------------------------------------------------------
# 0. Global Definitions
#-------------------------------------------------------------------------------

#Generate world time zone object
tz = WorldTimeZoneInfo()

#Define event/birthday info file
event_time_info = ("D:\その他\Python Scripts\info_files\clock_info.ods")


#-------------------------------------------------------------------------------
# 1. Driver Code
#-------------------------------------------------------------------------------

#Display every clock saved in memory
print_all_saved_locations()

#Grab event/birthday information
event_past_data_raw = pyexcel_ods3.get_data(event_time_info)['events_past']
event_future_data_raw = pyexcel_ods3.get_data(event_time_info)['events_future']
birthday_data_raw = pyexcel_ods3.get_data(event_time_info)['birthdays']

#Print all past event time
print_elapsed_time_multiple(event_past_data_raw)

#Grab specific birthday information
birthday_info = extract_single_event_data(birthday_data_raw, 'You')

#Print single event
print_time_have_been_for(birthday_info, ['You', 'alive'])

california_free = extract_single_event_data(
    event_past_data_raw, 'Last Time in California')
print_time_have_been_for(california_free, ['You', 'California-free'])


print_country_holidays('US', 2020)
print_country_holidays('JP', 2022)

print_time_until_holiday('US', 2022, 'Christmas')
print_time_until_holiday('US', 2023, "New Year's")

print_time_until_holiday('JP', 2022, '勤労感謝の日')

find_time_diff_between_two_locations()