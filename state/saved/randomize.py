#!/usr/bin/env python3
#
# "Twitch Hacks Online"
# 2020 - Frank Godo

import os
import csv
import random
import json

NEW_FILENAME = 'new_emotes.csv'

old = open('emotes.csv', 'r')
new = open(NEW_FILENAME, 'w')
emote_dict = json.load(open('emotes.json'))
emotes = list(emote_dict)

# Get the number of keys we need to select emotes for
num_keys = sum(1 for line in old)
old.seek(0)

# Reduce the number of emotes by randomly deleting keys
while len(emotes) > num_keys:
    sel = random.choice(emotes)
    emotes.remove(sel)

# Shuffle the list of emotes
random.shuffle(emotes)

# Write the new emotes to file
reader = csv.reader(old)
writer = csv.writer(new)

for index, row in enumerate(reader):
    emote = emotes[index]
    row[0] = emote_dict[emote]
    row[1] = emote 
    row[8] = 0  # Ensure keys are not unlocked by default
    writer.writerow(row)

print("New file written to {}".format(NEW_FILENAME))
