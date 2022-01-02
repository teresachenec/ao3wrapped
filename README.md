# ao3wrapped
Y'know how people went "what if there was an ao3 wrapped. That would be so cursed. I would hate it." Well.

Check out `todo.md` for what might get updated/what needs to be done. Pull requests are absolutely welcome, as you can tell by looking at this code, I have no idea what I'm doing.

If you run into `AttributeError: 'NoneType' object has no attribute 'find_all'` when running the program, this is likely because ao3 has rate limited you. Fix incoming (or you're welcome to create a PR).
`

# How To Use
[Download](https://github.com/teresachenec/ao3wrapped/archive/refs/heads/master.zip) or clone this repository (green button at the top, `git clone https://github.com/teresachenec/ao3wrapped.git`) . Have [Python 3.7+](https://www.python.org/downloads/) and pip/3 installed.

Have the dependencies (listed below) installed. This can be done like this if you're on a Unix machine:
```
pip install requests
pip install beautifulsoup4
pip install pandas
```
If you're on a macOS then do `pip3` instead of `pip` like `pip3 install requests`.

Then open `ao3wrapped.py` and the first two lines will have `username` and `password` variables. Enter your ao3 username and password. There are options to scrape your history instead of your bookmarks, as well as to change the year. Save your changes.

Run the program like this:
```
python ao3wrapped.py
```
If you're on macOS then do `python3` instead of `python` like `python3 ao3wrapped.py`.

This will also generate two files:
* `works.csv` - a spreadsheet of the works you read this year
* `user.csv` - a spreadsheet of your stats from this year

# Dependencies
* Requests
* Beautiful Soup
* pandas
