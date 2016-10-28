## Table To Json
Convert text tables to a json document.

## Usage
```$ ././convert_to_json.py (index=[name],...) (file,...) --delim=delim```

* *index*:  the table column index to print, begins from 0. Can be combined with '=' to 
            define a name for this index. If equal to '\*', all indexes will be accepted
            (you can combine '\*' with regular indexes).

* *file*:   one or more file names to read from. The default is stdin.

* *delim*:  The delimeter of the text table, default is tab (\t).

## Examples
Parse a CSV [file](https://github.com/Reflexe/convert_table_to_json/blob/master/Data/example.csv):
```
$ ./convert_to_json.py '0=Name,1=UserName,3=Phone' Data/names.csv --delim=','
[{"Phone": "1234", "UserName": "Jim1", "Name": "Jimmy"}, {"Phone": "0000", "UserName": "TheHacker^", "Name": "John"}, {"Phone": "1111", "UserName": "r00x", "Name": "Jack"}]
```

Have fun! :)
