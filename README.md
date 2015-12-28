
# traktor-tools

## pl2dir.py

Generates a directory structure based on your Traktor playlists.

This would be useful if you have a massive collection of tracks and you want to extract only what's in your playlists, either for importing your collection
to another machine with less disk space, or to place them on a USB key to be used in other places.

### Requirements

* A Unixlike operating system (Linux, Mac OSX)
** As of right now, [Cygwin](https://cygwin.com/) probably doesn't work due to pl2dir's dependence on hard links
* [Python](https://www.python.org/)
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) (pip install beautifulsoup4)

### Usage

```bash
./pl2dir.py COLLECTION PATH1 [PATH2 ...]

COLLECTION is a Traktor collection_*.nml file
PATH1, PATH2, etc. are lists of directories to recurse
when searching for audio files
```

As of right now pl2dir generates a script that can be used for generating a new directory structure.  This will be made simpler in a later version.

An example of how to use this:

```bash
./pl2dir.py collection_2015y12m21d_19h27m26s.nml /home/jack/mp3 | tee /tmp/playlists.sh
mkdir playlists
bash /tmp/playlists.sh
```

### TODO

This is a very early version, and I want to make a lot of changes to it:

* Rather than simply emitting a script, actually perform the actions
* Optionally copy rather than hard link
* Give the ability to import the entire collection, not just what's in the playlists
* Also allow the user to select specific playlists
* A setup/install script

But for right now, it does the task

