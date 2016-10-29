#!/usr/bin/env python3

import json

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

    json_objects_list = []    
    
    for fd in args.infiles:
        for line in fd:
            # Convert bytes object to string.
            if isinstance(line, bytes): 
                line = line.decode('utf-8')
            
            # Strip the \n in the end of the line.
            line = line.rstrip('\n')            

            # Split the line by the delim.
            splitted_line = line.split(args.delim)
            
            json_objects_list.append (columns_line_to_json (column_dict, splitted_line, should_filter_colunms))
            
    print(json.dumps (json_objects_list))
            

if __name__ == '__main__':
    import argparse    
    from sys import stdin
    
    parser = argparse.ArgumentParser()
    parser.add_argument('columns_and_names', help='The columns and its names to print out (format: n=name)', default='*')
    parser.add_argument('--delim', '-d', help='The input columns delimeter', default='\t')
    parser.add_argument('infiles', type=argparse.FileType('rb'), default=(stdin,), metavar='file', nargs='*')
    
    main(parser.parse_args())
