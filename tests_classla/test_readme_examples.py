"""
Basic testing of the English pipeline
"""

import pytest
import classla
from classla.utils.conll import CoNLL

from tests_classla import *


# data for testing
SL_STANDARD = "France Prešeren je rojen v Vrbi."

SL_STANDARD_CONLL = """
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

""".strip()

SL_NONSTANDARD = "kva smo mi zurali zadnje leto v zagrebu..."

SL_NONSTANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = kva smo mi zurali zadnje leto v zagrebu...
1	kva	kaj	PRON	Pq-nsa	Case=Acc|Gender=Neut|Number=Sing|PronType=Int	4	obj	_	NER=O
2	smo	biti	AUX	Va-r1p-n	Mood=Ind|Number=Plur|Person=1|Polarity=Pos|Tense=Pres|VerbForm=Fin	4	aux	_	NER=O
3	mi	jaz	PRON	Pp1-sd--y	Case=Dat|Number=Plur|Person=1|PronType=Prs|Variant=Short	4	iobj	_	NER=O
4	zurali	zurati	VERB	Vmep-pm	Aspect=Perf|Gender=Masc|Number=Plur|VerbForm=Part	0	root	_	NER=O
5	zadnje	zadnji	ADJ	Agpnsa	Case=Acc|Degree=Pos|Gender=Neut|Number=Sing	6	amod	_	NER=O
6	leto	leto	NOUN	Ncnsa	Case=Acc|Gender=Neut|Number=Sing	4	obl	_	NER=O
7	v	v	ADP	Sl	Case=Loc	8	case	_	NER=O
8	zagrebu	Zagreb	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	4	obl	_	NER=B-LOC|SpaceAfter=No
9	...	.	PUNCT	Z	_	4	punct	_	NER=O

""".strip()

HR_STANDARD = "Ante Starčević rođen je u Velikom Žitniku."

HR_STANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = Ante Starčević rođen je u Velikom Žitniku.
1	Ante	Ante	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	3	nsubj:pass	_	NER=B-PER
2	Starčević	Starčević	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	flat	_	NER=I-PER
3	rođen	roditi	ADJ	Appmsnn	Case=Nom|Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing|VerbForm=Part|Voice=Pass	0	root	_	NER=O
4	je	biti	AUX	Var3s	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux:pass	_	NER=O
5	u	u	ADP	Sl	Case=Loc	7	case	_	NER=O
6	Velikom	velik	ADJ	Agpmsly	Case=Loc|Definite=Def|Degree=Pos|Gender=Masc|Number=Sing	7	amod	_	NER=B-LOC
7	Žitniku	Žitnik	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	3	obl	_	NER=I-LOC|SpaceAfter=No
8	.	.	PUNCT	Z	_	3	punct	_	NER=O

""".strip()

HR_NONSTANDARD = "kaj sam ja tulumaril jucer u ljubljani..."

HR_NONSTANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = kaj sam ja tulumaril jucer u ljubljani...
1	kaj	što	PRON	Pi3n-a	Case=Acc|Gender=Neut|PronType=Int,Rel	4	obj	_	NER=O
2	sam	biti	AUX	Var1s	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin	4	aux	_	NER=O
3	ja	ja	PRON	Pp1-sn	Case=Nom|Number=Sing|Person=1|PronType=Prs	4	nsubj	_	NER=O
4	tulumaril	tulumariti	VERB	Vmp-sm	Gender=Masc|Number=Sing|Tense=Past|VerbForm=Part|Voice=Act	0	root	_	NER=O
5	jucer	jučer	ADV	Rgp	Degree=Pos	4	advmod	_	NER=O
6	u	u	ADP	Sl	Case=Loc	7	case	_	NER=O
7	ljubljani	Ljubljana	PROPN	Npfsl	Case=Loc|Gender=Fem|Number=Sing	4	obl	_	NER=B-LOC|SpaceAfter=No
8	...	.	PUNCT	Z	_	4	punct	_	NER=O

