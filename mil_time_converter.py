#------------------------------------------------------------------------------
# Converts civilian time to military time and vice versa
# Based on personal experience from time spent in US Naval R&D
#------------------------------------------------------------------------------

from datetime import datetime
import general_functions as gf


def convert_to_12_hr(input_string):
    original_hr_min = input_string.split(':')
    if int(original_hr_min[0]) > 12:
        new_hour = int(original_hr_min[0]) - 12
        new_time = f'{str(new_hour)}:{original_hr_min[1]} PM'
    else:
        new_hour = original_hr_min[0][1:]
        new_time = f'{new_hour}:{original_hr_min[1]} AM'
    return new_time

def convert_to_24_hr(input_string):
    am_or_pm = input_string.split(' ')[1]
    if am_or_pm == 'AM':
        new_time = input_string.split(' ')[0]
        hour_check = new_time.split(':')[0]
        if len(hour_check) == 1:
            new_time = f'0{new_time}'
    else:
        new_time = input_string.split(' ')[0]
        original_hr_min = new_time.split(':')
        new_hour = 12 + int(original_hr_min[0])
        new_time = f'{str(new_hour)}:{original_hr_min[1]}'
    return new_time

def convert_from_DTG(input_time):
    day = input_time[:2]
    hour = input_time[2:4]
    minute = input_time[4:6]
    tz = f'{timezone_letter[input_time[6:7]]}:00'
    month = f'{month_number[input_time[7:10]]}'
    year = input_time[10:]
    output_time = f'{year}-{month}-{day} {hour}:{minute} {tz}'
    return output_time

def convert_to_DTG(input_time):
    day = input_time.strftime("%d")
    hour = input_time.strftime("%H")
    minute = input_time.strftime("%M")
    tz = gf.get_dict_key_from_val(
        timezone_letter, input_time.strftime("%z")[:3])
    month = input_time.strftime("%b").upper()
    year = input_time.strftime("%Y")
    dtg = f'{day}{hour}{minute}{tz}{month}{year}'
    return dtg


timezone_letter = {
    'A': '+01',
    'B': '+02',
    'C': '+03',
    'D': '+04',
    'E': '+05',
    'F': '+06',
    'G': '+07',
    'H': '+08',
    'I': '+09',
    'K': '+10',
    'L': '+11',
    'M': '+12',
    'N': '-01',
    'O': '-02',
    'P': '-03',
    'Q': '-04',
    'R': '-05',
    'S': '-06',
    'T': '-07',
    'U': '-08',
    'V': '-09',
    'W': '-10',
    'X': '-11',
    'Y': '-12',
    'Z': '00'
    }

month_number = {
    'JAN': '01',
    'FEB': '02',
    'MAR': '03',
    'APR': '04',
    'MAY': '05',
    'JUN': '06',
    'JUL': '07',
    'AUG': '08',
    'SEP': '09',
    'OCT': '10',
    'NOV': '11',
    'DEC': '12'
    }

"""
test_string_12 = '3:07 AM'
test_string_24 = '03:07'

converted_time_24 = convert_to_24_hr(test_string_12)

print(f'Civilian Time: {test_string_12}')
print(f'Military Time: {converted_time_24}')

converted_time_12 = convert_to_12_hr(test_string_24)

print(f'Military Time: {test_string_24}')
print(f'Civilian Time: {converted_time_12}')
"""





time_now = datetime.now().astimezone()





#Convert to/from DTG
converted_to_DTG = convert_to_DTG(time_now)
converted_from_DTG = convert_from_DTG(converted_to_DTG)

print(f'Current Date and Time: {time_now}')
print(f'DTG: {converted_to_DTG}')
print(f'Back to Normal:{converted_from_DTG}')