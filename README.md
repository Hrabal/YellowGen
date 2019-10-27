# YellowGen
Random Music Generator

Put your favourite musical scales in scales.txt.
Example Diatonic Major scale:
diatmaj 2,2,1,2,2,2,1
name [space] [comma-separater halftones between each scale note]

Then import Song class from yellow.py, init with params and call make method. It will make a .mid file called "output.mid"
Example:
>>> from yellow import Song

>>> my_new_song = Song(80, ['blues', 'orientale'], 3)

>>> my_new_song.make()

Params of Song are:
-Tempo, song will add/subtract some random amount because random is cool.
-Scales, names of the scale that will be used in the song.
-Complexity, how much the song will be complex in terms of structure (eg. verse-chorus-verse is complexity 2)

Play around.
