from credentials import uname, pword

# Replace your ao3 username and password and put quotation marks around it
# Ex: username = "myao3username"
username = uname
password = pword

# Program defaults on getting its information from the history page, but you can choose to get it from the bookmarks by setting this variable to True
bookmarks = True

# If you want to run this for another year change this number
year = "2021"

# Import statements
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time

# Variables declaration
is_in_date = True
hist_page = 1
title_lower_count = 0
user_ship_type = {"M/M": 0, "F/F": 0, "F/M": 0, "Gen": 0, "Multi": 0, "Other": 0, "No category": 0}
user_rating = {"General Audiences": 0, "Teen And Up Audiences": 0, "Mature": 0, "Explicit": 0, "Not Rated": 0}
user_status = {"Complete Work": 0, "Work in Progress": 0, "Unknown": 0, "Series in Progress": 0}
user_authors = {}
user_fandoms = {}
user_ships = {}
user_characters = {}
user_tags = {}
user_word_count = 0
dict_list = [user_ship_type, user_rating, user_status, user_authors, user_fandoms, user_ships, user_characters, user_tags]
scrape_type = "readings"
if bookmarks:
	scrape_type = "bookmarks"

df_works = pd.DataFrame(columns=["title", "authors", "last_updated", "fandoms", "ship_types", "rating", "work_status", "ships", "characters", "additional_tags", "word_count", "kudos", "hits", "user_last_visited", "user_visitations"])
df_works = df_works.astype({"word_count": "int32", "kudos": "int32", "hits": "int32", "user_visitations": "int32"})
if bookmarks:
	df_works.drop(labels="user_visitations", axis=1, inplace=True)

def get_work_authors(work_index):
	global df_works
	work_authors = ""
	if len(df_works["authors"].iloc[work_index]) == 1:
		work_authors = df_works["authors"].iloc[work_index][0]
	elif len(df_works["authors"].iloc[work_index]) == 2:
		for author in df_works["authors"].iloc[work_index]:
			work_authors += author + " and "
		work_authors = work_authors[:-5]
	elif len(df_works["authors"].iloc[work_index]) >= 3:
		for author in df_works["authors"].iloc[work_index]:
			work_authors += author + ", "
		work_authors = work_authors[:-2]
	else:
		work_authors = "Anonymous"
	return work_authors

# Get authenticity_token token for Rails
# params:
# - session: requests Session object
def get_token(session):
	r = session.get("https://archiveofourown.org")
	soup = BeautifulSoup(r.content, "html.parser")

	return soup.find("meta", {"name": "csrf-token"})["content"]

