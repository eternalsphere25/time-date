#------------------------------------------------------------------------------
# List of IANA time zones can be found at the following link:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
#
# strftime format codes:
# https://docs.python.org/3/library/datetime.html
# #strftime-and-strptime-format-codes
#
#------------------------------------------------------------------------------

import dateutil
import holidays
import pyexcel_ods3
import pycountry
import tzlocal
from datetime import datetime, time
from dateutil.relativedelta import *
from general_functions import *
from zoneinfo import ZoneInfo
import timezone_diff_calc
import calendar

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
        self.day_name = self.datetime.strftime("%A")
        self.day_name_abbrv = self.datetime.strftime("%a")

    def calc_elapsed_time(self):
        time_now = get_datetime_now_with_timezone_local()
        self.elapsed_time = relativedelta(time_now, self.datetime)

    def calc_remaining_time(self):
        time_now = get_datetime_now_with_timezone_local()
        self.remaining_time = relativedelta(self.datetime, time_now)

    def print_elapsed_time(self):
        total_sec = combine_sec_and_microsec(
                    self.elapsed_time.seconds,self.elapsed_time.microseconds)
        print(f'{self.elapsed_time.years} Years, '
              f'{self.elapsed_time.months} Months, '
              f'{self.elapsed_time.days} Days, '
              f'{self.elapsed_time.hours} Hours, '
              f'{self.elapsed_time.minutes} Minutes, '
              f'{total_sec} Seconds')

    def print_remaining_time(self):
        total_sec = combine_sec_and_microsec(
                    self.remaining_time.seconds,
                    self.remaining_time.microseconds)
        print(f'{self.remaining_time.years} Years, '
              f'{self.remaining_time.months} Months, '
              f'{self.remaining_time.days} Days, '
              f'{self.remaining_time.hours} Hours, '
              f'{self.remaining_time.minutes} Minutes, '
              f'{total_sec} Seconds')



class Person:
    def __init__(self, input_data_list, input_name):
        self.name = input_name
        self.age_data = extract_single_event_data(input_data_list, input_name)
        self.age_datetime = build_datetime_object_from_components(self.age_data)

    def calculate_age(self):
        time_now = get_datetime_now_with_timezone_local()
        self.current_age = relativedelta(time_now, self.age_datetime)

    def find_upcoming_birthday(self):
        time_now = get_datetime_now_with_timezone_local()
        birthday_this_year = self.age_datetime.replace(year=time_now.year)
        delta_time = time_now - birthday_this_year
        if delta_time.days >= 0:
            self.next_birthday = birthday_this_year + relativedelta(years=+1)
        else:
            self.next_birthday = birthday_this_year
        self.time_to_next_birthday = relativedelta(self.next_birthday, time_now)
        self.next_birthday_local_tz = self.next_birthday.astimezone(
            tz=tzlocal.get_localzone())

    def print_age(self):
        total_sec = combine_sec_and_microsec(
                    self.current_age.seconds,self.current_age.microseconds)
        if self.name == 'You':
            verb = 'are'
        else:
            verb = 'is'
        print(f'\n{self.name} {verb} currently '
              f'{self.current_age.years} years, '
              f'{self.current_age.months} months, '
              f'{self.current_age.days} days, '
              f'{self.current_age.hours} hours, '
              f'{self.current_age.minutes} minutes, and '
              f'{total_sec} seconds old')
    
    def print_next_birthday(self):
        total_sec = combine_sec_and_microsec(
                    self.time_to_next_birthday.seconds,
                    self.time_to_next_birthday.microseconds)
        print(f'\nNext Birthday ({self.name}): ')
        print(f'{self.next_birthday.strftime("%Y-%m-%d %H:%M:%S %Z")} '
              f'({self.age_datetime.tzinfo})')
        print(f'{self.next_birthday_local_tz.strftime("%Y-%m-%d %H:%M:%S %Z")} '
              f'({tzlocal.get_localzone()})')
        print(f'Time remaining: '
              f'{self.time_to_next_birthday.months} Months, '
              f'{self.time_to_next_birthday.days} Days, '
              f'{self.time_to_next_birthday.hours} Hours, '
              f'{self.time_to_next_birthday.minutes} Minutes, '
              f'{total_sec} Seconds')



