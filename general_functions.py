import re

#------------------------------------------------------------------------------
# DATABASE FUNCTIONS
#------------------------------------------------------------------------------

def get_tables_in_database(cursor):
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    cursor.execute(query)
    results = cursor.fetchall()
    table_names = [item[0] for item in results]
    return table_names

def execute_query_prompt(input_query):
    print('\nSQL Query:\n')
    print(f'\t{input_query}')
    output_decision = input('\nExecute? y/n: ')
    return output_decision

def locate_database(db_location, db_name):
    path = f'{db_location}\\{db_name}'
    return path

def locate_database_manual():
    print('\nInput existing database (1) file path and (2) name: ')
    db_location = input('1. File Path: ')
    file_name = input('2. Database Name (do not include ".db"): ')
    path = f'{db_location}\\{file_name}.db'
    return path 


#------------------------------------------------------------------------------
# DICT FUNCTIONS
#------------------------------------------------------------------------------

def get_dict_key_from_val(input_dict, input_val):
    for key, value in input_dict.items():
        if input_val in value:
            return key
    return f'ERROR: {input_val} does not exist'


#------------------------------------------------------------------------------
# LIST FUNCTIONS
#------------------------------------------------------------------------------

def get_list_index_from_value(input_list, input_str):
    return input_list.index(input_str)


#------------------------------------------------------------------------------
# PRINT FUNCTIONS
#------------------------------------------------------------------------------

def print_as_bulleted_list_no_caps(input_list):
	for x in range(len(input_list)):
		print('* ' + str(input_list[x]))

def print_as_list(input_list):
	for x in range(len(input_list)):
		print(str(input_list[x]))

def print_dict_line_by_line(input_dict):
    for key, value in input_dict.items():
        print(f'{key}: {value}')

def print_set_line_by_line(input_set):
    for item in input_set:
        print(item)

#------------------------------------------------------------------------------
# REGEX FUNCTIONS
#------------------------------------------------------------------------------

def regex_search(input_text, search_str):
    item_found = re.search(search_str, input_text)
    if item_found == None:
        return None
    else:
        return item_found.group(0)