# Parses works on one history page from an ao3 account and adds to works DataFrame if it's from the year specified
# params:
# - soup: BeautifulSoup object of an ao3 history page
def parse_hist_page(soup):
	work_list = ""
	if bookmarks:
		work_list = soup.find("ol", {"class": "bookmark index group"}).find_all("li", {"class": "bookmark blurb group"})
	else:
		work_list = soup.find("ol", {"class": "reading work index group"}).find_all("li", {"class": "reading work blurb group"})
	for w in work_list:
		try:
			if bookmarks:
				# Check if work has been deleted
				if w.find("p", {"class": "message"}) != None:
					if w.find("p").text == "This has been deleted, sorry!":
						continue
				# Check if bookmark is a series
				elif w.find("div", {"class": "own user module group"}).find("ul", {"class": "actions"}).find("li", {"class": "share"}) == None:
					continue

			# Get when user last visited the fic
			last_visited = ""
			if bookmarks:
				last_visited = w.find("div", {"class": "own user module group"}).find("p").text
			else:
				last_visited = w.find("div", {"class": "user module group"}).find("h4").text[15:].split("\n")[0]
			if last_visited.find(year) == -1:
				global is_in_date
				is_in_date = False
			else:
				is_in_date = True
			# print(last_visited)

			# If user visited the fic in specified year
			if is_in_date:
				# Get title
				title = w.find("div", {"class": "header module"}).find("h4", {"class": "heading"}).find("a").text
				if title == title.lower():
					global title_lower_count
					title_lower_count += 1
				# print(title)

				# Get authors
				authors = []
				for author in w.find("div", {"class": "header module"}).find("h4", {"class": "heading"}).find_all(rel="author"):
					if author.text != "orphan_account":
						authors.append(author.text)
						if author.text in user_authors:
							user_authors[author.text] += 1
						else:
							user_authors[author.text] = 1
				# print(authors)

				# Get date last updated
				updated = w.find("div", {"class": "header module"}).find("p").text
				# print(updated)

				# Get fandoms
				fandoms = []
				for fandom in w.find("div", {"class": "header module"}).find("h5", "fandoms heading").find_all("a"):
					fandoms.append(fandom.text)
					if fandom.text in user_fandoms:
						user_fandoms[fandom.text] += 1
					else:
						user_fandoms[fandom.text] = 1
				# print(fandoms)

				# Get relationship type, rating, and work status
				req_tag_list = []
				for req_tag in w.find("div", {"class": "header module"}).find("ul").find_all("li"):
					req_tag_list.append(req_tag.find("a").find("span", {"class": "text"}).text)
				ship_types = []
				for type in req_tag_list[2].split(", "):
					ship_types.append(type)
					user_ship_type[type] += 1
				rating = req_tag_list[0]
				user_rating[rating] += 1
				work_status = req_tag_list[3]
				user_status[work_status] += 1
				# print(ship_types)
				# print(rating)
				# print(work_status)

				# Get relationships
				ships = []
				for ship in w.find("ul", {"class": "tags commas"}).find_all("li", {"class": "relationships"}):
					ships.append(ship.text)
					if ship.text in user_ships:
						user_ships[ship.text] += 1
					else:
						user_ships[ship.text] = 1
				# print(ships)

				# Get characters
				characters = []
				for character in w.find("ul", {"class": "tags commas"}).find_all("li", {"class": "characters"}):
					characters.append(character.text)
					if character.text in user_characters:
						user_characters[character.text] += 1
					else:
						user_characters[character.text] = 1
				# print(characters)

				# Get freeform tags
				additional_tags = []
				for tag in w.find("ul", {"class": "tags commas"}).find_all("li", {"class": "freeforms"}):
					additional_tags.append(tag.text)
					if tag.text in user_tags:
						user_tags[tag.text] += 1
					else:
						user_tags[tag.text] = 1
				# print(additional_tags)

				# Get word count
				word_count = int(w.find("dl", {"class": "stats"}).find("dd", {"class": "words"}).text.replace(",", ""))
				global user_word_count
				user_word_count += word_count
				# print(word_count)

				# Get kudos
				kudos = int(w.find("dl", {"class": "stats"}).find("dd", {"class": "kudos"}).find("a").text.replace(",", ""))
				# print(kudos)

				# Get hits
				hits = int(w.find("dl", {"class": "stats"}).find("dd", {"class": "hits"}).text.replace(",", ""))
				# print(hits)

				# Get number of times user visited the fic
				if not bookmarks:
					visitations = w.find("div", {"class": "user module group"}).find("h4").text[15:].split("\n")[4].split("Visited ")[1].split(" ")[0]
					if(visitations == "once"):
						visitations = 1
					else:
						visitations = int(visitations)
					# print(visitations)

				# Add this work to the works DataFrame
				global df_works
				work = {"title": title, "authors": authors, "last_updated": updated, "fandoms": fandoms, "ship_types": ship_types, "rating": rating, "work_status": work_status, "ships": ships, "characters": characters, "additional_tags": additional_tags, "word_count": word_count, "kudos": kudos, "hits": hits, "user_last_visited": last_visited}
				if not bookmarks:
					work = {"title": title, "authors": authors, "last_updated": updated, "fandoms": fandoms, "ship_types": ship_types, "rating": rating, "work_status": work_status, "ships": ships, "characters": characters, "additional_tags": additional_tags, "word_count": word_count, "kudos": kudos, "hits": hits, "user_last_visited": last_visited, "user_visitations": visitations}
				df_works = df_works.append(work, ignore_index=True)

		except (RuntimeError):
			print("Error adding work.")
			# print(w)
			pass

