# ao3wrapped
Y'know how people went "what if there was an ao3 wrapped. That would be so cursed. I would hate it." Well.

Check out `todo.md` for what might get updated/what needs to be done.

# How To Use
Clone this repository (green button at the top, `git clone https://github.com/teresachenec/ao3wrapped.git`). Have Python 3.7+ and pip/3 installed. You're on your own for this.

Have the dependencies (listed below) installed. This can be done like this if you're on a Unix machine:
```
pip install requests
pip install beautifulsoup4
pip install pandas
```
If you're on a macOS then do `pip3` instead of `pip` like `pip3 install requests`.

Then open `ao3wrapped.py` and the first two lines will have `username` and `password` variables. Enter your ao3 username and password. Save.

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
