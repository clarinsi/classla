import argparse
import copy
import csv
import logging
import time
import torch


def generate_new_composite_dict(path):
    composite_dict = {}
    with open(path) as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            # assert (row[0], row[2]) not in composite_dict, f'{(row[0], row[2])}: {row[1]}'
            composite_dict[(row[0].lower(), row[2])] = row[1]

    return composite_dict


def main(args):
    # new_comp_dict = generate_new_composite_dict(args.sloleks_path)
    logging.info('New composite dictionary generated!')

    try:
        checkpoint = torch.load(args.old_model_path, lambda storage, loc: storage)
    except BaseException:
        print("Cannot load model from {}".format(args.old_model_path))
        raise

    logging.info('Torch model loaded!')

    # checkpoint['dicts'] = (checkpoint['dicts'][0], new_comp_dict)
    del(checkpoint['dicts'])
    checkpoint['dicts'] = ({}, {})

    try:
        torch.save(checkpoint, args.new_model_path)
        print("model saved to {}".format(args.new_model_path))
    except BaseException:
        print("[Warning: Saving failed... continuing anyway.]")
    logging.info('Torch model saved!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Read already processed xmls, erase entries without examples and limit gigafida examples to 1 per entry.')
    parser.add_argument('--old_model_path', default='/home/luka/classla_resources/sl/lemma/standard.pt',
                        help='input file in (gz or xml currently). If none, then just database is loaded')
    parser.add_argument('--new_model_path', default='../TEST.pt',
                        help='input file in (gz or xml currently). If none, then just database is loaded')
    parser.add_argument('--sloleks_path', default='/home/luka/Development/classla/data/Sloleks2.0.MTE/sloleks_clarin_2.0-en.ud.tbl',
                        help='input file in (gz or xml currently). If none, then just database is loaded')
    args = parser.parse_args()

    start = time.time()
    main(args)
    logging.info("TIME: {}".format(time.time() - start))
