# A [CLASSLA](http://www.clarin.si/info/k-centre/) Fork of [Stanza](https://github.com/stanfordnlp/stanza) for Processing Slovenian, Croatian, Serbian, Macedonian and Bulgarian

## Description

This pipeline allows for processing of standard Slovenian, Croatian, Serbian and Bulgarian on the levels of

- tokenization and sentence splitting
- part-of-speech tagging
- lemmatization
- dependency parsing
- named entity recognition

It also allows for processing of standard Macedonian on the levels of

- tokenization and sentence splitting
- part-of-speech tagging
- lemmatization

Finally, it allows for processing of non-standard (Internet) Slovenian, Croatian and Serbian on the same levels as standard language (all models are tailored to non-standard language except for dependency parsing where the standard module is used).

## Differences to Stanza

The differences of this pipeline to the original Stanza pipeline are the following:

- usage of language-specific rule-based tokenizers and sentence splitters, [obeliks](https://pypi.org/project/obeliks/) for standard Slovenian and [reldi-tokeniser](https://pypi.org/project/reldi-tokeniser/) for the remaining varieties and languages (Stanza uses inferior machine-learning-based tokenization and sentence splitting trained on UD data)
- default pre-tagging and pre-lemmatization on the level of tokenizers for the following phenomena: punctuation, symbol, e-mail, URL, mention, hashtag, emoticon, emoji (usage documented [here](https://github.com/clarinsi/classla/blob/master/README.superuser.md#usage-of-tagging-control-via-the-tokenizer))
- optional control of the tagger for Slovenian via an inflectional lexicon on the levels of XPOS, UPOS, FEATS (usage documented [here](https://github.com/clarinsi/classla/blob/master/README.superuser.md#usage-of-inflectional-lexicon))
- closed class handling depending on the usage of the options described in the last two bullets, as documented [here](https://github.com/clarinsi/classla/blob/master/README.closed_classes.md)
- usage of external inflectional lexicons for lookup lemmatization, seq2seq being used very infrequently on OOVs only (Stanza uses only UD training data for lookup lemmatization)
- morphosyntactic tagging models based on larger quantities of training data than is available in UD (training data that are morphosyntactically tagged, but not UD-parsed)
- lemmatization models based on larger quantities of training data than is available in UD (training data that are lemmatized, but not UD-parsed)
- optional JOS-project-based parsing of Slovenian (usage documented [here](https://github.com/clarinsi/classla/blob/master/README.superuser.md#jos-dependency-parsing-system))
- named entity recognition models for all languages except Macedonian (Stanza does not cover named entity recognition for any of the languages supported by classla)
- Macedonian models (Macedonian is not available in UD yet)
- non-standard models for Croatian, Slovenian, Serbian (there is no UD data for these varieties)

The above modifications led to some important improvements in the tool's performance in comparison to original Stanza. For standard Slovenian, comparing the CLASSLA-Stanza tool with Stanza on the [SloBENCH benchmark](https://slobench.cjvt.si/leaderboard/view/11), shows relative error reduction (part of the error removed by moving from Stanza to CLASSLA-Stanza) on sentence segmentation to be 98%, on token segmentation 50%, on lemmatization 69%, on morphosyntactic XPOS tagging 65%, and on dependency parsing 34%.

## Citing

If you use this tool, please cite the following paper:

```
@inproceedings{ljubesic_2024_13936406,
  title        = {{CLASSLA-Stanza: The Next Step for Linguistic 
                   Processing of South Slavic Languages}},
  author       = {Nikola Ljube\v{s}i\'{c} and Luka Ter\v{c}on and Kaja Dobrovoljc},
  year         = 2024,
  booktitle    = {Conference on Language Technologies and Digital Humanities (JT-DH-2024)},
  address      = {Ljubljana, Slovenia},
  publisher    = {Institute of Contemporary History},
  doi          = {10.5281/zenodo.13936406},
  url          = {https://doi.org/10.5281/zenodo.13936406}
}

```


## Installation
### pip
We recommend that you install CLASSLA via pip, the Python package manager. To install, run:
```bash
pip install classla
```
This will also resolve all dependencies.

__NOTE TO EXISTING USERS__: Once you install this classla version, you will HAVE TO re-download the models. All previously downloaded models will not be used anymore. We suggest you delete the old models. Their default location is at `~/classla_resources`.

## Running CLASSLA

### Getting started

To run the CLASSLA pipeline for the first time on processing standard Slovenian, follow these steps:

```
>>> import classla
>>> classla.download('sl')                            # download standard models for Slovenian, use hr for Croatian, sr for Serbian, bg for Bulgarian, mk for Macedonian
>>> nlp = classla.Pipeline('sl')                      # initialize the default Slovenian pipeline, use hr for Croatian, sr for Serbian, bg for Bulgarian, mk for Macedonian
>>> doc = nlp("France Prešeren je rojen v Vrbi.")     # run the pipeline
>>> print(doc.to_conll())                             # print the output in CoNLL-U format
# newpar id = 1
# sent_id = 1.1
# text = France Prešeren je rojen v Vrbi.
1	France	France	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	4	nsubj	_	NER=B-PER
2	Prešeren	Prešeren	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	flat:name	_	NER=I-PER
3	je	biti	AUX	Va-r3s-n	Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin	4	cop	_	NER=O
4	rojen	rojen	ADJ	Appmsnn	Case=Nom|Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing|VerbForm=Part	0	root	_	NER=O
5	v	v	ADP	Sl	Case=Loc	6	case	_	NER=O
6	Vrbi	Vrba	PROPN	Npfsl	Case=Loc|Gender=Fem|Number=Sing	4	obl	_	NER=B-LOC|SpaceAfter=No
7	.	.	PUNCT	Z	_	4	punct	_	NER=O

```
You can find examples of standard language processing for [Croatian](#example-of-standard-croatian), [Serbian](#example-of-standard-serbian), [Macedonian](#example-of-standard-macedonian) and [Bulgarian](#example-of-standard-bulgarian) at the end of this document.

### Processing non-standard language

Processing non-standard Slovenian differs to the above standard example just by an additional argument ```type="nonstandard"```:

```
>>> import classla
>>> classla.download('sl', type='nonstandard')        # download non-standard models for Slovenian, use hr for Croatian and sr for Serbian
>>> nlp = classla.Pipeline('sl', type='nonstandard')  # initialize the default non-standard Slovenian pipeline, use hr for Croatian and sr for Serbian
>>> doc = nlp("kva smo mi zurali zadnje leto v zagrebu...")     # run the pipeline
>>> print(doc.to_conll())                             # print the output in CoNLL-U format
# newpar id = 1
# sent_id = 1.1
# text = kva smo mi zurali zadnje leto v zagrebu...
1	kva	kaj	PRON	Pq-nsa	Case=Acc|Gender=Neut|Number=Sing|PronType=Int	4	obj	_	NER=O
2	smo	biti	AUX	Va-r1p-n	Mood=Ind|Number=Plur|Person=1|Polarity=Pos|Tense=Pres|VerbForm=Fin	4	aux	_	NER=O
3	mi	jaz	PRON	Pp1mpn	Case=Nom|Gender=Masc|Number=Plur|Person=1|PronType=Prs	4	nsubj	_	NER=O
4	zurali	zurati	VERB	Vmpp-pm	Aspect=Imp|Gender=Masc|Number=Plur|VerbForm=Part	0	root	_	NER=O
5	zadnje	zadnji	ADJ	Agpnsa	Case=Acc|Degree=Pos|Gender=Neut|Number=Sing	6	amod	_	NER=O
6	leto	leto	NOUN	Ncnsa	Case=Acc|Gender=Neut|Number=Sing	4	obl	_	NER=O
7	v	v	ADP	Sl	Case=Loc	8	case	_	NER=O
8	zagrebu	Zagreb	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	4	obl	_	NER=B-LOC|SpaceAfter=No
9	...	...	PUNCT	Z	_	4	punct	_	NER=O

```

You can find examples of non-standard language processing for [Croatian](#example-of-non-standard-croatian) and [Serbian](#example-of-non-standard-serbian)  at the end of this document.

For additional usage examples you can also consult the ```pipeline_demo.py``` file.

### Processing online texts

A special web processing mode for processing texts obtained from the internet can be activated with the ```type="web"``` argument.

```
>>> import classla
>>> classla.download('sl', type='web')        # download web models for Slovenian, use hr for Croatian and sr for Serbian
>>> nlp = classla.Pipeline('sl', type='web')  # initialize the default Slovenian web pipeline, use hr for Croatian and sr for Serbian
>>> doc = nlp("Kdor hoce prenesti preko racunalnika http://t.co/LwWyzs0cA0")     # run the pipeline
>>> print(doc.to_conll())                             # print the output in CoNLL-U format
# newpar id = 1
# sent_id = 1.1
# text = Kdor hoce prenesti preko racunalnika http://t.co/LwWyzs0cA0
1	Kdor	kdor	PRON	Pr-msn	Case=Nom|Gender=Masc|Number=Sing|PronType=Rel	2	nsubj	_	NER=O
2	hoce	hoteti	VERB	Vmpr3s-n	Aspect=Imp|Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin	0	root	_	NER=O
3	prenesti	prenesti	VERB	Vmen	Aspect=Perf|VerbForm=Inf	2	xcomp	_	NER=O
4	preko	preko	ADP	Sg	Case=Gen	5	case	_	NER=O
5	racunalnika	računalnik	NOUN	Ncmsg	Case=Gen|Gender=Masc|Number=Sing	3	obl	_	NER=O
6	http://t.co/LwWyzs0cA0	http://t.co/LwWyzs0cA0	SYM	Xw	_	5	nmod	_	NER=O
```

### Processing spoken texts

The pipeline also has a dedicated processing mode for spoken texts which uses models trained on spoken data transcripts to annotate the input text. This is currently only supported for the Slovenian models. It is activated by passing the ```type="spoken"``` argument to the ```Pipeline``` object.

```
>>> import classla
>>> classla.download('sl', type='spoken')        # download spoken models for Slovenian
>>> nlp = classla.Pipeline('sl', type='spoken')  # initialize the Slovenian spoken pipeline
>>> doc = nlp("to je igra, ki jo igrajo, eee, ti, eee, člani družine.")   # run the pipeline
>>> print(doc.to_conll())                        # print the output in CoNLL-U format
# newpar id = 1
# sent_id = 1.1
# text = to je igra, ki jo igrajo, eee, ti, eee, člani družine.
1       to      ta      DET     Pd-nsn  Case=Nom|Gender=Neut|Number=Sing|PronType=Dem   3       nsubj   _       NER=O
2       je      biti    AUX     Va-r3s-n        Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin      3       cop     _       NER=O
3       igra    igra    NOUN    Ncfsn   Case=Nom|Gender=Fem|Number=Sing 0       root    _       NER=O|SpaceAfter=No
4       ,       ,       PUNCT   Z       _       7       punct   _       NER=O
5       ki      ki      SCONJ   Cs      _       7       mark    _       NER=O
6       jo      on      PRON    Pp3fsa--y       Case=Acc|Gender=Fem|Number=Sing|Person=3|PronType=Prs|Variant=Short     7       obj     _       NER=O
7       igrajo  igrati  VERB    Vmpr3p  Aspect=Imp|Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin        3       acl     _       NER=O|SpaceAfter=No
8       ,       ,       PUNCT   Z       _       9       punct   _       NER=O
9       eee     eee     INTJ    I       _       7       discourse:filler        _       NER=O|SpaceAfter=No
10      ,       ,       PUNCT   Z       _       9       punct   _       NER=O
11      ti      ta      DET     Pd-mpn  Case=Nom|Gender=Masc|Number=Plur|PronType=Dem   15      det     _       NER=O|SpaceAfter=No
12      ,       ,       PUNCT   Z       _       13      punct   _       NER=O
13      eee     eee     INTJ    I       _       7       discourse:filler        _       NER=O|SpaceAfter=No
14      ,       ,       PUNCT   Z       _       13      punct   _       NER=O
15      člani   član    NOUN    Ncmpn   Case=Nom|Gender=Masc|Number=Plur        7       nsubj   _       NER=O
16      družine družina NOUN    Ncfsg   Case=Gen|Gender=Fem|Number=Sing 15      nmod    _       NER=O|SpaceAfter=No
17      .       .       PUNCT   Z       _       3       punct   _       NER=O
```

## Processors

The CLASSLA pipeline is built from multiple units. These units are called processors. By default CLASSLA runs the ```tokenize```, ```ner```, ```pos```, ```lemma``` and ```depparse``` processors.

You can specify which processors CLASSLA should run, via the ```processors``` attribute as in the following example, performing tokenization, named entity recognition, part-of-speech tagging and lemmatization.

```python
>>> nlp = classla.Pipeline('sl', processors='tokenize,ner,pos,lemma')
```

Another popular option might be to perform tokenization, part-of-speech tagging, lemmatization and dependency parsing.

```python
>>> nlp = classla.Pipeline('sl', processors='tokenize,pos,lemma,depparse')
```

### Tokenization and sentence splitting

The tokenization and sentence splitting processor ```tokenize``` is the first processor and is required for any further processing.

In case you already have tokenized text, you should separate tokens via spaces and pass the attribute ```tokenize_pretokenized=True```.

By default CLASSLA uses a rule-based tokenizer - [obeliks](https://github.com/clarinsi/obeliks) for Slovenian standard language pipeline. In other cases we use [reldi-tokeniser](https://github.com/clarinsi/reldi-tokeniser).

<!--Most important attributes:
```
tokenize_pretokenized   - [boolean]     ignores tokenizer
```-->

### Part-of-speech tagging

The POS tagging processor ```pos``` will general output that contains morphosyntactic description following the [MULTEXT-East standard](http://nl.ijs.si/ME/V6/msd/html/msd.lang-specific.html) and universal part-of-speech tags and universal features following the [Universal Dependencies standard](https://universaldependencies.org). This processing requires the usage of the ```tokenize``` processor.

<!--Most important attributes:
```
pos_model_path          - [str]         alternative path to model file
pos_pretrain_path       - [str]         alternative path to pretrain file
```-->

### Lemmatization

The lemmatization processor ```lemma``` will produce lemmas (basic forms) for each token in the input. It requires the usage of both the ```tokenize``` and ```pos``` processors.

### Dependency parsing

The dependency parsing processor ```depparse``` performs syntactic dependency parsing of sentences following the [Universal Dependencies formalism](https://universaldependencies.org/introduction.html#:~:text=Universal%20Dependencies%20(UD)%20is%20a,from%20a%20language%20typology%20perspective.). It requires the ```tokenize``` and ```pos``` processors.

### Named entity recognition

The named entity recognition processor ```ner``` identifies named entities in text following the [IOB2](https://en.wikipedia.org/wiki/Inside–outside–beginning_(tagging)) format. It requires only the ```tokenize``` processor.

## Croatian examples

### Example of standard Croatian

```
>>> import classla
>>> nlp = classla.Pipeline('hr') # run classla.download('hr') beforehand if necessary
>>> doc = nlp("Ante Starčević rođen je u Velikom Žitniku.")
>>> print(doc.to_conll())
# newpar id = 1
# sent_id = 1.1
# text = Ante Starčević rođen je u Velikom Žitniku.
1	Ante	Ante	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	3	nsubj	_	NER=B-PER
2	Starčević	Starčević	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	flat	_	NER=I-PER
3	rođen	roditi	ADJ	Appmsnn	Case=Nom|Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing|VerbForm=Part|Voice=Pass	0	root	_	NER=O
4	je	biti	AUX	Var3s	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	NER=O
5	u	u	ADP	Sl	Case=Loc	7	case	_	NER=O
6	Velikom	velik	ADJ	Agpmsly	Case=Loc|Definite=Def|Degree=Pos|Gender=Masc|Number=Sing	7	amod	_	NER=B-LOC
7	Žitniku	Žitnik	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	3	obl	_	NER=I-LOC|SpaceAfter=No
8	.	.	PUNCT	Z	_	3	punct	_	NER=O

```
### Example of non-standard Croatian

```
>>> import classla
>>> nlp = classla.Pipeline('hr', type='nonstandard') # run classla.download('hr', type='nonstandard') beforehand if necessary
>>> doc = nlp("kaj sam ja tulumaril jucer u ljubljani...")
>>> print(doc.to_conll())
# newpar id = 1
# sent_id = 1.1
# text = kaj sam ja tulumaril jucer u ljubljani...
1	kaj	što	PRON	Pq3n-a	Case=Acc|Gender=Neut|PronType=Int,Rel	4	obj	_	NER=O
2	sam	biti	AUX	Var1s	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin	4	aux	_	NER=O
3	ja	ja	PRON	Pp1-sn	Case=Nom|Number=Sing|Person=1|PronType=Prs	4	nsubj	_	NER=O
4	tulumaril	tulumariti	VERB	Vmp-sm	Gender=Masc|Number=Sing|Tense=Past|VerbForm=Part|Voice=Act	0	root	_	NER=O
5	jucer	jučer	ADV	Rgp	Degree=Pos	4	advmod	_	NER=O
6	u	u	ADP	Sl	Case=Loc	7	case	_	NER=O
7	ljubljani	Ljubljana	PROPN	Npfsl	Case=Loc|Gender=Fem|Number=Sing	4	obl	_	NER=B-LOC|SpaceAfter=No
8	...	...	PUNCT	Z	_	4	punct	_	NER=O

```

## Serbian examples

### Example of standard Serbian

```
>>> import classla
>>> nlp = classla.Pipeline('sr') # run classla.download('sr') beforehand if necessary
>>> doc = nlp("Slobodan Jovanović rođen je u Novom Sadu.")
>>> print(doc.to_conll())
# newpar id = 1
# sent_id = 1.1
# text = Slobodan Jovanović rođen je u Novom Sadu.
1	Slobodan	Slobodan	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	3	nsubj	_	NER=B-PER
2	Jovanović	Jovanović	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	flat	_	NER=I-PER
3	rođen	roditi	ADJ	Appmsnn	Case=Nom|Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing|VerbForm=Part|Voice=Pass	0	root	_	NER=O
4	je	biti	AUX	Var3s	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	NER=O
5	u	u	ADP	Sl	Case=Loc	7	case	_	NER=O
6	Novom	nov	ADJ	Agpmsly	Case=Loc|Definite=Def|Degree=Pos|Gender=Masc|Number=Sing	7	amod	_	NER=B-LOC
7	Sadu	Sad	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	3	obl	_	NER=I-LOC|SpaceAfter=No
8	.	.	PUNCT	Z	_	3	punct	_	NER=O

```

### Example of non-standard Serbian

```
>>> import classla
>>> nlp = classla.Pipeline('sr', type='nonstandard') # run classla.download('sr', type='nonstandard') beforehand if necessary
>>> doc = nlp("ne mogu da verujem kakvo je zezanje bilo prosle godine u zagrebu...")
>>> print(doc.to_conll())
# newpar id = 1
# sent_id = 1.1
# text = ne mogu da verujem kakvo je zezanje bilo prosle godine u zagrebu...
1	ne	ne	PART	Qz	Polarity=Neg	2	advmod	_	NER=O
2	mogu	moći	VERB	Vmr1s	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin	0	root	_	NER=O
3	da	da	SCONJ	Cs	_	4	mark	_	NER=O
4	verujem	verovati	VERB	Vmr1s	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin	2	xcomp	_	NER=O
5	kakvo	kakav	DET	Pi-nsn	Case=Nom|Gender=Neut|Number=Sing|PronType=Int,Rel	4	ccomp	_	NER=O
6	je	biti	AUX	Var3s	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	aux	_	NER=O
7	zezanje	zezanje	NOUN	Ncnsn	Case=Nom|Gender=Neut|Number=Sing	8	nsubj	_	NER=O
8	bilo	biti	AUX	Vap-sn	Gender=Neut|Number=Sing|Tense=Past|VerbForm=Part|Voice=Act	5	cop	_	NER=O
9	prosle	prošli	ADJ	Agpfsgy	Case=Gen|Definite=Def|Degree=Pos|Gender=Fem|Number=Sing	10	amod	_	NER=O
10	godine	godina	NOUN	Ncfsg	Case=Gen|Gender=Fem|Number=Sing	8	obl	_	NER=O
11	u	u	ADP	Sl	Case=Loc	12	case	_	NER=O
12	zagrebu	Zagreb	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	8	obl	_	NER=B-LOC|SpaceAfter=No
13	...	...	PUNCT	Z	_	2	punct	_	NER=O

```

## Bulgarian examples

### Example of standard Bulgarian

```
>>> import classla
>>> nlp = classla.Pipeline('bg') # run classla.download('bg') beforehand if necessary
>>> doc = nlp("Алеко Константинов е роден в Свищов.")
>>> print(doc.to_conll())
# newpar id = 1
# sent_id = 1.1
# text = Алеко Константинов е роден в Свищов.
1	Алеко	алеко	PROPN	Npmsi	Definite=Ind|Gender=Masc|Number=Sing	4	nsubj:pass	_	NER=B-PER
2	Константинов	константинов	PROPN	Hmsi	Definite=Ind|Gender=Masc|Number=Sing	1	flat	_	NER=I-PER
3	е	съм	AUX	Vxitf-r3s	Aspect=Imp|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	4	aux:pass	_	NER=O
4	роден	родя-(се)	VERB	Vpptcv--smi	Aspect=Perf|Definite=Ind|Gender=Masc|Number=Sing|VerbForm=Part|Voice=Pass	0	root	_	NER=O
5	в	в	ADP	R	_	6	case	_	NER=O
6	Свищов	свищов	PROPN	Npmsi	Definite=Ind|Gender=Masc|Number=Sing	4	iobj	_	NER=B-LOC|SpaceAfter=No
7	.	.	PUNCT	punct	_	4	punct	_	NER=O

```

## Macedonian examples

### Example of standard Macedonian

```
>>> import classla
>>> nlp = classla.Pipeline('mk') # run classla.download('mk') beforehand if necessary
>>> doc = nlp('Крсте Петков Мисирков е роден во Постол.')
>>> print(doc.to_conll())
# newpar id = 1
# sent_id = 1.1
# text = Крсте Петков Мисирков е роден во Постол.
1	Крсте	Крсте	PROPN	Npmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	_
2	Петков	Петков	PROPN	Npmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	_
3	Мисирков	Мисирков	PROPN	Npmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	_
4	е	сум	AUX	Vapip3s-n	Aspect=Prog|Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres	_	_	_	_
5	роден	роден	ADJ	Ap-ms-n	Definite=Ind|Gender=Masc|Number=Sing|VerbForm=Part	_	_	_	_
6	во	во	ADP	Sps	AdpType=Prep	_	_	_	_
7	Постол	Постол	PROPN	Npmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	SpaceAfter=No
8	.	.	PUNCT	Z	_	_	_	_	_

```

## Training instructions

[Training instructions](https://github.com/clarinsi/classla-stanfordnlp/blob/master/README.train.md)

## Superuser instructions

[Superuser instructions](https://github.com/clarinsi/classla-stanfordnlp/blob/master/README.superuser.md)
