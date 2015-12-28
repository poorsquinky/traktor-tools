#!/usr/bin/python

# pl2dir - Generates a directory structure based on your Traktor playlists.

# Copyright (C) 2015 Erik Stambaugh

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program (see the file LICENSE); if not, see
# http://www.gnu.org/licenses/, or write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301  USA

from bs4 import BeautifulSoup
import os,re,sys


def help():
    print "Usage: %s COLLECTION PATH1 [PATH2 ...]\n" % sys.argv[0]
    print "       COLLECTION is a Traktor collection_*.nml file"
    print "       PATH1, PATH2, etc. are lists of directories to recurse"
    print "       when searching for audio files"

try:
    collection_filename = sys.argv[1]
    collection_fh = open(collection_filename)
except (IndexError, IOError), e:
    print "ERROR: invalid collection (%s)\n" % e
    help()
    sys.exit(1)

source_paths = sys.argv[2:]
if len(source_paths) < 1:
    print "ERROR: No source paths specified\n"
    help()
    sys.exit(1)

soup = BeautifulSoup(collection_fh, "xml")

print '# Getting a full list of source files...'
allfiles=[]
pathdict={}
for srcpath in source_paths:
    for path,dirs,files in os.walk(srcpath):
        for f in files:
            fullpath="%s/%s" % (path,f)
            allfiles.append(fullpath)
            d = pathdict.get(f,[])
            d.append(fullpath)
            pathdict[f] = d

### collection

class Track:

    def __str__(self):
        if self.artist:
            return "%s - %s" % (self.artist.encode('utf8'),self.title.encode('utf8'))
        return "%s" % (self.title.encode('utf8'))
    def __unicode__(self):
        return self.__str__()

    def __init__(self,soup):
        self.soup = soup

        self.artist = soup.attrs.get('ARTIST','')
        self.title  = soup.attrs.get('TITLE','')

        loc = soup.find('LOCATION')
        self.drive    = loc.attrs.get('VOLUME','')
        self.dir      = loc.attrs.get('DIR','')
        self.filename = loc.attrs.get('FILE','')

        self.pk = "%s%s%s" % (self.drive,self.dir,self.filename)

        self.located = None

    def find(self,pathdict):
        if self.located is None:
            if pathdict.has_key(self.filename):
                self.located = pathdict[self.filename][0]
        else:
            print "# NOT FOUND: %s" % self.filename

### playlists

class Playlist:

    def __str__(self):
        return self.name.encode('utf8')
    def __unicode__(self):
        return self.__str__()

    def __init__(self,soup,collection={}):

        self.soup = soup
        self.name = soup.attrs['NAME']
        self.tracklist = []
        self.tracks = []

        for t in self.soup.find_all('PRIMARYKEY', attrs={'TYPE': 'TRACK'}):
            self.tracklist.append(t["KEY"].encode('utf8'))
            if collection.has_key(t["KEY"]):
                track = collection[t['KEY']]
                self.tracks.append(track)
            else:
                print "# ***NOT FOUND IN COLLECTION: %s" % t["KEY"]

    def find_files(self, pathdict):
        for t in self.tracks:
            t.find(pathdict=pathdict)

collection={}
c = soup.find('COLLECTION')
for e in c.find_all('ENTRY'):
    track = Track(e)
    collection[track.pk] = track

playlists = []

pl = soup.find_all('NODE', attrs={"TYPE": "PLAYLIST"})
for l in pl:
    playlist = Playlist(l, collection=collection)
    playlists.append(playlist)



print "# Searching playlists..."
for l in playlists:
    if len(l.tracks) > 0:
        l.find_files(pathdict)
        found = reduce(lambda x,y: x+y, map(lambda z: 0 if z.located is None else 1, l.tracks))
        print "# %s - %s found %s not found" % (l, found, len(l.tracks) - found)

for l in playlists:
    if len(l.tracks) > 0:
        found = reduce(lambda x,y: x+y, map(lambda z: 0 if z.located is None else 1, l.tracks))
        if found > 0:
            dirname = re.sub(r'[^0-9a-zA-Z-_]','-',str(l))
            print "mkdir %s" % dirname
            for track in l.tracks:
                if track.located is not None:
                    extension = re.sub('.*\.','',track.located)
                    target = re.sub('[^0-9a-zA-Z-_]','_',str(track))
                    target = re.sub('_+$','',target)
                    target = "%s.%s" % (target,extension)
                    print 'cp -lvf "%s" "%s/%s"' % (re.sub(r'(["$])',r'\\\1',track.located), dirname, target)
        else:
            print "# NO TRACKS FOUND: %s" % l

