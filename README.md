# wire-backup-parser
`wire-backup-parser` is a command-line tool for creating reports and statistics of 
[Wire](https://github.com/wireapp/wire) conversations. It allows you to freely browse the entirety of your 
messaging history and to backup all your media, eternalizing your work-related discussions and/or happy memories.

## Features

* Easy-to-use, straightforward command line interface
* Elegant, interactive and printable HTML reports
* Many insightful statistics to cultivate your community

## Preparations
Install required dependencies
```shell script
# pip install -r requirements.txt
```
Download Wire backup file by selecting `Back up conversation` on `Preferences`->`Account` page.

## Usage
Generate report of conversation named `Some group` using backup file `wire.backup` to directory `output`:
```shell script
# python3 parser.py -f wire.backup -g 'Some Group' -o output
```
When requested, enter your Wire credentials

**Note**: Full backup generation may take even a few hour, depending on the size of selected conversation
