"""
Utility functions for the loading and conversion of CoNLL-format files.
"""
import os
import io

FIELD_NUM = 10

ID = 'id'
TEXT = 'text'
LEMMA = 'lemma'
UPOS = 'upos'
XPOS = 'xpos'
FEATS = 'feats'
HEAD = 'head'
DEPREL = 'deprel'
DEPS = 'deps'
MISC = 'misc'
NER = 'ner'
SRL = 'srl'
FIELD_TO_IDX = {ID: 0, TEXT: 1, LEMMA: 2, UPOS: 3, XPOS: 4, FEATS: 5, HEAD: 6, DEPREL: 7, DEPS: 8, MISC: 9}


class ListMetadata:
    def __init__(self, array, metadata):
        self.list = array
        self.metadata = metadata

    def __iter__(self):
        for el in self.list:
            yield el


class CoNLL:
    @staticmethod
    def load_conll(f, ignore_gapping=True, generate_raw_text=False):
        """ Load the file or string into the CoNLL-U format data.
        Input: file or string reader, where the data is in CoNLL-U format.
        Output: a list of list of list for each token in each sentence in the data, where the innermost list represents
        all fields of a token.
        """
        doc, sent, metadata, raw_text = [], [], '', ''
        for line in f:
            raw_line = line
            line = line.strip()
            if len(line) == 0:
                if len(sent) > 0:
                    if generate_raw_text:
                        doc.append((sent, metadata, raw_text))
                    else:
                        doc.append((sent, metadata))
                    metadata = ''
                    sent = []
            else:
                if line.startswith('#'): # skip comment line
                    metadata += raw_line
                    if generate_raw_text and line.startswith('# text = '):
                        raw_text = line[9:]
                    continue
                array = line.split('\t')
                if ignore_gapping and '.' in array[0]:
                    continue
                assert len(array) == FIELD_NUM, \
                        f"Cannot parse CoNLL line: expecting {FIELD_NUM} fields, {len(array)} found."
                sent += [array]
        if len(sent) > 0:
            if generate_raw_text:
                doc.append((sent, metadata, raw_text))
            else:
                doc.append((sent, metadata))
        return doc

    @staticmethod
    def convert_conll(doc_conll, generate_raw_text=False):
        """ Convert the CoNLL-U format input data to a dictionary format output data.
        Input: list of token fields loaded from the CoNLL-U format data, where the outmost list represents a list of sentences, and the inside list represents all fields of a token.
        Output: a list of list of dictionaries for each token in each sentence in the document.
        """
        doc_dict = []
        metadata_list = []
        raw_text_list = []
        for sent in doc_conll:
            if generate_raw_text:
                sent_conll, metadata, raw_text = sent
                raw_text_list.append(raw_text)
            else:
                sent_conll, metadata = sent
            sent_dict = []
            for token_conll in sent_conll:
                token_dict = CoNLL.convert_conll_token(token_conll)
                sent_dict.append(token_dict)
            metadata_list.append(metadata)
            doc_dict.append(sent_dict)
        if generate_raw_text:
            return doc_dict, metadata_list, ' '.join(raw_text_list)
        return doc_dict, metadata_list

    @staticmethod
    def convert_conll_token(token_conll):
        """ Convert the CoNLL-U format input token to the dictionary format output token.
        Input: a list of all CoNLL-U fields for the token.
        Output: a dictionary that maps from field name to value.
        """
        token_dict = {}
        for field in FIELD_TO_IDX:
            value = token_conll[FIELD_TO_IDX[field]]
            if value != '_':
                if field == HEAD:
                    token_dict[field] = int(value)
                elif field == ID:
                    token_dict[field] = tuple(int(x) for x in value.split('-'))
                else:
                    token_dict[field] = value
            # special case if text is '_'
            if token_conll[FIELD_TO_IDX[TEXT]] == '_':
                token_dict[TEXT] = token_conll[FIELD_TO_IDX[TEXT]]
                token_dict[LEMMA] = token_conll[FIELD_TO_IDX[LEMMA]]
        return token_dict

    @staticmethod
    def conll2dict(input_file=None, input_str=None, ignore_gapping=True, generate_raw_text=False):
        """ Load the CoNLL-U format data from file or string into lists of dictionaries.
        """
        assert any([input_file, input_str]) and not all([input_file, input_str]), 'either input input file or input string'
        if input_str:
            infile = io.StringIO(input_str)
        else:
            infile = open(input_file)
        doc_conll = CoNLL.load_conll(infile, ignore_gapping, generate_raw_text)
        doc_dict = CoNLL.convert_conll(doc_conll, generate_raw_text)
        return doc_dict

    @staticmethod
    def convert_dict(doc_dict):
        """ Convert the dictionary format input data to the CoNLL-U format output data. This is the reverse function of
        `convert_conll`.
        Input: dictionary format data, which is a list of list of dictionaries for each token in each sentence in the data.
        Output: CoNLL-U format data, which is a list of list of list for each token in each sentence in the data.
        """
        doc_conll = []
        for sent_dict, metadata in doc_dict:
            sent_conll = []
            for token_dict in sent_dict:
                token_conll = CoNLL.convert_token_dict(token_dict)
                sent_conll.append(token_conll)
            doc_conll.append((sent_conll, metadata))
        return doc_conll

    @staticmethod
    def convert_token_dict(token_dict):
        """ Convert the dictionary format input token to the CoNLL-U format output token. This is the reverse function of
        `convert_conll_token`.
        Input: dictionary format token, which is a dictionaries for the token.
        Output: CoNLL-U format token, which is a list for the token.
        """
        token_conll = ['_' for i in range(FIELD_NUM)]
        misc_dict = {}
        for key in token_dict:
            if key == ID:
                token_conll[FIELD_TO_IDX[key]] = '-'.join([str(x) for x in token_dict[key]]) if isinstance(token_dict[key], tuple) else str(token_dict[key])
            elif key == NER:
                misc_dict['NER'] = str(token_dict[key])
            elif key == SRL:
                misc_dict['SRL'] = str(token_dict[key])
            elif key == MISC:
                for misc in str(token_dict[key]).split('|'):
                    misc_key, misc_val = misc.split('=')
                    if misc_key not in [NER, SRL]:
                        misc_dict[misc_key] = misc_val
            elif key in FIELD_TO_IDX:
                token_conll[FIELD_TO_IDX[key]] = str(token_dict[key])
        token_conll[FIELD_TO_IDX[MISC]] = '|'.join([k + '=' + v for k, v in sorted(misc_dict.items(), key=lambda item: item[0].lower())]) if misc_dict else '_'
        return token_conll

    @staticmethod
    def conll_as_string(doc):
        """ Dump the loaded CoNLL-U format list data to string. """
        return_string = ""
        for sent, meta in doc:
            return_string += meta if meta else ''
            for ln in sent:
                return_string += ("\t".join(ln)+"\n")
            return_string += "\n"
        return return_string

    @staticmethod
    def dict2conll(doc_dict, filename):
        """ Convert the dictionary format input data to the CoNLL-U format output data and write to a file.
        """
        doc_conll = CoNLL.convert_dict(doc_dict)
        conll_string = CoNLL.conll_as_string(doc_conll)
        with open(filename, 'w') as outfile:
            outfile.write(conll_string)
        return

    @staticmethod
    def write_doc2conll(doc, filename):
        """ Writes the doc as a conll file to the given filename
        """
        with open(filename, 'w', encoding='utf-8') as outfile:
            outfile.write(CoNLL.conll_as_string(CoNLL.convert_dict(doc.to_dict())))
