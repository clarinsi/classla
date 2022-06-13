"""
Basic testing of dependency parser
"""

import classla
from classla.utils.conll import CoNLL

from tests_classla import *

with open('test_data/slovenian.raw') as f:
    SL_DOC = f.read()

with open('test_data/slovenian.parser') as f:
    SL_DOC_GOLD = f.read()


def test_parser():
    nlp = classla.Pipeline(
        **{'processors': 'tokenize,pos,lemma,depparse', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    # with open('test_data/slovenian.parser', 'w') as f:
    #     f.write(doc.to_conll())
    assert SL_DOC_GOLD == doc.to_conll()
