"""
Basic testing of dependency parser
"""

import classla
import classla.models.srl_tagger as trainer

from tests_classla import *

with open('test_data/slovenian.raw') as f:
    SL_DOC = f.read()

with open('test_data/slovenian.srl') as f:
    SL_DOC_GOLD = f.read()


def test_parser():
    nlp = classla.Pipeline(
        **{'processors': 'tokenize,pos,lemma,depparse,srl', 'dir': TEST_MODELS_DIR, 'lang': 'sl', 'type': 'standard_jos'})
    doc = nlp(SL_DOC)
    # with open('test_data/slovenian.srl', 'w') as f:
    #     f.write(doc.to_conll())
    assert SL_DOC_GOLD == doc.to_conll()

def test_parser_trainer():
    trainer.main(args=['--save_dir', 'test_data/train/data', '--save_name', 'srl.pt', '--train_file', 'test_data/train/srl_jos_example.conll',
                       '--eval_file', 'test_data/train/srl_jos_example.conll', '--output_file', 'test_data/train/data/srl', '--gold_file', 'test_data/train/srl_jos_example.conll', '--shorthand', 'sl_ssj',
                       '--mode', 'train', '--pretrain_file', 'classla_test/models/sl/pretrain/standard.pt', '--max_steps', '100'])
