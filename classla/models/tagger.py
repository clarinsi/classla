"""
Entry point for training and evaluating a POS/morphological features tagger.

This tagger uses highway BiLSTM layers with character and word-level representations, and biaffine classifiers
to produce consistant POS and UFeats predictions.
For details please refer to paper: https://nlp.stanford.edu/pubs/qi2018universal.pdf.
"""
import csv
import sys
import os
import shutil
import time
from collections import Counter
from datetime import datetime
import argparse
import numpy as np
import random
import torch
from torch import nn, optim

from classla.models.pos.data import DataLoader
from classla.models.pos.trainer import Trainer
from classla.models.pos import scorer
from classla.models.common import utils
from classla.models.common.pretrain import Pretrain
from classla.models.common.doc import *
from classla.utils.conll import CoNLL
from classla.models import _training_logging

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='data/pos', help='Root dir for saving models.')
    parser.add_argument('--wordvec_dir', type=str, default='extern_data/word2vec', help='Directory of word vectors.')
    parser.add_argument('--wordvec_file', type=str, default=None, help='Word vectors filename.')
    parser.add_argument('--train_file', type=str, default=None, help='Input file for data loader.')
    parser.add_argument('--eval_file', type=str, default=None, help='Input file for data loader.')
    parser.add_argument('--output_file', type=str, default=None, help='Output CoNLL-U file.')
    parser.add_argument('--gold_file', type=str, default=None, help='Output CoNLL-U file.')
    parser.add_argument('--pretrain_file', type=str, default=None, help='Input file containing pretrained data.')
    parser.add_argument('--use_lexicon', type=str, default=None, help="Input location of lemmatization model.")
    parser.add_argument('--inflectional_lexicon_path', type=str, default=None, help="Input location of inflectional lexicon (i.e. sloleks).")
    parser.add_argument('--lemma_pretag', action='store_true', help="Use pretag from tokenization processor.")

    parser.add_argument('--mode', default='train', choices=['train', 'predict'])
    parser.add_argument('--lang', type=str, help='Language')
    parser.add_argument('--shorthand', type=str, help="Treebank shorthand")

    parser.add_argument('--hidden_dim', type=int, default=200)
    parser.add_argument('--char_hidden_dim', type=int, default=400)
    parser.add_argument('--deep_biaff_hidden_dim', type=int, default=400)
    parser.add_argument('--composite_deep_biaff_hidden_dim', type=int, default=100)
    parser.add_argument('--word_emb_dim', type=int, default=75)
    parser.add_argument('--char_emb_dim', type=int, default=100)
    parser.add_argument('--tag_emb_dim', type=int, default=50)
    parser.add_argument('--transformed_dim', type=int, default=125)
    parser.add_argument('--num_layers', type=int, default=2)
    parser.add_argument('--char_num_layers', type=int, default=1)
    parser.add_argument('--pretrain_max_vocab', type=int, default=250000)
    parser.add_argument('--word_dropout', type=float, default=0.33)
    parser.add_argument('--dropout', type=float, default=0.5)
    parser.add_argument('--rec_dropout', type=float, default=0, help="Recurrent dropout")
    parser.add_argument('--char_rec_dropout', type=float, default=0, help="Recurrent dropout")
    parser.add_argument('--no_char', dest='char', action='store_false', help="Turn off character model.")
    parser.add_argument('--no_pretrain', dest='pretrain', action='store_false', help="Turn off pretrained embeddings.")
    parser.add_argument('--share_hid', action='store_true', help="Share hidden representations for UPOS, XPOS and UFeats.")
    parser.set_defaults(share_hid=False)

    parser.add_argument('--sample_train', type=float, default=1.0, help='Subsample training data.')
    parser.add_argument('--optim', type=str, default='adam', help='sgd, adagrad, adam or adamax.')
    parser.add_argument('--lr', type=float, default=3e-3, help='Learning rate')
    parser.add_argument('--beta2', type=float, default=0.95)

    parser.add_argument('--max_steps', type=int, default=50000)
    parser.add_argument('--eval_interval', type=int, default=100)
    parser.add_argument('--fix_eval_interval', dest='adapt_eval_interval', action='store_false', \
            help="Use fixed evaluation interval for all treebanks, otherwise by default the interval will be increased for larger treebanks.")
    parser.add_argument('--max_steps_before_stop', type=int, default=3000)
    parser.add_argument('--batch_size', type=int, default=5000)
    parser.add_argument('--max_grad_norm', type=float, default=1.0, help='Gradient clipping.')
    parser.add_argument('--log_step', type=int, default=20, help='Print log every k steps.')
    parser.add_argument('--save_dir', type=str, default='saved_models/pos', help='Root dir for saving models.')
    parser.add_argument('--save_name', type=str, default=None, help="File name to save the model")

    parser.add_argument('--seed', type=int, default=1234)
    parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
    parser.add_argument('--cpu', action='store_true', help='Ignore CUDA.')
    args = parser.parse_args(args=args)
    return args


