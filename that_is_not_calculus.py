import string, random

parts = {"<NP>":["it", "that", "that <NP> <VS>", "that \"<S>\" <VS>", "that that <NP> <V>", "<NP> that <VS>", "not <NP>"],
        "<VS>":["<V>", "<V> <NP>"], # "Verb subordinate," which is probably not a thing
        "<VP>":["<NP> <V> <NP>", "<NP> <V>"],
        "<S>":["<VP>", "<NP> <VS>", "<V> <NP> <NP>?"],
        "<V>":["is", "is not"],
        }

def gen_thatthatis():
    decay = .1
    formal_string = "<S>"
    while True:
        segment_split = formal_string.split('<')
        first_segment = segment_split.pop(0)
        segments = ['<' + sub for sub in segment_split]
        if not segments:
            break
        while True:
            segment = random.choice(segments)
            place = segments.index(segment)
            for part in parts:
                if part in segment:
                    proposed_replacement = random.choice(parts[part])
                    avg_splits = proposed_replacement.count('<')
                    chance =  1 if len(segments) == 1 or not avg_splits else decay/avg_splits
                    if random.random() > chance:
                        continue
                    segments[place] = segment.replace(part, proposed_replacement)
                    break
            else:
                continue
            break
        formal_string = first_segment + ''.join(segments)
    formal_string = formal_string.capitalize()

    if formal_string [-1] != '?':
        formal_string += '.'
    
    return formal_string

if __name__ == '__main__':
    print(gen_thatthatis())
            
