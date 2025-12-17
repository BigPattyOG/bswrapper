# Brawl Stars Wrapper (BSWrapper) - v0.1.1

## What is BSWrapper?

BSWrapper is a user friendly API wraper for the [Brawl Stars API](https://developer.brawlstars.com). It aims to make pulling all information found in the API as easy as possibly without needing to use a 3rd party API.

## Requirements

- Python 3.12 or higher

## How do I install it?

To install BSWrapper, simply run:

```bash
pip install bswrapper
```
or in your requirements.txt, enter it as:
```txt
bswrapper>=0.1.0
```

## How to use BSWrapper

### Example 1: Player Data:

```py
from bswrapper import BSWrapper

bs = BSWrapper("API_TOKEN")

player = bs.getplayer("#TAG")

print(player.name)
print(player.trophies) # current trophies
print(player.club.name) # if they are in a club, if not it just shows 'None'
print(player.club.tag) # if they are in a club, if not it just shows 'None'
print(player.highest) # highest trophies
print(player.explevel)
print(player.solo) # amount of solo victories

# NOTE: this is all of properties so far in the wrapper
```

### Example 2: Club Data:

```py
from bswrapper import BSWrapper

bs = BSWrapper("API_TOKEN")

club = bs.getclub("#TAG")

print(club.name)
print(club.trophies) # total trophies
print(club.required) # required trophies
print(club.type) # this will print either: open, inviteOnly, closed, unknown
print(club.description) # the club description/bio seen in the game

# NOTE: this is all of properties so far in the wrapper
```

