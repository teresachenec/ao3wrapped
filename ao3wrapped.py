from credentials import uname, pword

username = uname
password = pword

# pip3 install requests
# pip3 install beautifulsoup4
# pip3 install pandas

# Import statements
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Variables declaration
year = "2020"

is_in_date = True
hist_page = 1
title_lower_count = 0
user_ship_type = {"M/M": 0, "F/F": 0, "F/M": 0, "Gen": 0, "Multi": 0, "Other": 0, "No category": 0}
user_rating = {"General Audiences": 0, "Teen And Up Audiences": 0, "Mature": 0, "Explicit": 0, "Not Rated": 0}
user_status = {"Complete Work": 0, "Work in Progress": 0, "Unknown": 0}
user_authors = {}
user_fandoms = {}
user_ships = {}
user_characters = {}
user_tags = {}
user_word_count = 0
dict_list = [user_ship_type, user_rating, user_status, user_authors, user_fandoms, user_ships, user_characters, user_tags]

df_works = pd.DataFrame(columns=["title", "authors", "last_updated", "fandoms", "ship_types", "rating", "work_status", "ships", "characters", "additional_tags", "word_count", "kudos", "hits", "user_last_visited", "user_visitations"])

# get authenticity_token token for Rails
def get_token(session):
	r = session.get("https://archiveofourown.org")
	soup = BeautifulSoup(r.content, "html.parser")

	return soup.find("meta", {"name": "csrf-token"})["content"]

# params:
# - soup: BeautifulSoup object of an ao3 history page
def parse_hist_page(soup):
	try:
		work_list = soup.find("ol", {"class": "reading work index group"})
		for w in work_list.find_all("li", {"class": "reading work blurb group"}):
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

			# Get when user last visited the fic
			last_visited = w.find("div", {"class": "user module group"}).find("h4").text[15:].split("\n")[0]
			if last_visited.find(year) == -1:
				global is_in_date
				is_in_date = False
			# print(last_visited)

			# Get number of times user visited the fic
			visitations = w.find("div", {"class": "user module group"}).find("h4").text[15:].split("\n")[4].split("Visited ")[1].split(" ")[0]
			if(visitations == "once"):
				visitations = 1
			else:
				visitations = int(visitations)
			# print(visitations)

			# Add this work to the works DataFrame
			if is_in_date:
				global df_works
				work = {"title": title, "authors": authors, "last_updated": updated, "fandoms": fandoms, "ship_types": ship_types, "rating": rating, "work_status": work_status, "ships": ships, "characters": characters, "additional_tags": additional_tags, "word_count": word_count, "kudos": kudos, "hits": hits, "user_last_visited": last_visited, "user_visitations": visitations}
				df_works = df_works.append(work, ignore_index=True)

	except (RuntimeError, TypeError, NameError, AttributeError):
		print("Error adding work.")
		pass

with requests.Session() as s:
	token = get_token(s)
	payload = {"utf8": "✓",
				"authenticity_token": token,
				"user[login]": username,
				"user[password]": password,
				"commit": "Log in"}

	# POST request to ao3 to login
	p = s.post("https://archiveofourown.org/users/login", data=payload)

	while is_in_date:
		r = s.get("https://archiveofourown.org/users/" + username + "/readings?page=" + str(hist_page))
		soup = BeautifulSoup(r.content, "html.parser")
		parse_hist_page(soup)
		hist_page += 1

df_works.to_csv("works.csv")

sorted_dict_list = []
for d in dict_list:
	sorted_dict = {}
	for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True):
		sorted_dict[k] = v
	sorted_dict_list.append(sorted_dict)

with open("user.csv", "w") as f:
	f.write("%s, %s\n" % ("Word count", user_word_count))
	for dictionary in sorted_dict_list:
		for key in dictionary.keys():
			f.write("%s, %s\n" % (key, dictionary[key]))

print("LMAO you've read", len(df_works.index), "fanfics this year, totaling", user_word_count, "words.")
if len(df_works.index) > 1500:
	print("Oh jeez. The US National Suicide hotline is 800-273-8255. You probably need it.")
elif len(df_works.index) > 1000:
	print("Are you proud of yourself? Because I can almost assure you, your parents aren't.")
