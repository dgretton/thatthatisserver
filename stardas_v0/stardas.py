import string
import random
import json
import os
import sys
import string
import docx
from const import TAG_LEN, VALID_TAG_CHARS, TAG_CHAR_MAP

rn = random.SystemRandom()
def dastag():
    try:
        return ''.join((rn.choice(VALID_TAG_CHARS) for i in range(TAG_LEN)))
    except Exception:
        raise NotImplementedError('Your system may not support truly random number '
                'generation; you will have to generate *DAS tags some other way.')

class PrereqNode:
    def __init__(self, parent=None):
        self.parent = parent
        self.left = None
        self.right = None

    def children(self):
        return self.left, self.right

class PrereqAnd(PrereqNode):
    pass

class PrereqOr(PrereqNode):
    pass

class StarTransform:
    def __init__(self, source, path=True):
        # path is True when source is a file path; otherwise, source is data
        if path:
            self.rawdata = None
            self.from_path = source
        else:
            self.rawdata = source
            self.from_path = None
        self.rep = self.internal_rep()

    def internal_rep(self):
        raise NotImplementedError

    def validate_tag(self, tag):
        if not isinstance(tag, str):
            raise TypeError
        if tag[0] != '*':
            raise ValueError('invalid *DAS tag "' + tag +
                    '": tags start with an asterisk')
        if not tag[1:].isalnum():
            raise ValueError('invalid *DAS tag "' + tag + '": must be alphanumeric')

    @staticmethod
    def dumps(transform_inst):
        # Complete (invertible) string representation
        raise NotImplementedError

    @classmethod
    def writable(cls):
        # Override if self.dumps() is high-cost
        try:
            cls.dumps(None)
        except NotImplementedError:
            return False
        except Exception:
            pass
        return True

    @property
    def tag(self):
        return self.rep['tag']

    @property
    def title(self):
        return self.rep['title']

    @property
    def creator(self):
        return self.rep['creator']

    @property
    def create_time(self):
        return self.rep.get('create_time', None)

    @property
    def update_time(self):
        return self.rep.get('update_time', None)

    @property
    def description(self):
        return self.rep['description']

    @property
    def case(self):
        return self.rep['case']

    @property
    def prereqs(self):
        return self.rep.get('prereqs', '')

    @property
    def grants(self):
        return self.rep.get('grants', None)

    @property
    def grant_accs(self):
        return self.rep.get('grant_accs', None)


class PaperMDXform(StarTransform):
    def internal_rep(self):
        if not self.rawdata:
            with open(self.from_path) as f:
                self.rawdata = f.read()
        rep = {}
        rawdata = self.rawdata
        if rawdata[0] == '#':
             rawdata = rawdata[1:] # clean up initial # if no \n
        title_sec, *cert_parts = rawdata.split('\n#')
        title_line, *title_sec_lines = title_sec.split('\n')
        tag, *title = title_line.strip().split()
        tag = tag.strip()
        try:
            self.validate_tag(tag)
        except ValueError:
            if self.from_path:
                raise
            raise ValueError('format of starfile not loaded from valid path is invalid')
        rep['tag'] = tag
        rep['title'] = ' '.join(title)
        for named_line, possible_names in (
                ('creator', ('creator', 'by', 'maker', 'learner')),
                ('create_time', ('time', 'date', 'created')),
                ('update_time', ('revise', 'update', 'last'))):
            for title_sec_line in title_sec_lines:
                if ':' not in title_sec_line:
                    continue
                label, *line = title_sec_line.split(':')
                if any(p_name in label.lower() for p_name in possible_names):
                    rep[named_line] = ':'.join(line) # if there are multiple colons in this line, put them back
        for named_section, appearing_name in (
                ('description',)*2,
                ('case',)*2,
                ('prereqs','prerequisites'),
                ('grants',)*2,
                ('grant_accs', 'accepted grants')):
            for cert_part in cert_parts:
                lines = cert_part.strip().split('\n')
                if appearing_name in lines[0].lower():
                    rep[named_section] = '\n'.join(lines[1:])
        return rep;


