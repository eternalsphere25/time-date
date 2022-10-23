#------------------------------------------------------------------------------
# List of IANA time zones can be found at the following link:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
#------------------------------------------------------------------------------

import dateutil
import holidays
import pyexcel_ods3
import math
import pycountry
import tzlocal
from datetime import datetime, time
from dateutil.relativedelta import *
from general_functions import *
from zoneinfo import ZoneInfo
import timezone_diff_calc

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class DateTime:
    def __init__(self, input_datetime):
        self.datetime = input_datetime
        self.date = self.datetime.date()
        self.time = self.datetime.timetz().strftime("%H:%M:%S")
        self.tz = self.datetime.strftime("%z")
        self.tz_name = self.datetime.strftime("%Z")
        self.dst_offset = self.datetime.dst()

    def calc_elapsed_time(self):
        time_now = get_datetime_now_with_timezone_local()
        self.elapsed_time = relativedelta(time_now, self.datetime)

    def print_elapsed_time(self):
        print(f'{self.elapsed_time.years} Years, '
              f'{self.elapsed_time.months} Months, '
              f'{self.elapsed_time.days} Days, '
              f'{self.elapsed_time.hours} Hours, '
              f'{self.elapsed_time.minutes} Minutes, '
              f'{self.elapsed_time.seconds} Seconds')


class Person:
    def __init__(self, input_data_list, input_name):
        self.name = input_name
        self.age_data = extract_single_event_data(input_data_list, input_name)
        self.age_datetime = build_datetime_object_from_components(self.age_data)

    def calculate_age(self):
        time_now = get_datetime_now_with_timezone_local()
        self.current_age = relativedelta(time_now, self.age_datetime)

    def print_age(self):
        if self.name == 'You':
            verb = 'are'
        else:
            verb = 'is'
        print(f'\n{self.name} {verb} currently '
              f'{self.current_age.years} years, '
              f'{self.current_age.months} months, '
              f'{self.current_age.days} days, '
              f'{self.current_age.hours} hours, '
              f'{self.current_age.minutes} minutes, '
              f'{self.current_age.seconds} seconds, and '
              f'{self.current_age.microseconds} microseconds old')
           

class TimeDataImport:
    def __init__(self, input_file_location):
        self.event_past_raw = pyexcel_ods3.get_data(
                                input_file_location)['events_past']
        self.event_future_raw = pyexcel_ods3.get_data(
                                input_file_location)['events_future']
        self.birthday_raw = pyexcel_ods3.get_data(
                            input_file_location)['birthdays']
        self.saved_locations_raw = pyexcel_ods3.get_data(
                                    input_file_location)['saved_locations']

    def clean_input_data(self):
        self.event_past_clean = [
            row for row in self.event_past_raw if len(row) != 0]
        self.event_future_clean = [
            row for row in self.event_future_raw if len(row) != 0]
        self.birthday_clean = [
            row for row in self.birthday_raw if len(row) != 0]
        self.saved_locations_clean = [
            row for row in self.saved_locations_raw if len(row) != 0]


#-------------------------------------------------------------------------------
# Functions - Event Info Extraction
#-------------------------------------------------------------------------------

def build_datetime_object_from_components(input_list):
    date = datetime.strptime(input_list[1], f"%Y/%m/%d").date()
    time = input_list[2]
    tz = ZoneInfo(input_list[3])
    return datetime.combine(date, time, tzinfo=tz)

def extract_single_event_data(input_data, search_str):
    for x in range(len(input_data)):
        selected_row = input_data[x]
        if selected_row[0] == search_str:
            output_list = selected_row
    return output_list


#-------------------------------------------------------------------------------
# Functions - Age Calculations for People
#-------------------------------------------------------------------------------

def calc_age_diff_two_people(person1, person2):
    time_diff = person1.current_age - person2.current_age
    older_younger = person1.age_datetime - person2.age_datetime
    return time_diff, older_younger

def print_age_diff_two_people(input_calc_age_diff, person1, person2):
    if input_calc_age_diff[1].total_seconds() == 0:
        print(f'{person1.name} and {person2.name} are the same age')
    else:
        #Determine 'older' or 'younger' message
        if input_calc_age_diff[1].total_seconds() < 0:
            old_young = 'older'
        elif input_calc_age_diff[1].total_seconds() > 0:
            old_young = 'younger'
        #Determine proper verb for first person
        if person1.name == 'You':
            verb = 'are'
        else:
            verb = 'is'
        #Print age difference
        print(f'\n{person1.name} {verb} '
              f'\n{input_calc_age_diff[0].years} years, '
              f'{input_calc_age_diff[0].months} months, '
              f'{input_calc_age_diff[0].days} days, '
              f'{input_calc_age_diff[0].hours} hours, '
              f'{input_calc_age_diff[0].minutes} minutes, '
              f'{input_calc_age_diff[0].seconds} seconds, and '
              f'{input_calc_age_diff[0].microseconds} microseconds '
              f'\n{old_young} than {person2.name}')


#-------------------------------------------------------------------------------
# Functions - Holidays
#-------------------------------------------------------------------------------

def print_country_holidays(country, year):
    holiday_dict = holidays.country_holidays(country, years=year)
    country_info = pycountry.countries.get(alpha_2=country)
    print(f'\n{country_info.name} Holidays in {year}:')
    print_dict_line_by_line(holiday_dict)