class TimeDataImport:
    def __init__(self, input_file_location):
        self.event_past_raw = pyexcel_ods3.get_data(
                                input_file_location)['events_past']
        self.event_future_raw = pyexcel_ods3.get_data(
                                input_file_location)['events_future']
        self.event_recurring_raw = pyexcel_ods3.get_data(
                                   input_file_location)['events_recurring']
        self.birthday_raw = pyexcel_ods3.get_data(
                            input_file_location)['birthdays']
        self.saved_locations_raw = pyexcel_ods3.get_data(
                                    input_file_location)['saved_locations']

    def clean_input_data(self):
        self.event_past_clean = [
            row for row in self.event_past_raw if len(row) != 0]
        self.event_future_clean = [
            row for row in self.event_future_raw if len(row) != 0]
        self.event_recurring_clean = [
            row for row in self.event_recurring_raw if len(row) != 0]
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
    #Calculate year and month difference, return result as tuple with
    #separate quotient and remainder
    person1_info = person1.age_datetime.utctimetuple()
    person2_info = person2.age_datetime.utctimetuple()
    diff_years = abs(person1_info[0] - person2_info[0])
    diff_months = abs(person1_info[1] - person2_info[1])
    total_months = (diff_years*12) - diff_months
    calc_age_diff = divmod(total_months, 12)

    #Calculate older/younger/same age based on total elapsed seconds, return
    #result as a list of booleans
    older_younger_same = [False, False, False]
    older_younger_check = person1.age_datetime - person2.age_datetime
    if older_younger_check.total_seconds() < 0:
        older_younger_same[0] = True
    elif older_younger_check.total_seconds() > 0:
        older_younger_same[1] = True
    elif older_younger_check.total_seconds() == 0:
        older_younger_same[2] = True
    return calc_age_diff, older_younger_same


def print_age_diff_two_people(input_calc_age_diff, person1, person2):
    #Determine proper verb for first person
    if person1.name == 'You':
        verb = 'are'
    else:
        verb = 'is'

    #Print age difference, if any
    if input_calc_age_diff[1][2] == True:
        print(f'{person1.name} and {person2.name} are the same age')
    elif input_calc_age_diff[1][1] == True:
        print(f'{person1.name} {verb} '
              f'{input_calc_age_diff[0][0]} year(s) and '
              f'{input_calc_age_diff[0][1]} month(s) '
              f'younger then {person2.name}')
    elif input_calc_age_diff[1][0] == True:
        print(f'{person1.name} {verb} '
              f'{input_calc_age_diff[0][0]} year(s) and '
              f'{input_calc_age_diff[0][1]} month(s) '
              f'older then {person2.name}')



#-------------------------------------------------------------------------------
# Functions - Holidays
#-------------------------------------------------------------------------------

def find_holiday_date_from_name(country, year, name):
    dict_of_holidays = holidays.country_holidays(country, years=year)
    if len(dict_of_holidays.get_named(name)) == 0:
        country_info = pycountry.countries.get(alpha_2=country)
        print(f'\nWARNING: "{name}" is/may not (be) celebrated in '
              f'{country_info.name}'
              f'\n\t  Perhaps it goes by a different local name?'
              f'\n\t  Did you make sure you spelled "{name}" correctly?')
        return None
    else:
        holiday_date = dict_of_holidays.get_named(name)
        if len(holiday_date) > 1:
            for x in range(len(holiday_date)):
                holiday_name = dict_of_holidays.get(holiday_date[x])
                if 'Observed' not in holiday_name:
                    return holiday_date[x]
        else:
            return holiday_date[0]

def find_previous_and_next_holiday(country, year):
    dict_of_holidays = holidays.country_holidays(country, years=year)
    current_date = datetime.now().date()
    previous_holiday = ''
    next_holiday = ''
    for k in dict_of_holidays:
        if k < current_date:
            #print(f'{k} {current_date} PAST')
            previous_holiday = k
        elif k == current_date:
            #print(f'{k} {current_date} TODAY')
            pass
        elif k > current_date:
            #print(f'{k} {current_date} FUTURE')
            next_holiday = k
            break
    output_dict = {
        previous_holiday: dict_of_holidays[previous_holiday],
        next_holiday: dict_of_holidays[next_holiday]
        }
    return output_dict

def print_country_holidays(country, year):
    holiday_dict = holidays.country_holidays(country, years=year)
    country_info = pycountry.countries.get(alpha_2=country)
    print(f'\n{country_info.name} Holidays in {year}:')
    print_dict_line_by_line(holiday_dict)