""".strip()

SR_STANDARD = "Slobodan Jovanović rođen je u Novom Sadu."

SR_STANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = Slobodan Jovanović rođen je u Novom Sadu.
1	Slobodan	Slobodan	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	3	nsubj	_	NER=B-PER
2	Jovanović	Jovanović	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	flat	_	NER=I-PER
3	rođen	roditi	ADJ	Appmsnn	Case=Nom|Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing|VerbForm=Part|Voice=Pass	0	root	_	NER=O
4	je	biti	AUX	Var3s	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	NER=O
5	u	u	ADP	Sl	Case=Loc	6	case	_	NER=O
6	Novom	nov	ADJ	Agpmsly	Case=Loc|Definite=Def|Degree=Pos|Gender=Masc|Number=Sing	3	obl	_	NER=B-LOC
7	Sadu	Sad	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	6	flat	_	NER=I-LOC|SpaceAfter=No
8	.	.	PUNCT	Z	_	3	punct	_	NER=O

""".strip()

SR_NONSTANDARD = "ne mogu da verujem kakvo je zezanje bilo prosle godine u zagrebu..."

SR_NONSTANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = ne mogu da verujem kakvo je zezanje bilo prosle godine u zagrebu...
1	ne	ne	PART	Qz	Polarity=Neg	2	advmod	_	NER=O
2	mogu	moći	VERB	Vmr1s	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin	0	root	_	NER=O
3	da	da	SCONJ	Cs	_	4	mark	_	NER=O
4	verujem	verovati	VERB	Vmr1s	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin	2	xcomp	_	NER=O
5	kakvo	kakav	DET	Pi-nsn	Case=Nom|Gender=Neut|Number=Sing|PronType=Int,Rel	4	ccomp	_	NER=O
6	je	biti	AUX	Var3s	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	aux	_	NER=O
7	zezanje	zezanje	NOUN	Ncnsn	Case=Nom|Gender=Neut|Number=Sing	5	nsubj	_	NER=O
8	bilo	biti	AUX	Vap-sn	Gender=Neut|Number=Sing|Tense=Past|VerbForm=Part|Voice=Act	5	cop	_	NER=O
9	prosle	prošli	ADJ	Agpfsgy	Case=Gen|Definite=Def|Degree=Pos|Gender=Fem|Number=Sing	10	amod	_	NER=O
10	godine	godina	NOUN	Ncfsg	Case=Gen|Gender=Fem|Number=Sing	8	obl	_	NER=O
11	u	u	ADP	Sl	Case=Loc	12	case	_	NER=O
12	zagrebu	Zagreb	PROPN	Npmsl	Case=Loc|Gender=Masc|Number=Sing	8	obl	_	NER=B-LOC|SpaceAfter=No
13	...	.	PUNCT	Z	_	2	punct	_	NER=O

""".strip()

BG_STANDARD = "Алеко Константинов е роден в Свищов."

BG_STANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = Алеко Константинов е роден в Свищов.
1	Алеко	алеко	PROPN	Npmsi	Definite=Ind|Gender=Masc|Number=Sing	4	nsubj:pass	_	NER=B-PER
2	Константинов	константинов	PROPN	Hmsi	Definite=Ind|Gender=Masc|Number=Sing	1	flat	_	NER=I-PER
3	е	съм	AUX	Vxitf-r3s	Aspect=Imp|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	4	aux:pass	_	NER=O
4	роден	родя-(се)	VERB	Vpptcv--smi	Aspect=Perf|Definite=Ind|Gender=Masc|Number=Sing|VerbForm=Part|Voice=Pass	0	root	_	NER=O
5	в	в	ADP	R	_	6	case	_	NER=O
6	Свищов	свищов	PROPN	Npmsi	Definite=Ind|Gender=Masc|Number=Sing	4	iobj	_	NER=B-LOC|SpaceAfter=No
7	.	.	PUNCT	Z	_	4	punct	_	NER=O

""".strip()

MK_STANDARD = 'Крсте Петков Мисирков е роден во Постол.'

MK_STANDARD_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = Крсте Петков Мисирков е роден во Постол.
1	Крсте	крсте	ADJ	Afpms-n	Definite=Ind|Gender=Masc|Number=Sing	_	_	_	_
2	Петков	петков	NOUN	Ncmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	_
3	Мисирков	мисирков	NOUN	Ncmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	_
4	е	сум	AUX	Vapip3s-n	Aspect=Prog|Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres	_	_	_	_
5	роден	роден	ADJ	Ap-ms-n	Definite=Ind|Gender=Masc|Number=Sing|VerbForm=Part	_	_	_	_
6	во	во	ADP	Sps	AdpType=Prep	_	_	_	_
7	Постол	постол	NOUN	Ncmsnn	Case=Nom|Definite=Ind|Gender=Masc|Number=Sing	_	_	_	SpaceAfter=No
8	.	.	PUNCT	Z	_	_	_	_	_

