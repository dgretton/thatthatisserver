TAG_CHAR_GROUPS = (
    ('0', '0O'),
    ('1', '1ILJ7'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('8', '8A'),
    ('9', '9'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
    ('G', 'G'),
    ('H', 'H'),
    ('K', 'K'),
    ('M', 'M'),
    ('N', 'N'),
    ('P', 'P'),
    ('Q', 'Q'),
    ('R', 'R'),
    ('S', 'S'),
    ('T', 'T'),
    ('U', 'UV'),
    ('W', 'W'),
    ('X', 'X'),
    ('Y', 'Y'),
    ('Z', 'Z'))

TAG_CHAR_MAP = {}
for group in TAG_CHAR_GROUPS:
    char_out, chars_in = group
    for c_in in chars_in:
        TAG_CHAR_MAP[c_in.upper()] =  TAG_CHAR_MAP[c_in.lower()] = char_out
VALID_TAG_CHARS = ''.join(next(zip(*TAG_CHAR_GROUPS)))
TAG_LEN = 15