with requests.Session() as s:
	token = get_token(s)

	# Creates payload to login to ao3
	payload = {"utf8": "✓",
				"authenticity_token": token,
				"user[login]": username,
				"user[password]": password,
				"commit": "Log in"}

	# POST request to ao3 to login
	p = s.post("https://archiveofourown.org/users/login", data=payload)

	# Get every fic in a user's history from the year specified and loads them into a DataFrame and updates the user dictionaries
	while is_in_date:
		r = s.get("https://archiveofourown.org/users/" + username + "/" + scrape_type + "?page=" + str(hist_page))
		soup = BeautifulSoup(r.content, "html.parser")
		if soup.find("div", {"class": "flash error"}) != None:
			if soup.find("div", {"class": "flash error"}).text == "Sorry, you don't have permission to access the page you were trying to reach. Please log in.":
				print("Error logging in.")
				exit(1)
		parse_hist_page(soup)
		hist_page += 1

# Stores information collected on works into a csv file
df_works.to_csv("works.csv")

# Sorts the information collected about the user by key (most to least common)
i = 0
for d in dict_list:
	dict_list[i] = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
	i += 1

# Reassigns dictionaries with sorted ones
user_ship_type = dict_list[0]
user_rating = dict_list[1]
user_status = dict_list[2]
user_authors = dict_list[3]
user_fandoms = dict_list[4]
user_ships = dict_list[5]
user_characters = dict_list[6]
user_tags = dict_list[7]

# Stores information collected on the user's readings into a csv file
with open("user.csv", "w") as f:
	f.write("%s, %s\n" % ("Word count", user_word_count))
	for dictionary in dict_list:
		for key in dictionary.keys():
			f.write("%s, %s\n" % (key, dictionary[key]))

# Prints user statistics
print("You've read %d fanfics this year, totaling %d words, or %.2f words/day. There's about 70000 words in a novel. You could've read %.2f novels this year, but you read fanfic instead." % (len(df_works.index), user_word_count, user_word_count/365, user_word_count/70000))

print("%d of those %d fics had all lower-case titles. Hipster." % (title_lower_count, len(df_works.index)))

if not bookmarks:
	work_index = df_works["user_visitations"].idxmax(axis=1)
	work_authors = get_work_authors(work_index)
	print("The fic you've visited the most was %s by %s, with %d visitations." % (df_works["title"].iloc[work_index], work_authors, df_works["user_visitations"].iloc[work_index]))

top_key = list(user_ship_type.keys())[0]
top_val = user_ship_type[top_key]
print("You read %d %s fics this year." % (top_val, top_key))
print("You also read")
user_ship_type_list = list(user_ship_type)[1:]
for key in user_ship_type_list:
	print("%d %s fics" % (user_ship_type[key], key))

print("\n")

top_key = list(user_rating.keys())[0]
top_val = user_rating[top_key]
print("You read %d %s fics this year." % (top_val, top_key))
print("You also read")
user_rating_list = list(user_rating)[1:]
for key in user_rating_list:
	print("%d %s fics" % (user_rating[key], key))

print("\n")

top_key = list(user_status.keys())[0]
top_val = user_status[top_key]
print("You read %d %s and %d %s fics this year." % (top_val, top_key, user_status[list(user_status.keys())[1]], list(user_status.keys())[1]))

print("\n")

top_key = list(user_authors.keys())[0]
top_val = user_authors[top_key]
print("You read %d different authors this year." % len(user_authors))
print("Your most read author this year was %s, with %d fics. You should tell them you're such a big fan, like right now. They deserve to know." % (top_key, top_val))
print("Seriously. I'll wait. Leave (another) comment on a fic of theirs.")
# time.sleep(30)
print("You also read:")
index = len(user_authors)
if len(user_authors) >= 5:
	index = 5
