# !/usr/bin/env python
#  -*- coding: utf-8 -*-

from __future__ import division

from pprint import pprint
import networkx as nx
import random
from math import log

from itertools import chain

from midiutil.MidiFile3 import MIDIFile

#  Utility functions


def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w


def note_from_interval(start, interval):
    note = [start]
    for x in range(interval):
        note = HalfSteps.successors(note[0])
    return note[0]


def weight_list(list_from, most_probable=None, smoothness=1):
    l = len(list_from)
    y = list_from.index(most_probable) if most_probable else l/2
    z = smoothness
    weights = [x + ((1/l-abs(abs(y-x))) * z**(l-abs(abs(y-x))/z)) for x in range(1, l)]
    return map(lambda x: (int(x+(abs(min(weights))))), weights)


# Ordered list of notes
note_list = list(chain.from_iterable([[note, note+'# '] if note not in ('B', 'E') else note for note in map(chr, range(65, 72))]))

# Weighted list of durations
durations = [8, 4, 2, 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256]
durations = zip(durations, weight_list(durations, 1, 1.5))

# Weighted list of octaves
octaves = zip(range(0, 9), weight_list(range(0, 9), 4, 1.5))

# directed graph for the notes
HalfSteps = nx.DiGraph()
HalfSteps.add_nodes_from(note_list)
HalfSteps.add_path(note_list)
HalfSteps.add_edge('G# ', 'A')


class Scale(object):
    """docstring for Scale"""
    def __init__(self, steps):
        super(Scale, self).__init__()
        self.steps = steps

    def notes_from(self, start):
        notes = [start, ]
        for step in self.steps:
            notes.append(note_from_interval(notes[-1],step))
        return notes

with open('scales.txt', 'r') as f:
    scales = dict()
    for line in f:
        name, steps = line.split(' ')
        scales[name] = Scale(list(map(int, steps.strip('\n').split(','))))


class Note(object):
    f0 = 16.352
    a = 2**(1/12)

    def __init__(self, name, octave, duration):
        super(Note, self).__init__()
        self.name = name
        self.octave = octave
        self.freq = self.f0 * (self.a)**((12 * self.octave) + nx.shortest_path_length(HalfSteps, 'C', self.name))
        self.pitch = int(69 + 12 * log((self.freq/440), 2))
        self.duration = duration


class Riff(object):
    def __init__(self, start_note, scale):
        super(Riff, self).__init__()
        self.start_note = start_note
        avaiable_notes = scales[scale].notes_from(self.start_note)
        self.score = []
        self.score.append(Note(start_note, 4, weighted_choice(durations)))
        for x in range(random.randint(2, 6)):
            note = avaiable_notes[random.randint(0, len(avaiable_notes)-1)]
            duration = weighted_choice(durations)
            octave = weighted_choice(octaves)
            self.score.append(Note(note, octave, duration))


class Song(object):
    song_parts = [('verse', (2, 4)),
                ('chorus', (2, 4)),
                ('prechorus', (1, 3)),
                ('solo', (1, 2)),
                ('intro', (1, 1)),
                ('outro', (1, 1))]

    """docstring for Song"""
    def __init__(self, tempo, styles, complexity):
        super(Song, self).__init__()
        self.tempo = tempo + random.randint(-3, 3)
        self.scales = styles
        start_scale = scales[styles[random.randint(0, len(self.scales)-1)]]
        avaiable_notes = start_scale.notes_from(note_list[random.randint(0, 11)])
        self.complexity = complexity if complexity <= len(self.song_parts) else len(self.song_parts)
        self.base_notes = [avaiable_notes[random.randint(0, len(avaiable_notes)-1)] for x in range(0, self.complexity)]
        self.riffs = {self.song_parts[x][0]: [Riff(self.base_notes[x], self.scales[random.randint(0, len(self.scales)-1)]), random.randint(*self.song_parts[x][1]), self.base_notes[x]] for x in range(0, self.complexity)}
        structure = list(chain(*[[part] * riff[1] for part, riff in self.riffs.items() if part not in ('intro', 'outro')]))
        self.structure = ['verse']
        structure.remove('verse')
        for x in range(len(structure)):
            avaiables = [p for p in structure if p != self.structure[-1]]
            if len(set(avaiables)) > 1:
                next_part = random.choice(avaiables)
                structure.remove(next_part)
                self.structure.append(next_part)
        self.structure = list(chain(*[[riff] * (random.randint(1, 2)*2) for riff in self.structure]))
        if 'intro' in self.riffs.keys():
            self.structure = ['intro'] * (random.randint(1, 2)*2) + self.structure
        if 'outro' in self.riffs.keys():
            self.structure = self.structure + ['outro'] * (random.randint(1, 2)*2)
        pprint(self.__dict__)

    def make(self):
        with open("output.mid", 'wb') as f:
            MyMIDI = MIDIFile(1)
            track = 0
            time = 0
            channel = 0
            volume = 100
            MyMIDI.addTrackName(track, self.tempo, "Sample Track")
            MyMIDI.addTempo(track, time, 120)
            for part in self.structure:
                for note in self.riffs[part][0].score:
                    MyMIDI.addNote(track, channel, note.pitch, time, note.duration, volume)
                    time += note.duration
            MyMIDI.writeFile(f)

#test = Song(80, ['blues', 'enigmatica', 'orientale'], 6)
#test.make()