def main(args=None):
    sys.setrecursionlimit(50000)

    args = parse_args(args=args)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    if args.cpu:
        args.cuda = False
    elif args.cuda:
        torch.cuda.manual_seed(args.seed)

    args = vars(args)
    print("Running tagger in {} mode".format(args['mode']))

    if args['mode'] == 'train':
        train(args)
    else:
        evaluate(args)


def generate_new_composite_dict(inflectional_lexicon_path, train_batch):
    # generate initial composite dictionary from all train data
    train_dict = train_batch.doc.get([TEXT, XPOS, UPOS, FEATS, LEMMA])
    inflectional_dict = set()

    lemmas_frequencies = {}
    # get lemma frequencies
    with open(inflectional_lexicon_path) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter='\t')
        for row in csv_reader:
            if row[0] == 'FORM' and row[1] == 'LEMMA':   # ignore header line
                continue

            # if row[6] is not float
            if re.match(r'^-?\d+(?:\.\d+)$', row[6]) is None:
                lemmas_frequencies[row[1]] = float(row[3]) if row[1] not in lemmas_frequencies else lemmas_frequencies[
                                                                                                        row[1]] + float(
                    row[3])
                upos_ufeats = row[6].split()
                ufeats = '|'.join(sorted(upos_ufeats[1:], key=lambda x: x.lower())) if upos_ufeats[1:] else '_'
                inflectional_dict.add((row[0].lower(), row[2], upos_ufeats[0],
                                       ufeats, float(row[3]), row[1]))

            else:
                lemmas_frequencies[row[1]] = float(row[6]) if row[1] not in lemmas_frequencies else lemmas_frequencies[row[1]] + float(row[6])
                # '_' fix
                ufeats = row[5] if row[5] else '_'
                inflectional_dict.add((row[0].lower(), row[3], row[4], ufeats, float(row[6]), row[1]))

    composite_dict = sorted(inflectional_dict, key=lambda x: x[4], reverse=True)
    all_keys = {}

    cleaned_composite_dict = []
    i = 0
    for el in composite_dict:
        if (el[0], el[1], el[2], el[3]) not in all_keys:
            all_keys[(el[0], el[1], el[2], el[3])] = (el, i)
            cleaned_composite_dict.append((el[0], el[1], el[2], el[3], el[5]))
            i += 1
        else:
            if el[5] in lemmas_frequencies and all_keys[(el[0], el[1], el[2], el[3])][0][5] in lemmas_frequencies and \
                    lemmas_frequencies[all_keys[(el[0], el[1], el[2], el[3])][0][5]] < lemmas_frequencies[el[5]]:
                old_el, updating_index = all_keys[(el[0], el[1], el[2], el[3])]
                all_keys[(el[0], el[1], el[2], el[3])] = (el, updating_index)
                cleaned_composite_dict[updating_index] = (el[0], el[1], el[2], el[3], el[5])

    train_dict = [(el[0], el[1], el[2], el[3], el[4]) if el[3] is not None else (el[0], el[1], el[2], '_', el[4])
                  for el in train_dict]
    train_dict_most_common = Counter(train_dict).most_common()
    filtered_train_dict = [el[0] for el in train_dict_most_common
                           if (el[0][0], el[0][1], el[0][2], el[0][3]) not in all_keys]
    cleaned_composite_dict.extend(filtered_train_dict)
    return cleaned_composite_dict


