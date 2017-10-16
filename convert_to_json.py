#!/usr/bin/env python3

import json
import re

def all_columns_to_json (column_dict, columns_line):    
    json_object = {}    

    for column_index, column_value in enumerate(columns_line):
        if column_index in column_dict:
            column_name = column_dict[column_index]
        else:
            column_name = str(column_index)
            
        json_object[column_name] = column_value
        
    return json_object
         

def filter_columns_in_dict_to_json(column_dict, columns_line):
    '''Parse columns_line, make sure every element in column_dict
       exists there, filter elements that are not in column_dict from 
       columns_line, and convert it to a dict.
    '''
    json_object = {}    
    
    for column_index, column_name in column_dict.items():
        try:
            json_object[column_name] = columns_line[column_index]
        except IndexError as err:
            # columns_line doesn't has column_index.
        
            raise ValueError('Invalid table line ({}) : no {} element.'.format(columns_line,
                                                                               column_index)) from err     
                                                                               
    return json_object
            
def columns_line_to_json (column_dict, columns_line, should_filter_colunms):
    '''Parse a list of values to a json object with special names.
    '''
    
    if should_filter_colunms:
        return filter_columns_in_dict_to_json(column_dict, columns_line)
    else:
        return all_columns_to_json(column_dict, columns_line)

def regex_from_delims_list(delims_list):
    '''Get a regex compiled pattern from a delims list'''    
    
    one_characters_delims = ''
    final_pattern = ''
            
    for delim in delims_list:
        delim_and_maybe_min_max = delim.split(':')
        
        escaped_delim = re.escape(delim_and_maybe_min_max[0])
        
        # Check if this is a delim without min count.
        if len(delim_and_maybe_min_max) == 1:
            final_pattern += "%s{1,}|" % (escaped_delim)
        elif len(delim_and_maybe_min_max) == 2:
            min_and_maybe_max = delim_and_maybe_min_max[1].split('-')
            
            current_pattern = escaped_delim
            
            # Add count to the regex (only min or max too)
            if len(min_and_maybe_max) == 2:
                current_pattern += '{%d,%d}' % (int(min_and_maybe_max[0],
                                                int(min_and_maybe_max[1])))
            else:
                current_pattern += '{%d,}' % (int(min_and_maybe_max[0]))
                
            final_pattern += current_pattern + '|'
        else:
            raise ValueError("Invalid ':' count in the delimiter argument")

        # If there are one character delims without count, add them. If not
        # Remove the last OR ('|').
  
        final_pattern = final_pattern[:-1]
            
        return re.compile (final_pattern)
        

def main(args):
    column_dict = {}    
    
    # Split the user's argument by a comma, and parse each columns
    # seperatly.
    for column_and_name in args.columns_and_names.split(','):
        # Split the name from the columns.
        column_and_name = column_and_name.split('=')
        if len(column_and_name) > 2:
            raise ValueError("Invalid column: {}".format(str(column_and_name())))
            
        # If there is not name, set it to the column index.
        if len(column_and_name) == 1:
            column_and_name.append (str(column_and_name[0]))
        
        # Try to convert the column index is it isn't '*'
        if column_and_name[0] != '*':
            try:
                column_and_name[0] = int(column_and_name[0])
            except ValueError as err:
                raise ValueError('Invalid column index: {} (not an integer)'.format(column_and_name[0])) from err
        
        # Add this column definition. 
        column_dict[column_and_name[0]] = column_and_name[1]
   

    # Check if column_dict has the '*' member.
    # If it does, we will print all of the columns (even ones that
    # are not in column_dict)
    should_filter_colunms = ('*' not in column_dict)
    
    # We have checked it, no need for it now.
    if not should_filter_colunms:
        del column_dict['*']

    # Parse the delim list into a regex pattern.
    strip_regex_pattern = regex_from_delims_list(args.delim)

    json_objects_list = []    
    
    for fd in args.infiles:
        for line in fd:
            # Convert bytes object to string.
            if isinstance(line, bytes): 
                line = line.decode('utf-8')
            
            # Strip the \n in the end of the line.
            line = line.rstrip('\n')            

            # Split the line by the delims.
            splitted_line = re.split(strip_regex_pattern, line)
            
            json_objects_list.append (columns_line_to_json (column_dict, splitted_line, should_filter_colunms))
            
    print(json.dumps (json_objects_list))
            

def comma_list(string):
    '''Convert a comma list '1,2,3,4' to a list
    [1,2,3,4] with escaping of , by a one \\ char'''
    
    # Split the string by commas after non-\ chars.
    splitted_string = re.split('(?<!\\\\),', string)
    
    replaced_string = []    
        
    # Replace '\,' with ',' and '\\' with '\'.
    for string in splitted_string:
        string = string.replace ('\\,', ',')
        string = string.replace ('\\\\', '\\')
    
        replaced_string.append (string)    

    print(replaced_string)

    return replaced_string

if __name__ == '__main__':
    import argparse    
    from sys import stdin
    
    parser = argparse.ArgumentParser()
    parser.add_argument('columns_and_names', help='The columns and its names to print out (format: n=name)', default='*')
    parser.add_argument('--delim', '-d', type=comma_list, 
                        help='A list of input columns delimiters. Format: delim[:min[-max]]. Where `min` and `max` are the numbers of times `delim` should repeat. As default min=1 and max is not set. Enter "\," for the delimiter "," and "\\\\"" for "\\"',
                        default=(' ', '\t'), 
                        metavar='delim[:min-max]')
    parser.add_argument('infiles', type=argparse.FileType('rb'), default=(stdin,), metavar='file', nargs='*')
    
    main(parser.parse_args())