def print_time_until_holiday(locale, year, name):
    event_date = find_holiday_date_from_name(locale, year, name)
    if event_date != None:
        event_datetime = datetime.combine(
                            event_date, time(0,0,0))
        difference = relativedelta(event_datetime, datetime.now())
        print(f'\nTime until {name}: '
              f'\n{difference.years} Years, '
              f'{difference.months} Months, '
              f'{difference.days} Days, '
              f'{difference.hours} Hours, '
              f'{difference.minutes} Minutes, '
              f'{difference.seconds} Seconds')


#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

def clean_input_ods_raw_data(input_raw_data):
    return [row for row in input_raw_data if len(row) != 0]

def find_holiday_date_from_name(country, year, name):
    list_of_holidays = holidays.country_holidays(country, years=year)
    if len(list_of_holidays.get_named(name)) == 0:
        country_info = pycountry.countries.get(alpha_2=country)
        print(f'\nWARNING: "{name}" is/may not (be) celebrated in '
              f'{country_info.name}'
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

"""
def format_timedelta_object_to_readable_string(input_timedelta):
    time_data = input_timedelta
    weeks = math.floor(time_data.days/7)
    days = time_data.days - (weeks*7)
    hours = math.floor(time_data.seconds/3600)
    minutes = math.floor((time_data.seconds - (hours*3600))/60)
    seconds = time_data.seconds - (hours*3600) - (minutes*60)
    return (f'{weeks} Weeks, {days} Days, {hours} Hours, '
            f'{minutes} Minutes, {seconds} Seconds')    
"""

def get_datetime_now_with_timezone_local():
    return datetime.now(dateutil.tz.gettz(str(tzlocal.get_localzone())))

def print_all_saved_locations(input_location_data):
    for item in range(len(input_location_data)):
        if item == 0:
            print_current_time('Local Time', tzlocal.get_localzone())
        else:
            current_item = input_location_data[item]
            location_name = f'{current_item[0]}, {current_item[1]}'
            timezone_name = current_item[2]
            print_current_time(location_name, ZoneInfo(timezone_name))

def print_current_time(location, timezone):
    #Get current time
    current_datetime = DateTime(datetime.now().astimezone(timezone))

    #Print out location, date, time, and DST offset
    if current_datetime.dst_offset.seconds == 0:
        dst_status = 'DST is currently not in effect'
    else:
        dst_status = f'DST offset: {current_datetime.dst_offset}'
    print(f'\nLocation: {location}'
          f'\nToday\'s date is: '
          f'{current_datetime.date}'
          f'\nThe time right now is: '
          f'{current_datetime.time} {current_datetime.tz} '
          f'({current_datetime.tz_name}) \n{dst_status}')

def print_elapsed_time_multiple(input_data_list):
    for x in range(len(input_data_list)):
        if x != 0:
            print_elapsed_time_single(input_data_list[x])

def print_elapsed_time_single(input_data_list):
    event = DateTime(
        build_datetime_object_from_components(input_data_list))
    print(f'\nTime elapsed since {input_data_list[0]}: ')
    event.calc_elapsed_time()
    event.print_elapsed_time()

def print_time_have_been_for(input_data_list, input_str):
    event = DateTime(
        build_datetime_object_from_components(input_data_list))
    print(f'\n{input_str[0]} have been {input_str[1]} for: ')
    event.calc_elapsed_time()
    event.print_elapsed_time()


#-------------------------------------------------------------------------------
# 0. Global Definitions
#-------------------------------------------------------------------------------

#Define event/birthday info file
event_time_info = ("D:\その他\Python Scripts\info_files\clock_info.ods")


#-------------------------------------------------------------------------------
# 1. Driver Code
#-------------------------------------------------------------------------------

#Import event/birthday/location etc information and clean the input
timedata = TimeDataImport(event_time_info)
timedata.clean_input_data()

#Display every clock saved in memory
print_all_saved_locations(timedata.saved_locations_clean)

#Print all past event time
print_elapsed_time_multiple(timedata.event_past_clean)

#Grab specific birthday information
birthday_info = extract_single_event_data(timedata.birthday_clean, 'You')

#Print single event
print_time_have_been_for(birthday_info, ['You', 'alive'])

california_free = extract_single_event_data(
    timedata.event_past_clean, 'Last Time in California')
print_time_have_been_for(california_free, ['You', 'California-free'])


print_country_holidays('US', 2020)
print_country_holidays('JP', 2022)

print_time_until_holiday('US', 2022, 'Christmas')
print_time_until_holiday('US', 2023, "New Year's")

print_time_until_holiday('JP', 2022, '勤労感謝の日')

#find_time_diff_between_two_locations()

#Sample code for person age calculations
mom = Person(timedata.birthday_clean, 'Mom')
mom.calculate_age()
mom.print_age()

you = Person(timedata.birthday_clean, 'You')
you.calculate_age()
you.print_age()


age_diff = calc_age_diff_two_people(mom, you)
print_age_diff_two_people(age_diff, mom, you)

age_diff = calc_age_diff_two_people(you, mom)
print_age_diff_two_people(age_diff, you, mom)




