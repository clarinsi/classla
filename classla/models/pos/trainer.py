"""
A trainer class to handle training and testing of models.
"""

import sys
import logging
import torch
from torch import nn

from classla.models.common.trainer import Trainer as BaseTrainer
from classla.models.common import utils, loss
from classla.models.pos.model import Tagger
from classla.models.pos.postprocessor import InflectionalLexicon, DefaultPostprocessor
from classla.models.pos.vocab import MultiVocab

logger = logging.getLogger('classla')

def unpack_batch(batch, use_cuda):
    """ Unpack a batch from the data loader. """
    if use_cuda:
        inputs = [b.cuda() if b is not None else None for b in batch[:8]]
    else:
        inputs = batch[:8]
    orig_idx = batch[8]
    word_orig_idx = batch[9]
    sentlens = batch[10]
    wordlens = batch[11]
    word_string = batch[12]
    return inputs, orig_idx, word_orig_idx, sentlens, wordlens, word_string


class Trainer(BaseTrainer):
    """ A trainer for training models. """
    def __init__(self, args=None, vocab=None, pretrain=None, model_file=None, use_cuda=False):
        self.use_cuda = use_cuda
        if model_file is not None:
            # load everything from file
            self.load(model_file, pretrain)
        else:
            # build model from scratch
            self.args = args
            self.vocab = vocab
            self.model = Tagger(args, vocab, emb_matrix=pretrain.emb if pretrain is not None else None, share_hid=args['share_hid'])
            self.dict = None

        self.use_lexicon = args['use_lexicon'] if 'use_lexicon' in args else None
        self.pos_lemma_pretag = args['lemma_pretag'] if 'lemma_pretag' in args else None
        self.postprocessor = None
        if self.use_lexicon:
            args['shorthand'] = args['shorthand'] if 'shorthand' in args else self.args['shorthand']
            inflectional_lexicon = self.dict
            self.postprocessor = InflectionalLexicon(inflectional_lexicon, args['shorthand'], self.vocab, pretrain,
                                                     args['lemma_pretag'])
        else:
            if self.pos_lemma_pretag:
                self.postprocessor = DefaultPostprocessor(None, self.vocab, None, pos_lemma_pretag=self.pos_lemma_pretag)
            else:
                self.postprocessor = None
        self.parameters = [p for p in self.model.parameters() if p.requires_grad]
        if self.use_cuda:
            self.model.cuda()
        else:
            self.model.cpu()
        self.optimizer = utils.get_optimizer(self.args['optim'], self.parameters, self.args['lr'], betas=(0.9, self.args['beta2']), eps=1e-6)

    def update(self, batch, eval=False):
        inputs, orig_idx, word_orig_idx, sentlens, wordlens, word_string = unpack_batch(batch, self.use_cuda)
        word, word_mask, wordchars, wordchars_mask, upos, xpos, ufeats, pretrained = inputs

        if eval:
            self.model.eval()
        else:
            self.model.train()
            self.optimizer.zero_grad()
        loss, _ = self.model(word, word_mask, wordchars, wordchars_mask, upos, xpos, ufeats, pretrained, word_orig_idx, sentlens, wordlens, word_string)
        loss_val = loss.data.item()
        if eval:
            return loss_val

        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.args['max_grad_norm'])
        self.optimizer.step()
        return loss_val

    def predict(self, batch, unsort=True):
        inputs, orig_idx, word_orig_idx, sentlens, wordlens, word_string = unpack_batch(batch, self.use_cuda)
        word, word_mask, wordchars, wordchars_mask, upos, xpos, ufeats, pretrained = inputs

        self.model.eval()
        batch_size = word.size(0)
        _, preds = self.model(word, word_mask, wordchars, wordchars_mask, upos, xpos, ufeats, pretrained, word_orig_idx, sentlens, wordlens, word_string, postprocessor=self.postprocessor)

        # upos_seqs = [self.vocab['upos'].unmap(sent) for sent in preds[0].tolist()]
        # feats_seqs = [self.vocab['feats'].unmap(sent) for sent in preds[2].tolist()]

        if self.postprocessor is None:
            upos_seqs = [self.vocab['upos'].unmap(sent) for sent in preds[0].tolist()]
            xpos_seqs = [self.vocab['xpos'].unmap(sent) for sent in preds[1].tolist()]
            feats_seqs = [self.vocab['feats'].unmap(sent) for sent in preds[2].tolist()]
        else:
            upos_seqs = preds[0]
            xpos_seqs = preds[1]
            feats_seqs = preds[2]

        pred_tokens = [[[upos_seqs[i][j], xpos_seqs[i][j], feats_seqs[i][j]] for j in range(sentlens[i])] for i in range(batch_size)]
        if unsort:
            pred_tokens = utils.unsort(pred_tokens, orig_idx)
        return pred_tokens

    def save(self, filename, skip_modules=True, inflectional_lexicon=None):
        model_state = self.model.state_dict()
        # skip saving modules like pretrained embeddings, because they are large and will be saved in a separate file
        if skip_modules:
            skipped = [k for k in model_state.keys() if k.split('.')[0] in self.model.unsaved_modules]
            for k in skipped:
                del model_state[k]
        params = {
                'model': model_state,
                'vocab': self.vocab.state_dict(),
                'config': self.args
                }
        if inflectional_lexicon:
            params['dicts'] = inflectional_lexicon

        try:
            torch.save(params, filename)
            logger.info("Model saved to {}".format(filename))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logger.warning("Saving failed... continuing anyway.")

    def load(self, filename, pretrain):
        """
        Load a model from file, with preloaded pretrain embeddings. Here we allow the pretrain to be None or a dummy input,
        and the actual use of pretrain embeddings will depend on the boolean config "pretrain" in the loaded args.
        """
        try:
            checkpoint = torch.load(filename, lambda storage, loc: storage, weights_only=False)
        except BaseException:
            logger.error("Cannot load model from {}".format(filename))
            raise
        self.args = checkpoint['config']
        self.vocab = MultiVocab.load_state_dict(checkpoint['vocab'])
        # load model
        emb_matrix = None
        if self.args['pretrain'] and pretrain is not None: # we use pretrain only if args['pretrain'] == True and pretrain is not None
            emb_matrix = pretrain.emb
        self.model = Tagger(self.args, self.vocab, emb_matrix=emb_matrix, share_hid=self.args['share_hid'])
        self.model.load_state_dict(checkpoint['model'], strict=False)
        self.dict = checkpoint['dicts'] if 'dicts' in checkpoint else None

    @staticmethod
    def load_inflectional_lexicon(filename):
        try:
            checkpoint = torch.load(filename, lambda storage, loc: storage, weights_only=False)
        except BaseException:
            logger.error("Cannot load model from {}".format(filename))
            raise

        inf_lexicon = {}
        assert 'dicts' in checkpoint, Exception('Can not load inflectional dictionary. Make sure that your tagger model has it.')
        for entry in checkpoint['dicts']:
            if (entry[0], entry[1]) not in inf_lexicon:
                inf_lexicon[(entry[0], entry[1])] = entry[4]

        return inf_lexicon
