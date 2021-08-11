import json
import random
from argparse import ArgumentParser
from decimal import Decimal
from collections import defaultdict

from pychord import Chord
from midiutil import MIDIFile


EOC = "EndOfComposition"

note2pitch = {
    "C": 60,
    "C#": 61,
    "Db": 61,
    "D": 62,
    "D#": 63,
    "Eb": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "Gb": 66,
    "G": 67,
    "G#": 68,
    "Ab": 68,
    "A": 69,
    "A#": 70,
    "Bb": 70,
    "B": 71,
}


def create_midi(chord_sequence, midi_filename):
    print(f"Generating sequence: {chord_sequence}")
    bpm = random.randint(40, 80)
    file = MIDIFile()
    file.addTempo(0, 0, bpm)

    time = 0
    for chord in chord_sequence:
        channel = 0
        for note in Chord(chord).components():
            pitch = note2pitch[note]
            file.addNote(0, channel, pitch, time, duration=1, volume=100)
            channel += 1
        time += 1

    with open(midi_filename, "wb") as out:
        file.writeFile(out)


def gen_sequence(chains):
    chord = random.choice(list(chains.keys()))
    sequence = [chord]
    for _ in range(8):
        filtered = None
        while not filtered:
            number = Decimal(random.random())
            filtered = list(filter(lambda x: x >= number, chains[chord].keys()))
        choice = min(filtered)

        chord = chains[chord][choice]
        if chord == EOC:
            break
        sequence.append(chord)
    return sequence


def get_chains(compositions):
    # How many times this chord connection appears
    connections = defaultdict(lambda: defaultdict(int))
    # How many times this chord appears
    totals = defaultdict(int)
    for chords in compositions:
        if not chords:
            continue
        # Do not use itertools chain, because compositions are not connected.
        for chord, next_chord in zip(chords, chords[1:]):
            connections[chord][next_chord] += 1
            totals[chord] += 1

        # Add last chord + end of composition connection, because it wasn't processed in the loop.
        connections[chords[-1]][EOC] += 1
        totals[chords[-1]] += 1

    chains = defaultdict(dict)
    for chord, next_chords in connections.items():
        for next_chord, next_chord_n in next_chords.items():
            probability = Decimal(next_chord_n) / Decimal(totals[chord])
            chains[chord][probability] = next_chord

    return chains


def filter_compositions(compositions):
    is_minor = random.choice((True, False))
    result = []
    for entry in compositions.values():
        if entry["is_minor"] != is_minor:
            continue

        result.append(entry["chords"])
    return result


def main():
    parser = ArgumentParser()
    parser.add_argument("--midi", required=True, type=str, help="where MIDI output should be generated")
    parser.add_argument("--dataset", required=False, type=str, default="compositions.json")
    args = parser.parse_args()

    with open(args.dataset) as file:
        contents = json.load(file)

    dataset = filter_compositions(contents)
    chains = get_chains(dataset)
    sequence = gen_sequence(chains)
    create_midi(sequence, args.midi)

if __name__ == "__main__":
    main()