def print_previous_and_next_holiday(input_dict, locale, year):
    item = list(input_dict.keys())

    print(f'Previous Holiday: {item[0]} ({input_dict[item[0]]})')
    print(f'Next Holiday: {item[1]} ({input_dict[item[1]]})')

    print_time_until_holiday(locale, year, input_dict[item[1]])


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
# Functions - World Time
#-------------------------------------------------------------------------------

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
          f'{current_datetime.date} ({current_datetime.day_name_abbrv.upper()})'
          f'\nThe time right now is: '
          f'{current_datetime.time} {current_datetime.tz} '
          f'({current_datetime.tz_name}) \n{dst_status}')


#-------------------------------------------------------------------------------
# Functions - Elapsed Time
#-------------------------------------------------------------------------------

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
# Functions - Remaining Time
#-------------------------------------------------------------------------------

def print_remaining_time_multiple(input_data_list):
    for x in range(len(input_data_list)):
        if x != 0:
            print_remaining_time_single(input_data_list[x])

def print_remaining_time_single(input_data_list):
    event = DateTime(
        build_datetime_object_from_components(input_data_list))
    print(f'\nTime remaining until {input_data_list[0]}: ')
    event.calc_remaining_time()
    event.print_remaining_time()


#-------------------------------------------------------------------------------
# Functions - Recurring Events
#-------------------------------------------------------------------------------

def convert_day_to_int(input_str):
    return get_list_index_from_value(list(calendar.day_name), input_str)

def print_recurring_events_multiple(input_event_data):
    for item in range(len(input_event_data)):
        if item != 0:
            event_info = input_event_data[item]
            print_recurring_events_single(event_info)

def print_recurring_events_single(input_event_data):
    day_int = convert_day_to_int(input_event_data[2])
    time_now = get_datetime_now_with_timezone_local()
    time_next = time_now + relativedelta(weekday=day_int)
    time_interval = relativedelta(time_next, time_now)
    print(f'\n{input_event_data[0]} occurs '
            f'{input_event_data[1]} on {input_event_data[2]}s')
    print(f'Today is: {time_now.date()} '
            f'({time_now.strftime("%a").upper()})')
    print(f'The next time this will happen is: {time_next.date()} '
            f'({time_next.strftime("%a").upper()})')
    if time_now == time_next:
        print('That would be today...')
    else:
        print(f'That would be {time_interval.days} day(s) from now')


#-------------------------------------------------------------------------------
# Functions - Shared
#-------------------------------------------------------------------------------

def clean_input_ods_raw_data(input_raw_data):
    return [row for row in input_raw_data if len(row) != 0]

def combine_sec_and_microsec(input_sec, input_microsec):
    return input_sec + (input_microsec/1000000)

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
    #Note: to get the timezone as a string call .tzinfo._filename on the object


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

#Print all past event time
print_remaining_time_multiple(timedata.event_future_clean)

#Grab specific birthday information
birthday_info = extract_single_event_data(timedata.birthday_clean, 'You')

#Print single event
print_time_have_been_for(birthday_info, ['You', 'alive'])

california_free = extract_single_event_data(
    timedata.event_past_clean, 'Last Time in California')
print_time_have_been_for(california_free, ['You', 'California-free'])

current_year = int(get_datetime_now_with_timezone_local().strftime("%Y"))
print_country_holidays('US', current_year)
print_country_holidays('JP', current_year)

print_time_until_holiday('US', current_year, 'Christmas')
print_time_until_holiday('US', current_year+1, "New Year's")

print_time_until_holiday('JP', current_year, '勤労感謝の日')

print('\nPrevious and Next Holiday in the US:')
print_previous_and_next_holiday(
    find_previous_and_next_holiday('US', current_year), 'US', current_year)

print('\nPrevious and Next Holiday in Japan:')
print_previous_and_next_holiday(
    find_previous_and_next_holiday('JP', current_year), 'JP', current_year)

#find_time_diff_between_two_locations()

#Sample code for person age calculations
reiko = Person(timedata.birthday_clean, 'Reiko')
reiko.calculate_age()
reiko.print_age()

you = Person(timedata.birthday_clean, 'You')
you.calculate_age()
you.print_age()

age_diff = calc_age_diff_two_people(reiko, you)
print_age_diff_two_people(age_diff, reiko, you)

age_diff = calc_age_diff_two_people(you, reiko)
print_age_diff_two_people(age_diff, you, reiko)

#Sample code to display recurring events
print_recurring_events_multiple(timedata.event_recurring_clean)

#Sample code to calculate time until next birthday
you.find_upcoming_birthday()
reiko.find_upcoming_birthday()

you.print_next_birthday()
reiko.print_next_birthday()