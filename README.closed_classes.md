# Documentation on how closed classes are dealt with

Depending on the status of the two parameters, ```pos_lemma_pretag``` and ```pos_use_lexicon```, different XPOS and UPOS are considered to be "closed class". The control of the closed classes comes from the tokenizer (if ```pos_lemma_pretag``` is used) and from the inflectional lexicon (if ```pos_use_lexicon``` is used). The overall logic of closed classes is that tokens can be tagged as closed classes only by the two relevant information sources (tokenizer, lexicon). Closed class control on the level of XPOS and UPOS are dealt with separately.

## XPOS control

This decision diagram defines the list of closed classes depending on the combination of the two relevant parameters. Important is to not that the first two options are available only for Slovenian. The `punct` tag is the Bulgarian variant of the `Z` tag.

```
pos_lemma_pretag==True &  pos_use_lexicon==True || closed_classes_xpos = ['P', 'S', 'C', 'Q', 'Z', 'punct']
pos_lemma_pretag==False &  pos_use_lexicon==True || closed_classes_xpos = ['P', 'S', 'C', 'Q']
pos_lemma_pretag==True &  pos_use_lexicon==False || closed_classes_xpos = ['Z', 'punct']
pos_lemma_pretag==False &  pos_use_lexicon==False || closed_classes_xpos = []
```

## UPOS control

For UPOS the situation is rather similar as with XPOS. The first two cases are available for Slovenian only.

```
pos_lemma_pretag==True &  pos_use_lexicon==True || closed_classes_upos = ['PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'PUNCT', 'SYM']
pos_lemma_pretag==False &  pos_use_lexicon==True || closed_classes_upos = ['PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART']
pos_lemma_pretag==True &  pos_use_lexicon==False || closed_classes_upos = ['PUNCT', 'SYM']
pos_lemma_pretag==False &  pos_use_lexicon==False || closed_classes_upos = []
```