""".strip()

SL_STANDARD_JOS = "France Prešeren je rojen v Vrbi."

SL_STANDARD_JOS_CONLL = """
# newpar id = 1
# sent_id = 1.1
# text = France Prešeren je rojen v Vrbi.
1	France	France	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	3	Sb	_	NER=B-PER
2	Prešeren	Prešeren	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	Atr	_	NER=I-PER
3	je	biti	AUX	Va-r3s-n	Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin	0	Root	_	NER=O
4	rojen	rojen	ADJ	Appmsnn	Case=Nom|Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing|VerbForm=Part	3	Atr	_	NER=O
5	v	v	ADP	Sl	Case=Loc	6	Atr	_	NER=O
6	Vrbi	Vrba	PROPN	Npfsl	Case=Loc|Gender=Fem|Number=Sing	3	AdvO	_	NER=B-LOC|SpaceAfter=No
7	.	.	PUNCT	Z	_	0	Root	_	NER=O

""".strip()


def test_sl_standard():
    classla.download('sl', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sl', dir=TEST_MODELS_DIR)
    doc = nlp(SL_STANDARD)
    assert doc.to_conll().strip() == SL_STANDARD_CONLL


def test_sl_nonstandard():
    classla.download('sl', type='nonstandard', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sl', type='nonstandard', dir=TEST_MODELS_DIR)
    doc = nlp(SL_NONSTANDARD)
    assert doc.to_conll().strip() == SL_NONSTANDARD_CONLL


def test_hr_standard():
    classla.download('hr', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('hr', dir=TEST_MODELS_DIR)
    doc = nlp(HR_STANDARD)
    assert doc.to_conll().strip() == HR_STANDARD_CONLL


def test_hr_nonstandard():
    classla.download('hr', type='nonstandard', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('hr', type='nonstandard', dir=TEST_MODELS_DIR)
    doc = nlp(HR_NONSTANDARD)
    assert doc.to_conll().strip() == HR_NONSTANDARD_CONLL


def test_sr_standard():
    classla.download('sr', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sr', dir=TEST_MODELS_DIR)
    doc = nlp(SR_STANDARD)
    assert doc.to_conll().strip() == SR_STANDARD_CONLL


def test_sr_nonstandard():
    classla.download('sr', type='nonstandard', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sr', type='nonstandard', dir=TEST_MODELS_DIR)
    doc = nlp(SR_NONSTANDARD)
    assert doc.to_conll().strip() == SR_NONSTANDARD_CONLL


def test_bg_standard():
    classla.download('bg', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('bg', dir=TEST_MODELS_DIR)
    doc = nlp(BG_STANDARD)
    assert doc.to_conll().strip() == BG_STANDARD_CONLL


def test_mk_standard():
    classla.download('mk', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('mk', dir=TEST_MODELS_DIR)
    doc = nlp(MK_STANDARD)
    assert doc.to_conll().strip() == MK_STANDARD_CONLL


def test_sl_standard_jos():
    classla.download('sl', type='standard_jos', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sl', type='standard_jos', dir=TEST_MODELS_DIR)
    doc = nlp(SL_STANDARD_JOS)
    assert doc.to_conll().strip() == SL_STANDARD_JOS_CONLL


def test_sl_inflectional():
    classla.download('sl', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sl', pos_use_lexicon=True, dir=TEST_MODELS_DIR)
    doc = nlp(SL_STANDARD)
    assert doc.to_conll().strip() == SL_STANDARD_CONLL


def test_sl_pretokenized_conllu():
    classla.download('sl', dir=TEST_MODELS_DIR)
    nlp = classla.Pipeline('sl', tokenize_pretokenized='conllu', dir=TEST_MODELS_DIR)
    conllu_pretokenized = """
# newpar id = 1
# sent_id = 1.1
# text = France Prešeren je rojen v Vrbi.
1	France	France	_	_	_	_	_	_	_
2	Prešeren	Prešeren	_	_	_	_	_	_	_
3	je	biti	_	_	_	_	_	_	_
4	rojen	rojen	_	_	_	_	_	_	_
5	v	v	_	_	_	_	_	_	_
6	Vrbi	Vrba	_	_	_	_	_	_	SpaceAfter=No
7	.	.	_	_	_	_	_	_	_

"""
    doc = nlp(conllu_pretokenized)
    assert doc.to_conll().strip() == SL_STANDARD_CONLL
