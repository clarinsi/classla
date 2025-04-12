"""
A trainer class to handle training and testing of models.
"""

import logging
import torch

from classla.models.common.trainer import Trainer as BaseTrainer
from classla.models.common import utils
from classla.models.srl.model import SRLTagger
from classla.models.srl.vocab import MultiVocab

logger = logging.getLogger('classla')

def unpack_batch(batch, use_cuda):
    """ Unpack a batch from the data loader. """
    if use_cuda:
        inputs = [b.cuda() if b is not None else None for b in batch[:11]]
    else:
        inputs = batch[:11]
    orig_idx = batch[11]
    sentlens = batch[12]
    return inputs, orig_idx, sentlens

class Trainer(BaseTrainer):
    """ A trainer for training models. """
    def __init__(self, args=None, vocab=None, pretrain=None, model_file=None, use_cuda=False):
        self.use_cuda = use_cuda
        if model_file is not None:
            # load everything from file
            self.load(model_file, pretrain=pretrain, args=args)
        else:
            assert all(var is not None for var in [args, vocab, pretrain])
            # build model from scratch
            self.args = args
            self.vocab = vocab
            self.model = SRLTagger(args, vocab, emb_matrix=pretrain.emb)
        self.parameters = [p for p in self.model.parameters() if p.requires_grad]
        if self.use_cuda:
            self.model.cuda()
        else:
            self.model.cpu()
        self.optimizer = utils.get_optimizer(self.args['optim'], self.parameters, self.args['lr'], betas=(0.9, self.args['beta2']), eps=1e-6)

    def update(self, batch, eval=False):
        inputs, orig_idx, sentlens = unpack_batch(batch, self.use_cuda)
        words, words_mask, deprel, head_words, xpos, lemma, head_lemma, head_xpos, pretrained, head_pretrained, srl = inputs

        if eval:
            self.model.eval()
        else:
            self.model.train()
            self.optimizer.zero_grad()
        loss, preds = self.model(words, words_mask, deprel, head_words, xpos, lemma, head_lemma, head_xpos, pretrained, head_pretrained, srl, orig_idx, sentlens)
        loss_val = loss.data.item()
        if eval:
            return loss_val

        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.args['max_grad_norm'])
        self.optimizer.step()
        return loss_val

    def predict(self, batch, unsort=True):
        inputs, orig_idx, sentlens = unpack_batch(batch, self.use_cuda)
        words, words_mask, deprel, head_words, xpos, lemma, head_lemma, head_xpos, pretrained, head_pretrained, srl = inputs

        self.model.eval()
        batch_size = words.size(0)
        _, preds = self.model(words, words_mask, deprel, head_words, xpos, lemma, head_lemma, head_xpos, pretrained, head_pretrained, srl, orig_idx, sentlens)

        # decode
        srl_seqs = [self.vocab['srl'].unmap(sent) for sent in preds[0].tolist()]

        pred_tokens = [[srl_seqs[i][j] for j in range(sentlens[i])] for i in range(batch_size)]
        if unsort:
            pred_tokens = utils.unsort(pred_tokens, orig_idx)
        return pred_tokens

    def save(self, filename, skip_modules=True):
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
        try:
            torch.save(params, filename)
            logger.info("Model saved to {}".format(filename))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logger.warning("Saving failed... continuing anyway.")

    def load(self, filename, pretrain=None, args=None):
        try:
            checkpoint = torch.load(filename, lambda storage, loc: storage, weights_only=False)
        except BaseException:
            logger.error("Cannot load model from {}".format(filename))
            raise
        self.args = checkpoint['config']
        if args: self.args.update(args)
        self.vocab = MultiVocab.load_state_dict(checkpoint['vocab'])
        self.model = SRLTagger(self.args, self.vocab, emb_matrix=pretrain.emb)
        self.model.load_state_dict(checkpoint['model'], strict=False)