elif len(df_works.index) == 666 or len(df_works.index) == 420 or len(df_works.index) == 69:
	print("Nice.")
elif len(df_works.index) > 500:
	print("Think of all that time you've wasted...")
elif len(df_works.index) < 250:
	print("C'mon, those are rookie numbers. You can do better next year.")
elif len(df_works.index) < 50:
	print("Really? Only", len(df_works.index), "? Why'd you even bother doing this?")

if title_lower_count >= 10:
	print(title_lower_count, "of those", len(df_works.index), "fics had all lower-case titles. Hipster.")

top_key = list(user_ship_type.keys())[0]
top_val = user_ship_type[top_key]
print("You read", top_val, top_key, "fics this year.")
if top_key == "F/M":
	print("Fucking hets.")
elif top_key == "M/M" or top_key == "F/F":
	print("Fucking gay.")
elif top_key == "Gen":
	print("That's actually really wholesome.")
print("You also read:")
user_ship_type_list = list(user_ship_type)[1:]
for key in user_ship_type_list:
	print(key + ": " + str(user_ship_type[key]))

print("\n")

top_key = list(user_rating.keys())[0]
top_val = user_rating[top_key]
print("You read", top_val, top_key, "fics this year.")
if top_key == "General Audiences":
	print("Keeping it wholesome, I see. I can respect that.")
elif top_key == "Teen And Up Audiences":
	print("TODO")
elif top_key == "Mature":
	print("TODO")
elif top_key == "Explicit":
	print("Well, they did say the internet was for porn.")
print("You also read:")
user_rating_list = list(user_rating)[1:]
for key in user_rating_list:
	print(key + ": " + str(user_rating[key]))

print("\n")

top_key = list(user_status.keys())[0]
top_val = user_status[top_key]
print("You read", top_val, top_key, "fics and", user_status[list(user_status.keys())[1]], list(user_status.keys())[1], "this year.")
if user_status["Work in Progress"] > user_status["Complete Work"] and user_status["Work in Progress"] > 50:
	print("Are you okay?")

print("\n")

top_key = list(user_authors.keys())[0]
top_val = user_authors[top_key]
print("Your most read author was", top_key, ", with", top_val, "fics this year. You should tell them you're such a big fan. They deserve to know. Seriously.")
print("You also read a lot of:")
index = len(user_authors)
if len(user_authors) >= 5:
	index = 5
user_authors_list = list(user_authors)
for key in user_authors_list[1:5]:
	print(key + ": " + str(user_authors[key]))

print("\n")

top_key = list(user_fandoms.keys())[0]
top_val = user_fandoms[top_key]
print("Your most read fandom was", top_key, ", with", top_val, "fics this year. Loser.")
print("You also read a lot of:")
index = len(user_fandoms)
if len(user_fandoms) >= 5:
	index = 5
user_fandoms_list = list(user_fandoms)
for key in user_fandoms_list[1:5]:
	print(key + ": " + str(user_fandoms[key]))

print("\n")

top_key = list(user_ships.keys())[0]
top_val = user_ships[top_key]
print("Holy shit, how are you not tired of reading about", top_key, "? You read", top_val, "fics of them this year. Get help.")
print("You also read a lot of:")
index = len(user_ships)
if len(user_ships) >= 5:
	index = 5
user_ships_list = list(user_ships)
for key in user_ships_list[1:5]:
	print(key + ": " + str(user_ships[key]))

print("\n")

top_key = list(user_characters.keys())[0]
top_val = user_characters[top_key]
print("What a fucking", top_key, "stan. You read", top_val, "fics of them this year. You know you're unbearable, right?")
print("You also read a lot of:")
index = len(user_characters)
if len(user_characters) >= 5:
	index = 5
user_characters_list = list(user_characters)
for key in user_characters_list[1:5]:
	print(key + ": " + str(user_characters[key]))

print("\n")

top_key = list(user_tags.keys())[0]
top_val = user_tags[top_key]
print("You're a fucking slut for", top_key, ", but you already knew that. You read", top_val, "fics this year. Can't say I'm judging.")
print("You also read a lot of:")
index = len(user_tags)
if len(user_tags) >= 5:
	index = 5
user_tags_list = list(user_tags)
for key in user_tags_list[1:5]:
	print(key + ": " + str(user_tags[key]))