def train(args):
    utils.ensure_dir(args['save_dir'])
    model_file = args['save_dir'] + '/' + args['save_name'] if args['save_name'] is not None \
            else '{}/{}_tagger.pt'.format(args['save_dir'], args['shorthand'])

    # load pretrained vectors
    vec_file = args['wordvec_file']

    pretrain_file = '{}/{}.pretrain.pt'.format(args['save_dir'], args['shorthand']) if args['pretrain_file'] is None \
        else args['pretrain_file']
    pretrain = Pretrain(pretrain_file, vec_file, args['pretrain_max_vocab'])


    # load data
    print("Loading data with batch size {}...".format(args['batch_size']))
    doc, metasentences = CoNLL.conll2dict(input_file=args['train_file'])
    train_doc = Document(doc, metasentences=metasentences)
    train_batch = DataLoader(train_doc, args['batch_size'], args, pretrain, evaluation=False)
    vocab = train_batch.vocab

    # create inflectional_lexicon
    inflectional_lexicon = generate_new_composite_dict(args['inflectional_lexicon_path'], train_batch) if args['inflectional_lexicon_path'] else None

    doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
    dev_doc = Document(doc, metasentences=metasentences)
    dev_batch = DataLoader(dev_doc, args['batch_size'], args, pretrain, vocab=vocab, evaluation=True, sort_during_eval=True)

    # pred and gold path
    system_pred_file = args['output_file']
    gold_file = args['gold_file']

    # skip training if the language does not have training or dev data
    if len(train_batch) == 0 or len(dev_batch) == 0:
        print("Skip training because no data available...")
        sys.exit(0)

    print("Training tagger...")
    trainer = Trainer(args=args, vocab=vocab, pretrain=pretrain, use_cuda=args['cuda'])

    global_step = 0
    max_steps = args['max_steps']
    dev_score_history = []
    best_dev_preds = []
    current_lr = args['lr']
    global_start_time = time.time()
    format_str = '{}: step {}/{}, loss = {:.6f} ({:.3f} sec/batch), lr: {:.6f}'

    if args['adapt_eval_interval']:
        args['eval_interval'] = utils.get_adaptive_eval_interval(dev_batch.num_examples, 2000, args['eval_interval'])
        print("Evaluating the model every {} steps...".format(args['eval_interval']))

    using_amsgrad = False
    last_best_step = 0
    # start training
    train_loss = 0
    while True:
        do_break = False
        for i, batch in enumerate(train_batch):
            start_time = time.time()
            global_step += 1
            loss = trainer.update(batch, eval=False) # update step
            train_loss += loss
            if global_step % args['log_step'] == 0:
                duration = time.time() - start_time
                print(format_str.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), global_step,\
                        max_steps, loss, duration, current_lr))

            if global_step % args['eval_interval'] == 0:
                # eval on dev
                print("Evaluating on dev set...")
                dev_preds = []
                for batch in dev_batch:
                    preds = trainer.predict(batch)
                    dev_preds += preds
                dev_preds = utils.unsort(dev_preds, dev_batch.data_orig_idx)
                dev_batch.doc.set([UPOS, XPOS, FEATS], [y for x in dev_preds for y in x])
                CoNLL.dict2conll(dev_batch.doc.to_dict(), system_pred_file)
                _, _, dev_score = scorer.score(system_pred_file, gold_file)

                train_loss = train_loss / args['eval_interval'] # avg loss per batch
                print("step {}: train_loss = {:.6f}, dev_score = {:.4f}".format(global_step, train_loss, dev_score))
                train_loss = 0

                # save best model
                if len(dev_score_history) == 0 or dev_score > max(dev_score_history):
                    last_best_step = global_step
                    trainer.save(model_file, inflectional_lexicon=inflectional_lexicon)
                    print("new best model saved.")
                    best_dev_preds = dev_preds

                dev_score_history += [dev_score]
                print("")

            if global_step - last_best_step >= args['max_steps_before_stop']:
                if not using_amsgrad:
                    print("Switching to AMSGrad")
                    last_best_step = global_step
                    using_amsgrad = True
                    trainer.optimizer = optim.Adam(trainer.model.parameters(), amsgrad=True, lr=args['lr'], betas=(.9, args['beta2']), eps=1e-6)
                else:
                    do_break = True
                    break

            if global_step >= args['max_steps']:
                do_break = True
                break

        if do_break: break

        train_batch.reshuffle()

    print("Training ended with {} steps.".format(global_step))

    best_f, best_eval = max(dev_score_history)*100, np.argmax(dev_score_history)+1
    print("Best dev F1 = {:.2f}, at iteration = {}".format(best_f, best_eval * args['eval_interval']))

def evaluate(args):
    # file paths
    system_pred_file = args['output_file']
    gold_file = args['gold_file']
    model_file = args['save_dir'] + '/' + args['save_name'] if args['save_name'] is not None \
            else '{}/{}_tagger.pt'.format(args['save_dir'], args['shorthand'])

    pretrain_file = '{}/{}.pretrain.pt'.format(args['save_dir'], args['shorthand']) if args['pretrain_file'] is None \
        else args['pretrain_file']
    pretrain = Pretrain(pretrain_file)

    # load model
    print("Loading model from: {}".format(model_file))
    use_cuda = args['cuda'] and not args['cpu']
    trainer = Trainer(args=args, pretrain=pretrain, model_file=model_file, use_cuda=use_cuda)
    loaded_args, vocab = trainer.args, trainer.vocab

    # load config
    for k in args:
        if k.endswith('_dir') or k.endswith('_file') or k in ['shorthand'] or k == 'mode':
            loaded_args[k] = args[k]

    # load data
    print("Loading data with batch size {}...".format(args['batch_size']))
    doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
    doc = Document(doc, metasentences=metasentences)
    batch = DataLoader(doc, args['batch_size'], loaded_args, pretrain, vocab=vocab, evaluation=True, sort_during_eval=True)
    if len(batch) > 0:
        print("Start evaluation...")
        preds = []
        for i, b in enumerate(batch):
            preds += trainer.predict(b)
    else:
        # skip eval if dev data does not exist
        preds = []
    preds = utils.unsort(preds, batch.data_orig_idx)

    # write to file and score
    batch.doc.set([UPOS, XPOS, FEATS], [y for x in preds for y in x])
    CoNLL.dict2conll(batch.doc.to_dict(), system_pred_file)

    if gold_file is not None:
        _, _, score = scorer.score(system_pred_file, gold_file)

        print("Tagger score:")
        print("{} {:.2f}".format(args['shorthand'], score*100))

if __name__ == '__main__':
    main()