user_authors_list = list(user_authors)
for key in user_authors_list[1:5]:
	print("%d fics by %s" % (user_authors[key], key))

print("\n")

top_key = list(user_fandoms.keys())[0]
top_val = user_fandoms[top_key]
print("You read fics for %d different fandoms this year." % len(user_fandoms))
print("Your most read fandom was %s, with %d fics this year." % (top_key, top_val))
print("You also read:")
index = len(user_fandoms)
if len(user_fandoms) >= 5:
	index = 5
user_fandoms_list = list(user_fandoms)
for key in user_fandoms_list[1:5]:
	print("%d %s fics" % (user_fandoms[key], key))

print("\n")

top_key = list(user_ships.keys())[0]
top_val = user_ships[top_key]
print("You read fics with %d different ships this year." % len(user_ships))
print("Are you not tired of reading about %s? You read %d fics of them this year." % (top_key, top_val))
print("You also read:")
index = len(user_ships)
if len(user_ships) >= 5:
	index = 5
user_ships_list = list(user_ships)
for key in user_ships_list[1:5]:
	print("%d %s fics" % (user_ships[key], key))

print("\n")

top_key = list(user_characters.keys())[0]
top_val = user_characters[top_key]
print("You read about %d different characters this year." % len(user_characters))
print("What a %s stan. You read %d fics of them this year." % (top_key, top_val))
print("You also read:")
index = len(user_characters)
if len(user_characters) >= 5:
	index = 5
user_characters_list = list(user_characters)
for key in user_characters_list[1:5]:
	print("%d %s fics" % (user_characters[key], key))

print("\n")

top_key = list(user_tags.keys())[0]
top_val = user_tags[top_key]
print("You read fics with %d different tags this year, averaging %.2f tags/work." % (len(user_tags), len(user_tags)/len(df_works)))
print("You absolutely love %s, but you already knew that. You read %d fics with that tag this year." % (top_key, top_val))
print("You also read:")
index = len(user_tags)
if len(user_tags) >= 5:
	index = 5
user_tags_list = list(user_tags)
for key in user_tags_list[1:5]:
	print("%d %s fics" % (user_tags[key], key))

print("\n")

# Most/least/avg hits/kudos/word count
work_index = df_works["word_count"].idxmax(axis=0)
work_authors = get_work_authors(work_index)
print("Highest word count: %s by %s with %d words" % (df_works["title"].iloc[work_index], work_authors, df_works["word_count"].iloc[work_index]))
work_index = df_works["word_count"].idxmin(axis=0)
work_authors = get_work_authors(work_index)
print("Lowest word count: %s by %s with %d words" % (df_works["title"].iloc[work_index], work_authors, df_works["word_count"].iloc[work_index]))
print("Average word count: %d" % df_works.describe().at["mean", "word_count"])

print("\n")

work_index = df_works["hits"].idxmax(axis=0)
work_authors = get_work_authors(work_index)
print("Most hits: %s by %s with %d hits" % (df_works["title"].iloc[work_index], work_authors, df_works["hits"].iloc[work_index]))
work_index = df_works["hits"].idxmin(axis=0)
work_authors = get_work_authors(work_index)
print("Least hits: %s by %s with %d hits" % (df_works["title"].iloc[work_index], work_authors, df_works["hits"].iloc[work_index]))
print("Average hits: %d" % df_works.describe().at["mean", "hits"])

print("\n")

work_index = df_works["kudos"].idxmax(axis=0)
work_authors = get_work_authors(work_index)
print("Most kudos: %s by %s with %d kudos" % (df_works["title"].iloc[work_index], work_authors, df_works["kudos"].iloc[work_index]))
work_index = df_works["kudos"].idxmin(axis=0)
work_authors = get_work_authors(work_index)
print("Least kudos: %s by %s with %d kudos" % (df_works["title"].iloc[work_index], work_authors, df_works["kudos"].iloc[work_index]))
print("Average kudos: %d" % df_works.describe().at["mean", "kudos"])