class PaperWordDocXform(StarTransform):
    def internal_rep(self):
        if not self.from_path:
            raise ValueError('Word files must be specified by path.')
        doc = docx.Document(self.from_path)

        #scratch
        sections = []

        def extract_text(pp, prep=''):
            # dig recursively for text e.g. in hyperlinks
            ex = ''
            if pp.text and pp.text.strip():
                return prep + pp.text
            try:
                for el in pp._p:
                    ex = extract_text(el, ex)
            except AttributeError:
                for el in pp:
                    ex = extract_text(el, ex)
            return prep + ex

        for pp in doc.paragraphs:
            text = extract_text(pp)
            if not sections and not text.strip():
                continue
            if pp.style.name == 'Heading 1':
                sections.append([text.strip()])
                continue
            sections[-1].append(text.strip())

        rep = {}
        title_sec_lines, *cert_parts = sections
        tag, *title = title_sec_lines[0].split()
        title = ' '.join(title)
        self.validate_tag(tag)
        rep['tag'] = tag
        rep['title'] = title
        for named_line, possible_names in (
                ('creator', ('creator', 'by', 'maker', 'learner')),
                ('create_time', ('time', 'date', 'created')),
                ('update_time', ('revise', 'update', 'last'))):
            for title_sec_line in title_sec_lines:
                if ':' not in title_sec_line:
                    continue
                label, *line = title_sec_line.split(':')
                if any(p_name in label.lower() for p_name in possible_names):
                    rep[named_line] = ':'.join(line) # if there are multiple colons in this line, put them back
        for named_section, appearing_name in (
                ('description',)*2,
                ('case',)*2,
                ('prereqs','prerequisites'),
                ('grants',)*2,
                ('grant_accs', 'accepted grants')):
            for lines in cert_parts:
                if appearing_name in lines[0].lower():
                    rep[named_section] = '\n'.join(lines[1:])
        return rep;


class StarFileXform(StarTransform):
    def internal_rep(self):
        if not self.rawdata:
            with open(self.from_path) as f:
                self.rawdata = f.read()
        parse = json.loads(self.rawdata.replace('\n', ''))
        ver = parse['version']
        majv, minv, _ = ver.split('.')
        if int(majv) == 0 and int(minv) == 1:
            return parse['content']
        raise ValueError('unknown starfile version ' + ver)

    @staticmethod
    def dumps(source):
        natural_split_delimiter = '$$$nAtUrAlSpLiTdEliMiTeR_' + dastag() + '$$$'

        def natural_splitter(long_str):
            counter = 0
            for c in long_str:
                counter += 1
                if counter < 10:
                    yield c
                    continue
                if c == '\n':
                    yield natural_split_delimiter
                    yield c
                    counter = 0
                    continue
                if counter < 100:
                    yield c
                    continue
                if c in string.punctuation:
                    yield c
                    yield natural_split_delimiter
                    counter = 0
                    continue
                if counter < 600:
                    yield c
                    continue
                if c in string.whitespace:
                    yield c
                    yield natural_split_delimiter
                    counter = 0
                    continue
                yield c

        def natural_split(long_str):
            if not long_str:
                return long_str
            return ''.join(natural_splitter(long_str))

        json_str = json.dumps({'version':'0.1.1', 'content':{
                'tag':source.tag, 
                'title':source.title, 
                'creator':source.creator, 
                'create_time':source.create_time, 
                'update_time':source.update_time, 
                'description':natural_split(source.description), 
                'case':natural_split(source.case), 
                'prereqs':natural_split(source.prereqs), 
                'grants':natural_split(source.grants), 
                'grant_accs':natural_split(source.grant_accs)
                }}, sort_keys=True, separators=(',\n', ': '))

        return json_str.replace(natural_split_delimiter, '\n')

class CertView:
    CERTS = {}
    DEFAULT_TRANSFORMS = {
            'md':PaperMDXform,
            'docx':PaperWordDocXform,
            'doc': PaperWordDocXform,
            'starf':StarFileXform
            }

    def __init__(self, source, transform=None):
        extension = source.split('.')[-1]
        if transform:
            self.transform = transform
        elif extension in self.DEFAULT_TRANSFORMS:
            self.transform = self.DEFAULT_TRANSFORMS[extension]
        else:
            raise ValueError('Undefined transform for source ' + ('...' + source[-50:] if len(source) > 50 else source))
        self.content = self.transform(source)
        self.tag = self.content.tag
        self.CERTS[self.tag] = self

    def all_prereqs(self):
        # TODO: re-implement with a smarter method that respects tree structure
        def get_prereqs():
            for tag in self.CERTS:
                if tag in self.content.prereqs:
                    yield self.CERTS[tag]
        return list(get_prereqs())

    def save(self, path=None, transform=None, overwrite=False):
        if transform is None:
            transform = self.transform
        if not transform.writable():
            raise RuntimeError(transform.__name__ + ' is not writable')
        if path is None:
            path = self.transform.from_path
            if not path:
                raise ValueError('No default path remembered from creation. Specify path to save.')
        if not overwrite and os.path.exists(path):
            raise IOError("Can't save to " + path + ': file or directory already exists. force with overwrite=True.')
        dump_str = transform.dumps(self.content)
        with open(path, 'w+') as f:
            f.write(dump_str)

if __name__ == '__main__':
    try:
        cert = CertView(sys.argv[1])
    except IndexError:
        raise Exception('Must supply path to a valid *das certificate as first arg')
    print(cert.content.case)

