Speech and Language Processing. Daniel Jurafsky & James H. Martin. Copyright © 2021. All rights reserved. Draft of September 21, 2021.

CHAPTER ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.001.png)

C Statisticaling Constituency Pars-

The characters in Damon Runyon’s short stories are willing to bet “on any propo- sition whatever”, as Runyon says about Sky Masterson in The Idyll of Miss Sarah Brown, from getting aces back-to-back to a man being able to throw a peanut from second base to home plate. There is a moral here for language processing: with enough knowledge we can estimate the probability of just about anything. The last twochaptershaveintroducedmodelsofsyntacticconstituencystructureanditspars- ing. Here, we show that it is possible to build probabilistic models of syntactic knowledge and efficientprobabilistic parsers.

One use of probabilistic parsing is to solve the problem of disambiguation. Re- call from Chapter 13 that sentences on average tend to be syntactically ambiguous because of phenomena like coordination ambiguity and attachment ambiguity. The CKY parsing algorithm can represent these ambiguities in an efficient way but is not equipped to resolve them. There we introduced a neural algorithm for disam- biguation. Here we introduce probabilistic parsers, which offer an alternative solu- tion to the problem: compute the probability of each interpretation and choose the most probable interpretation. The most commonly used probabilistic constituency grammar formalism is the probabilistic context-free grammar (PCFG), a prob- abilistic augmentation of context-free grammars in which each rule is associated with a probability. We introduce PCFGs in the next section, showing how they can be trained on Treebank grammars and how they can be parsed with a probabilistic version of the CKY algorithm of Chapter 13.

We then show a number of ways that we can improve on this basic probabil- ity model (PCFGs trained on Treebank grammars), such as by modifying the set of non-terminals (making them either more specific or more general), or adding more sophisticated conditioning factors like subcategorization or dependencies. Heav- ily lexicalized grammar formalisms such as Lexical-Functional Grammar (LFG) [(Bresnan, 1982](#_page19_x72.42_y328.34)), Head-Driven Phrase Structure Grammar (HPSG) [(Pollard and Sag, 1994](#_page19_x278.29_y471.49)), Tree-Adjoining Grammar (TAG) [(Joshi, 1985](#_page19_x278.29_y130.94)), and Combinatory Categorial Grammar (CCG) pose additional problems for probabilistic parsers. Section ?? in- troduces the task of supertagging and the use of heuristic search methods based on the A\* algorithm in the context of CCG parsing.

C.1 Probabilistic Context-Free Grammars

Thesimplestaugmentationofthecontext-freegrammaristheProbabilisticContext- PCFG Free Grammar (PCFG), also known as the Stochastic Context-Free Grammar SCFG (SCFG), first proposed by [Booth ](#_page19_x72.42_y265.86)([1969).](#_page19_x72.42_y265.86) Recall that a context-free grammar G is

definedby four parameters (N; S; R; S); a probabilistic context-free grammar is also

definedby four parameters, with a slight augmentation to each of the rules in R:

2  APPENDIX C • STATISTICAL CONSTITUENCY PARSING

N a set of non-terminal symbols (or variables)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.002.png)

S a set of terminal symbols (disjoint from N)

R a set of rules or productions, each of the form A! b [p],

where Ais a non-terminal,

b is a string of symbols from the infiniteset of strings (S[ N), and p is a number between 0 and 1 expressing P(bjA)

S a designated start symbol

That is, a PCFG differs from a standard CFG by augmenting each rule in Rwith a conditional probability:

A! b [p] (C.1)

Here p expresses the probability that the given non-terminal Awill be expanded to the sequence b. That is, p is the conditional probability of a given expansion b given the left-hand-side (LHS) non-terminal A. We can represent this probability as

P(A! b) or as

P(A! bjA) or as

P(RHSjLHS)

Thus, if we consider all the possible expansions of a non-terminal, the sum of their probabilities must be 1: X

P(A! b) = 1

b

Figure[ C.1 ](#_page2_x493.70_y207.89)shows a PCFG: a probabilistic augmentation of the L 1 miniature En- glish CFG grammar and lexicon. Note that the probabilities of all of the expansions of each non-terminal sum to 1. Also note that these probabilities were made up for pedagogical purposes. A real grammar has a great many more rules for each non-terminal; hence, the probabilities of any particular rule would tend to be much smaller.

consistent A PCFG is said to be consistent if the sum of the probabilities of all sentences

in the language equals 1. Certain kinds of recursive rules cause a grammar to be inconsistent by causing infinitely looping derivations for some sentences. For ex- ample, a rule S ! S with probability 1 would lead to lost probability mass due to derivations that never terminate. See[ Booth and Thompson (1973)](#_page19_x72.42_y297.10) for more details on consistent and inconsistent grammars.

How are PCFGs used? A PCFG can be used to estimate a number of useful probabilities concerning a sentence and its parse tree(s), including the probability of a particular parse tree (useful in disambiguation) and the probability of a sentence or a piece of a sentence (useful in language modeling). Let’s see how this works.

C.1.1 PCFGs for Disambiguation

A PCFG assigns a probability to each parse tree T (i.e., each derivation) of a sen- tence S. This attribute is useful in disambiguation. For example, consider the two parsesofthesentence“Bookthedinnerflight”showninFig.[C.2.](#_page3_x142.20_y434.01) Thesensibleparse

C.1 • PROBABILISTIC CONTEXT-FREE GRAMMARS 5

Grammar Lexicon![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.003.png)

S ! NP VP [:80] Det ! that [:10] j a [:30] j the [:60] S ! Aux NP VP [:15] Noun ! book[:10] j trip [:30]

S ! VP [:05] j meal [:05] j money[:05] NP ! Pronoun [:35] j flight[:40] j dinner [:10] NP ! Proper-Noun [:30] Verb ! book[:30] j include [:30] NP ! Det Nominal [:20] j prefer [:40]

NP ! Nominal [:15] Pronoun ! I [:40] j she [:05] Nominal ! Noun [:75] j me[:15] j you[:40]<a name="_page2_x493.70_y207.89"></a>Nominal ! Nominal Noun [:20] Proper-Noun ! Houston [:60] Nominal ! Nominal PP [:05] j NWA[:40]

VP ! Verb [:35] Aux ! does [:60] j can [:40]

VP ! Verb NP [:20] Preposition ! from[:30] j to [:30] VP ! Verb NP PP [:10] j on [:20] j near [:15]

VP ! Verb PP [:15] j through [:05]

VP ! Verb NP NP [:05]

VP ! VP PP [:15]

PP ! Preposition NP [1:0]

Figure C.1 A PCFG that is a probabilistic augmentation of the L 1 miniature English CFG grammar and lexicon of Fig. ??. These probabilities were made up for pedagogical purposes and are not based on a corpus (any real corpus would have many more rules, so the true probabilities of each rule would be much smaller).

on the left means “Book a flight that serves dinner”. The nonsensical parse on the right, however, would have to mean something like “Book a flighton behalf of ‘the dinner”’ just as a structurally similar sentence like “Can you book John a flight?” means something like “Can you book a flighton behalf of John?”

The probability of a particular parse T is definedas the product of the probabil- ities of all the n rules used to expand each of the n non-terminal nodes in the parse tree T, where each rule i can be expressed as LHSi ! RHSi:

Yn

P(T;S) = P(RHSijLHSi) (C.2)

i=1

The resulting probability P(T;S) is both the joint probability of the parse and the sentence and also the probability of the parse P(T). How can this be true? First, by the definitionof joint probability:

P(T;S) = P(T)P(SjT) (C.3) But since a parse tree includes all the words of the sentence, P(SjT) is 1. Thus,

P(T;S) = P(T)P(SjT) = P(T) (C.4)

WecancomputetheprobabilityofeachofthetreesinFig.[C.2](#_page3_x142.20_y434.01)bymultiplyingthe probabilities of each of the rules used in the derivation. For example, the probability of the left tree in Fig.[ C.2a](#_page3_x142.20_y434.01) (call it Tleft) and the right tree (Fig.[ C.2](#_page3_x142.20_y434.01)b or Tright) can be computed as follows:

P(Tleft) = :05:20:20:20:75:30:60:10:40 = 2:210 6 P(Tright) = :05:10:20:15:75:75:30:60:10:40 = 6:110 7

|S|S||||||||
| - | - | :- | :- | :- | :- | :- | :- | :- |
||||||||||
|Verb NP|Verb NP NP||||||||
||Book Det Nominal||Book Det Nominal Nominal||||||
||the Nominal Noun||||||||
||||||||||
||||||||||
||||||||||
|S ! VP .05|S ! VP .05||||||||
|VP ! Verb NP .20|VP ! Verb NP NP .10||||||||
|NP ! Det Nominal .20|NP ! Det Nominal .20||||||||
|Nominal ! Nominal Noun .20|NP ! Nominal .15||||||||
|Nominal ! Noun .75|Nominal ! Noun .75||||||||
||Nominal ! Noun .75||||||||
|Verb ! book .30|Verb ! book .30||||||||
|Det ! the .60|Det ! the .60||||||||
|Noun ! dinner .10|Noun ! dinner .10||||||||
|<a name="_page3_x142.20_y434.01"></a>Noun ! flight .40|Noun ! flight .40||||||||

Figure C.2 Two parse trees for an ambiguous sentence. The parse on the left corresponds to the sensible meaning “Book a flightthat serves dinner”, while the parse on the right corre- sponds to the nonsensical meaning “Book a flighton behalf of ‘the dinner’ ”.

We can see that the left tree in Fig.[ C.2 ](#_page3_x142.20_y434.01)has a much higher probability than the tree on the right. Thus, this parse would correctly be chosen by a disambiguation algorithm that selects the parse with the highest PCFG probability.

Let’s formalize this intuition that picking the parse with the highest probability is the correct way to do disambiguation. Consider all the possible parse trees for a

yield given sentence S. The string of words S is called the yield of any parse tree over S. Thus, out of all parse trees with a yield of S, the disambiguation algorithm picks the

parse tree that is most probable given S:

Tˆ(S) = argmax P(TjS) (C.5)

Ts:t:S=yield(T)

By definition,the probability P(TjS) can be rewritten as P(T;S)=P(S), thus leading to

P(T;S)

Tˆ(S) = Ts:tar:S=gmaxyield(T) P(S) (C.6) Since![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.004.png) we are maximizing over all parse trees for the same sentence, P(S) will be a

C.1 • PROBABILISTIC CONTEXT-FREE GRAMMARS 6

constant for each tree, so we can eliminate it:

Tˆ(S) = argmax P(T;S) (C.7)

Ts:t:S=yield(T)

Furthermore, since we showed above that P(T;S) = P(T), the final equation for choosing the most likely parse neatly simplifiesto choosing the parse with the high- est probability:

Tˆ(S) = argmax P(T) (C.8)

Ts:t:S=yield(T)

C.1.2 PCFGs for Language Modeling

A second attribute of a PCFG is that it assigns a probability to the string of words constituting a sentence. This is important in language modeling, whether for use in speech recognition, machine translation, spelling correction, augmentative com- munication, or other applications. The probability of an unambiguous sentence is P(T;S) = P(T) or just the probability of the single parse tree for that sentence. The probability of an ambiguous sentence is the sum of the probabilities of all the parse trees for the sentence:

X

P(S) = P(T;S) (C.9)

Ts:t:S=yield(T)

X

= P(T) (C.10)

Ts:t:S=yield(T)

An additional feature of PCFGs that is useful for language modeling is their ability to assign a probability to substrings of a sentence. For example, suppose we want to know the probability of the next word wi in a sentence<a name="_page4_x380.17_y434.60"></a> given all the words we’ve seen so far w1;:::;wi 1. The general formula for this is

P(wjw ;w ;:::;w ) = P(w1;w2;:::;wi 1;wi) (C.11)

i 1 2 i 1 P(w1;w2;:::;wi 1)

We saw in Chapter 3 a simple approximation of this probability using N-grams, conditioning on only the last word or two instead of the entire context; thus, the bigram approximation would give us

P(wjw ;w ;:::;w )  P(wi 1;wi) (C.12)

i 1 2 i 1 P(wi 1)

But the fact that the N-gram model can only make use of a couple words of context means it is ignoring potentially useful prediction cues. Consider predicting the word after in the following sentence from[ Chelba and Jelinek (2000](#_page19_x72.42_y443.84)):

(C.13) the contract ended with a loss of 7 cents after trading as low as 9 cents

A trigram grammar must predict after from the words 7 cents, while it seems clear that the verb ended and the subject contract would be useful predictors that a PCFG- based parser could help us make use of. Indeed, it turns out that PCFGs allow us to condition on the entire previous context w1;w2;:::;wi 1 shown in Eq.[ C.11.](#_page4_x380.17_y434.60)

In summary, this section and the previous one have shown that PCFGs can be applied both to disambiguation in syntactic parsing and to word prediction in lan- guage modeling. Both of these applications require that we be able to compute the probability of parse tree T for a given sentence S. The next few sections introduce some algorithms for computing this probability.

6  APPENDIX C • STATISTICAL CONSTITUENCY PARSING

C.2 Probabilistic CKY Parsing of PCFGs

The parsing problem for PCFGs is to produce the most-likely parse Tˆ for a given sentence S, that is,

Tˆ(S) = argmax P(T) (C.14)

Ts:t:S=yield(T)

The algorithms for computing the most likely parse are simple extensions of the

standard algorithms for parsing; most modern probabilistic parsers are based on the probabilisticCKY probabilistic CKY algorithm, firstdescribed by[ Ney (1991](#_page19_x278.29_y410.00)). The probabilistic CKY

algorithm assumes the PCFG is in Chomsky normal form. Recall from page ?? that

in CNF, the right-hand side of each rule must expand to either two non-terminals or

to a single terminal, i.e., rules have the form A ! B C, or A ! w.

For the CKY algorithm, we represented each sentence as having indices between the words. Thus, an example sentence like

(C.15) Book the flightthrough Houston.

would assume the following indices between each word: (C.16) 0 Book 1 the 2 flight 3 through 4 Houston 5

Using these indices, each constituent in the CKY parse tree is encoded in a two-dimensional matrix. Specifically, for a sentence of length n and a grammar that contains V non-terminals, we use the upper-triangular portion of an (n+ 1)  (n+ 1) matrix. For CKY, each cell table[i; j] contained a list of constituents that could span the sequence of words from i to j. For probabilistic CKY, it’s slightly simpler to think of the constituents in each cell as constituting a third dimension of maximum lengthV. This third dimension corresponds to each non-terminal that can be placed in this cell, and the value of the cell is then a probability for that non- terminal/constituent rather than a list of constituents. In summary, each cell [i; j;A] in this (n+ 1)(n+ 1)V matrix is the probability of a constituent of type Athat spans positions i through j of the input.

Figure[ C.3 ](#_page5_x475.20_y583.70)gives the probabilistic CKY algorithm.



|<p>function PROBABILISTIC-CKY(words,grammar) returns most probable parse</p><p>and its probability</p><p>for j from 1 to LENGTH(words) do</p><p>for all f Aj A ! words[j] 2 grammarg</p><p>table[j 1; j;A] P(A! words[j])</p><p>for i from j 2 downto 0 do</p><p>for k i+ 1 to j 1 do</p><p><a name="_page5_x475.20_y583.70"></a>for all f Aj A ! BC 2 grammar;</p><p>and table[i;k;B] > 0 and table[k; j;C] > 0 g</p><p>if (table[i,j,A] < P(A ! BC)  table[i,k,B]  table[k,j,C]) then</p><p>table[i,j,A] P(A ! BC)  table[i,k,B]  table[k,j,C] back[i,j,A] fk;B;Cg</p><p>return BUILD~~ TREE(back[1, LENGTH(words), S]), table[1, LENGTH(words), S]</p>|
| - |

Figure C.3 The probabilistic CKY algorithm for finding the maximum probability parse of a string of num~~ words words given a PCFG grammar with num~~ rules rules in Chomsky normal form. back is an array of backpointers used to recover the best parse. The build~~ tree function is left as an exercise to the reader.

C.2 • PROBABILISTIC CKY PARSING OF PCFGS 8

Like the basic CKY algorithm in Fig. ??, the probabilistic CKY algorithm re- quires a grammar in Chomsky normal form. Converting a probabilistic grammar to CNF requires that we also modify the probabilities so that the probability of each parse remains the same underthenewCNFgrammar. ExerciseC.[2](#_page17_x142.20_y724.32)asksyoutomod- ify the algorithm for conversion to CNF in Chapter 13 so that it correctly handles rule probabilities.

In practice, a generalized CKY algorithm that handles unit productions directly is typically used. Recall that Exercise 13.3 asked you to make this change in CKY; Exercise C.[3 ](#_page18_x160.20_y149.67)asks you to extend this change to probabilistic CKY.

Let’s see an example of the probabilistic CKY chart, using the following mini- grammar, which is already in CNF:



|S|! NP VP|.80||Det|! the|.40|
| - | - | - | :- | - | - | - |
|NP|! Det N|.30||Det|! a|.40|
|VP|! V NP|.20||N|! meal|.01|
|V|! includes|.05||N|! flight|.02|

Given this grammar, Fig.[ C.4 ](#_page6_x493.20_y642.53)shows the firststeps in the probabilistic CKY parse of the sentence “The flightincludes a meal”.



|<p>*The flight includes a meal ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.005.png)*Det: .40 NP: .30 \*.40 \*.02 ![ref1]![ref1]![ref2]![ref2]![ref2]</p><p>= .0024 </p><p>[0,1] [0,2] [0,3] [0,4] [0,5]</p><p>N: .02 ![ref2]![ref2]![ref2]</p><p>[1,2] [1,3] [1,4] [1,5]</p><p>V: .05 ![ref3]![ref3]</p><p>[2,3] [2,4] [2,5]</p><p>Det: .40 ![ref3]![ref3]</p><p>[3,4] [3,5]</p><p>N: .01![ref2]</p><p>[4,5]</p>|
| :- |

Figure C.4 The beginning of the probabilistic CKY matrix. Filling out the rest of the chart<a name="_page6_x493.20_y642.53"></a>is left as Exercise C.[4 ](#_page18_x160.20_y190.02)for the reader.

8  APPENDIX C • STATISTICAL CONSTITUENCY PARSING

C.3 Ways to Learn PCFG Rule Probabilities

Where do PCFG rule probabilities come from? There are two ways to learn prob- abilities for the rules of a grammar. The simplest way is to use a treebank, a cor- pus of already parsed sentences. Recall that we introduced in Chapter 12 the idea of treebanks and the commonly used Penn Treebank, a collection of parse trees in English, Chinese, and other languages that is distributed by the Linguistic Data Consortium. Given a treebank, we can compute the probability of each expansion of a non-terminal by counting the number of times that expansion occurs and then normalizing.

<a name="_page7_x142.20_y240.68"></a>Count(a ! b) Count(a ! b)

P(a ! bja ) = ~~P~~ = (C.17)

g Count(a ! g) Count(a )

If we don’t have a treebank but we do have a (non-probabilistic) parser, we can generate the counts we need for computing PCFG rule probabilities by firstparsing a corpus of sentences with the parser. If sentences were unambiguous, it would be as simple as this: parse the corpus, increment a counter for every rule in the parse, and then normalize to get probabilities.

But wait! Since most sentences are ambiguous, that is, have multiple parses, we don’t know which parse to count the rules in. Instead, we need to keep a separate count for each parse of a sentence and weight each of these partial counts by the probability of the parse it appears in. But to get these parse probabilities to weight the rules, we need to already have a probabilistic parser.

The intuition for solving this chicken-and-egg problem is to incrementally im- prove our estimates by beginning with a parser with equal rule probabilities, then

parse the sentence, compute a probability for each parse, use these probabilities to weight the counts, re-estimate the rule probabilities, and so on, until our proba-

bilities converge. The standard algorithm for computing this solution is called the inside-outside inside-outside algorithm; it was proposed by[ Baker (1979)](#_page19_x72.42_y131.43) as a generalization of the forward-backward algorithm for HMMs. Like forward-backward, inside-outside is

a special case of the Expectation Maximization (EM) algorithm, and hence has two

steps: the expectation step, and the maximization step. See [Lari and Young (1990) ](#_page19_x278.29_y305.95)or[ Manning and Schutze¨ (1999)](#_page19_x278.29_y357.97) for more on the algorithm.

C.4 Problems with PCFGs

While probabilistic context-free grammars are a natural extension to context-free grammars, they have two main problems as probability estimators:

Poorindependenceassumptions: CFGrulesimposeanindependenceassumption

on probabilities that leads to poor modeling of structural dependencies across the parse tree.

Lackoflexicalconditioning: CFGrulesdon’tmodelsyntacticfactsaboutspecific

words, leading to problems with subcategorization ambiguities, preposition attachment, and coordinate structure ambiguities.

Because of these problems, probabilistic constituent parsing models use some augmented version of PCFGs, or modify the Treebank-based grammar in some way.


C.4 • PROBLEMS WITH PCFGS 9

In the next few sections after discussing the problems in more detail we introduce some of these augmentations.

C.4.1 Independence Assumptions Miss Rule Dependencies

Let’s look at these problems in more detail. Recall that in a CFG the expansion of a non-terminal is independent of the context, that is, of the other nearby non- terminals in the parse tree. Similarly, in a PCFG, the probability of a particular rule like NP ! DetN is also independent of the rest of the tree. By definition, the probability of a group of independent events is the product of their probabilities. These two facts explain why in a PCFG we compute the probability of a tree by just multiplying the probabilities of each non-terminal expansion.

Unfortunately, this CFG independence assumption results in poor probability estimates. This is because in English the choice of how a node expands can after all depend on the location of the node in the parse tree. For example, in English it turns out that NPs that are syntactic subjects are far more likely to be pronouns, and NPs that are syntactic objects are far more likely to be non-pronominal (e.g., a proper noun or a determiner noun sequence), as shown by these statistics for NPs in the Switchboard corpus [(Francis et al., 1999](#_page19_x72.42_y518.64)):[1](#_page8_x169.77_y678.80)

Pronoun Non-Pronoun Subject![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.009.png) 91% 9%

Object 34% 66%

Unfortunately, there is no way to represent this contextual difference in the prob- abilities of a PCFG. Consider two expansions of the non-terminal NP as a pronoun or as a determiner+noun. How shall we set the probabilities of these two rules? If we set their probabilities to their overall probability in the Switchboard corpus, the two rules have about equal probability.

NP ! DT NN :28 NP ! PRP :25

Because PCFGs don’t allow a rule probability to be conditioned on surrounding context, this equal probability is all we get; there is no way to capture the fact that in subject position, the probability for NP ! PRP should go up to .91, while in object position, the probability for NP ! DT NNshould go up to .66.

These dependencies could be captured if the probability of expanding an NP as a pronoun (e.g., NP ! PRP) versus a lexical NP (e.g., NP ! DT NN) were con- ditioned on whether the NP was a subject or an object. Section[ C.5 ](#_page10_x160.20_y589.10)introduces the technique of parent annotation for adding this kind of conditioning.

C.4.2 Lack of Sensitivity to Lexical Dependencies

A second class of problems with PCFGs is their lack of sensitivity to the words in the parse tree. Words do play a role in PCFGs since the parse probability includes the probability of a word given a part-of-speech (e.g., from rules like V! sleep, NN! book, etc.).![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.010.png)

1<a name="_page8_x169.77_y678.80"></a> Distribution of subjects from 31,021 declarative sentences; distribution of objects from 7,489 sen- tences. This tendency is caused by the use of subject position to realize the topic or old information in a sentence [(Givon´ , 1990](#_page19_x72.42_y562.19)). Pronouns are a way to talk about old information, while non-pronominal (“lexical”) noun-phrases are often used to introduce new referents (Chapter 22).

But it turns out that lexical information is useful in other places in the grammar, such as in resolving prepositional phrase (PP) attachment ambiguities. Since prepo- sitional phrases in English can modify a noun phrase or a verb phrase, when a parser finds a prepositional phrase, it must decide where to attach it in the tree. Consider the following example:

<a name="_page9_x142.20_y173.76"></a>(C.18) Workers dumped sacks into a bin.

Figure[ C.5 ](#_page9_x475.20_y277.78)shows two possible parse trees for this sentence; the one on the left is the correct parse; Fig.[ C.6 ](#_page10_x493.20_y259.76)shows another perspective on the preposition attachment problem, demonstrating that resolving the ambiguity in Fig.[ C.5 ](#_page9_x475.20_y277.78)is equivalent to deciding whether to attach the prepositional phrase into the rest of the tree at the

VP attachment NP or VP nodes; we say that the correct parse requires VP attachment, and the NP attachment incorrect parse implies NP attachment.



|<p>S S</p><p>![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.011.png)<a name="_page9_x475.20_y277.78"></a> ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.012.png)</p><p>NP VP NP VP</p><p>![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.013.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.014.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.015.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.016.png)</p><p>NNS VBD NP PP NNS VBD NP![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.017.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.018.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.019.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.020.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.021.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.022.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.023.png)</p><p>workers dumped NNS P NP workers dumped NP PP![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.024.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.025.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.026.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.027.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.028.png)</p><p>sacks into DT NN NNS P NP</p><p>a bin sacks into DT NN a![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.029.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.030.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.031.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.032.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.033.png) bin![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.034.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.035.png)</p>|
| - |

Figure C.5 Two possible parse trees for a prepositional phrase attachment ambiguity. The left parse is the sensible one, in which “into a bin” describes the resulting location of the sacks. In the right incorrect parse, the sacks to be dumped are the ones which are already “into a bin”, whatever that might mean.

Why doesn’t a PCFG already deal with PP attachment ambiguities? Note that the two parse trees in Fig.[ C.5 ](#_page9_x475.20_y277.78)have almost exactly the same rules; they differ only in that the left-hand parse has this rule:


VP ! while the right-hand parse has these:

VP ! NP !

VBD NP PP

VBD NP NP PP


Depending on how these probabilities are set, a PCFG will always either prefer NP attachment or VP attachment. As it happens, NP attachment is slightly more common in English, so if we trained these rule probabilities on a corpus, we might always prefer NP attachment, causing us to misparse this sentence.

But suppose we set the probabilities to prefer the VP attachment for this sen- tence. Now we would misparse the following, which requires NP attachment:


C.5 • IMPROVING PCFGS BY SPLITTING NON-TERMINALS 11



||S|||||
| :- | - | :- | :- | :- | :- |
||NP VP|||||
|||PP NNS VBD NP||||
|||||||
|||||||
|||a bin||||
|<a name="_page10_x493.20_y259.76"></a>Figure C.6||||||

or NP nodes of the partial parse tree on the left?

<a name="_page10_x160.20_y313.87"></a>(C.19) fishermencaught tons of herring

What information in the input sentence lets us know that [(C.19)](#_page10_x160.20_y313.87) requires NP attachment while [(C.18)](#_page9_x142.20_y173.76) requires VP attachment? These preferences come from the identities of the verbs, nouns, and prepositions. The affinity between the verb dumped and the preposition into is greater than the affinity between the noun sacks and the preposition into, thus leading to VPattachment. On the other hand, in [(C.19) ](#_page10_x160.20_y313.87)the affinitybetween tons and ofis greater than that between caught and of, leading to NP attachment. Thus, to get the correct parse for these kinds of examples, we need a model that somehow augments the PCFG probabilities to deal with these lexical

dependencylexical dependency statistics for different verbs and prepositions.

Coordination ambiguities are another case in which lexical dependencies are the key to choosing the proper parse. Figure[ C.7 ](#_page11_x142.20_y270.49)shows an example from[ Collins (1999)](#_page19_x72.42_y487.40) with two parses for the phrase dogs in houses and cats. Because dogs is semantically a better conjunct for cats than houses (and because most dogs can’t fit inside cats), the parse [dogs in [NP houses and cats]] is intuitively unnatural and should be dispreferred. The two parses in Fig.[ C.7,](#_page11_x142.20_y270.49) however, have exactly the same PCFG rules, and thus a PCFG will assign them the same probability.

Insummary,wehaveshowninthissectionandthepreviousonethatprobabilistic context-free grammars are incapable of modeling important structural and lexical dependencies. In the next two sections we sketch current methods for augmenting PCFGs to deal with both these issues.

C.5 Impro<a name="_page10_x160.20_y589.10"></a>ving PCFGs by Splitting Non-Terminals

Let’s start with the first of the two problems with PCFGs mentioned above: their inability to model structural dependencies, like the fact that NPs in subject position

tend to be pronouns, whereas NPs in object position tend to have full lexical (non- pronominal) form. How could we augment a PCFG to correctly model this fact?

split One idea would be to split the NP non-terminal into two versions: one for sub- jects, one for objects. Having two nodes (e.g., NPsubject and NPobject) would allow

us to correctly model their different distributional properties, since we would have

12  APPENDIX C • STATISTICAL CONSTITUENCY PARSING

NP NP![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.036.png)

NP Conj NP NP PP

NP PP and Noun Noun Prep NP

Noun Prep NP cats dogs in NP Conj NP dogs in Noun Noun and Noun

<a name="_page11_x142.20_y270.49"></a>houses houses cats

Figure C.7 Aninstance ofcoordinationambiguity. Althoughtheleftstructureisintuitively the correct one, a PCFG will assign them identical probabilities since both structures use exactly the same set of rules. After[ Collins (1999](#_page19_x72.42_y487.40)).

different probabilities for the rule NPsubject ! PRP and the rule NPobject ! PRP. annotationparent[ ](#_page19_x278.29_y109.65)One way to implement this intuition of splits is to do parent annotation [(John-](#_page19_x278.29_y109.65)

[son, 1998](#_page19_x278.29_y109.65)), in which we annotate each node with its parent in the parse tree. Thus,

an NP node that is the subject of the sentence and hence has parent Swould be anno-

tated NPˆS, while a direct object NP whose parent is VPwould be annotated NPˆVP.

Figure[ C.8 ](#_page11_x142.20_y561.01)shows an example of a tree produced by a grammar that parent-annotates

the phrasal non-terminals (like NP and VP).

a) S b) S![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.037.png)

NP VP NPˆS VPˆS

PRP VBD NP PRP VBD NPˆVP

I need DT NN I need DT NN

a flight a flight

<a name="_page11_x142.20_y561.01"></a>Figure C.8 A standard PCFG parse tree (a) and one which has parent annotation on the nodes which aren’t pre-terminal (b). All the non-terminal nodes (except the pre-terminal part-of-speech nodes) in parse (b) have been annotated with the identity of their parent.

In addition to splitting these phrasal nodes, we can also improve a PCFG by splitting the pre-terminal part-of-speech nodes [(Klein and Manning, 2003b](#_page19_x278.29_y244.45)). For ex- ample, different kinds of adverbs (RB) tend to occur in different syntactic positions: the most common adverbs with ADVP parents are also and now, with VP parents n’t and not, and with NP parents only and just. Thus, adding tags like RBˆADVP, RBˆVP, and RBˆNP can be useful in improving PCFG modeling.

Similarly, the Penn Treebank tag IN can mark a wide variety of parts-of-speech, including subordinating conjunctions (while, as, if), complementizers (that, for), and prepositions (of, in, from). Some of these differences can be captured by parent

C.6 • PROBABILISTIC LEXICALIZED CFGS 15

annotation(subordinatingconjunctionsoccurunderS,prepositionsunderPP),while others require splitting the pre-terminal nodes. Figure[ C.9 ](#_page12_x493.20_y504.57)shows an example from [Klein and Manning (2003b)](#_page19_x278.29_y244.45) in which even a parent-annotated grammar incorrectly parsesworksasanounintoseeifadvertisingworks. Splittingpre-terminalstoallow

ifto prefer a sentential complement results in the correct verbal parse. Node-splitting is not without problems; it increases the size of the grammar and

hence reduces the amount of training data available for each grammar rule, leading tooverfitting. Thus, itisimportanttosplittojustthecorrectlevelofgranularityfora

particular training set. While early models employed handwritten rules to try to find an optimal number of non-terminals [(Klein and Manning, 2003b](#_page19_x278.29_y244.45)), modern models

split and merge[ automatically](#_page19_x278.29_y440.75) search for the optimal splits. The split and merge algorithm of[ Petrov et al. (2006](#_page19_x278.29_y440.75)), for example, starts with a simple X-bar grammar, alternately splits the

non-terminals, and merges non-terminals, finding the set of annotated nodes that

maximizes the likelihood of the training set treebank.

C.6 Probabilistic Lexicalized CFGs

The previous section showed that a simple probabilistic CKY algorithm for pars- ing raw PCFGs can achieve extremely high parsing accuracy if the grammar rule symbols are redesigned by automatic splits and merges.

In this section, we discuss an alternative family of models in which instead of modifying the grammar rules, we modify the probabilistic model of the parser to allow for lexicalized rules. The resulting family of lexicalized parsers includes the Collins parser [(Collins, 1999)](#_page19_x72.42_y487.40) and the Charniak parser [(Charniak, 1997](#_page19_x72.42_y422.07)).

We saw in Section ?? that syntactic constituents could be associated with a lexi- lexicalizedgrammar cal head, and we defined a lexicalized grammar in which each non-terminal in the

tree is annotated with its lexical head, where a rule like VP! VBD NP PP would

be extended as

VP(dumped) ! VBD(dumped) NP(sacks) PP(into) (C.20)



||VPˆS VPˆS||||||
| :- | - | :- | :- | :- | :- | :- |
||<a name="_page12_x493.20_y504.57"></a>TO VPˆVP TOˆVP VPˆVP||||||
||||||||
||||||||
||||||||
||||||||
||||||||
|Figure C.9|||||||

duced by a grammar in which the pre-terminal nodes have been split, allowing the probabilistic grammar to capture the fact that ifprefers sentential complements. Adapted from[ Klein and Manning (2003b](#_page19_x278.29_y244.45)).

In the standard type of lexicalized grammar, we actually make a further exten- head tag sion, which is to associate the head tag, the part-of-speech tags of the headwords,

with the non-terminal symbols as well. Each rule is thus lexicalized by both the headword and the head tag of each constituent resulting in a format for lexicalized

rules like

VP(dumped,VBD)! VBD(dumped,VBD) NP(sacks,NNS) PP(into,P) (C.21) We show a lexicalized parse tree with head tags in Fig.[ C.10,](#_page13_x475.20_y429.51) extended from Fig. ??.



|<p>TOP S(dumped,VBD)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.038.png)</p><p>![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.039.png)</p><p>NP(workers,NNS) VP(dumped,VBD)</p><p>![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.040.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.041.png)</p><p>NNS(workers,NNS) VBD(dumped,VBD) NP(sacks,NNS) PP(into,P)</p><p>![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.042.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.043.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.044.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.045.png)</p><p>workers dumped NNS(sacks,NNS) P(into,P) NP(bin,NN)</p><p>![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.046.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.047.png) ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.048.png)</p><p>sacks into DT(a,DT) NN(bin,NN)</p><p>a bin![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.049.png)![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.050.png)</p>|
| :- |
|<p>Internal Rules Lexical Rules![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.051.png)</p><p><a name="_page13_x475.20_y429.51"></a>TOP ! S(dumped,VBD) NNS(workers,NNS) ! workers S(dumped,VBD) ! NP(workers,NNS) VP(dumped,VBD) VBD(dumped,VBD) ! dumped NP(workers,NNS) ! NNS(workers,NNS) NNS(sacks,NNS) ! sacks VP(dumped,VBD) ! VBD(dumped, VBD) NP(sacks,NNS) PP(into,P) P(into,P) ! into PP(into,P) ! P(into,P) NP(bin,NN) DT(a,DT) ! a NP(bin,NN) ! DT(a,DT) NN(bin,NN) NN(bin,NN) ! bin</p>|

Figure C.10 A lexicalized tree, including head tags, for a WSJ sentence, adapted from[ Collins (1999](#_page19_x72.42_y487.40)). Below we show the PCFG rules needed for this parse tree, internal rules on the left, and lexical rules on the right.

To generate such a lexicalized tree, each PCFG rule must be augmented to iden- tify one right-hand constituent to be the head daughter. The headword for a node is then set to the headword of its head daughter, and the head tag to the part-of-speech tag of the headword. Recall that we gave in Fig. ?? a set of handwritten rules for identifying the heads of particular constituents.

A natural way to think of a lexicalized grammar is as a parent annotation, that is, as a simple context-free grammar with many copies of each rule, one copy for each possible headword/head tag for each constituent. Thinking of a probabilistic lexicalizedCFGinthiswaywouldleadtothesetofsimplePCFGrulesshownbelow the tree in Fig.[ C.10.](#_page13_x475.20_y429.51)

lexical rules Note that Fig.[ C.10 ](#_page13_x475.20_y429.51)shows two kinds of rules: lexical rules, which express the internal rules expansion of a pre-terminal to a word, and internal rules, which express the other

ruleexpansions. Weneedtodistinguishthesekindsofrulesinalexicalizedgrammar because they are associated with very different kinds of probabilities. The lexical rules are deterministic, that is, they have probability 1.0 since a lexicalized pre-

C.6 • PROBABILISTIC LEXICALIZED CFGS 16

terminal like NN(bin;NN) can only expand to the word bin. But for the internal rules, we need to estimate probabilities.

Suppose we were to treat a probabilistic lexicalized CFG like a really big CFG that just happened to have lots of very complex non-terminals and estimate the probabilities for each rule from maximum likelihood estimates. Thus, according to Eq.[ C.17,](#_page7_x142.20_y240.68) the MLE estimate for the probability for the rule P(VP(dumped,VBD) ! VBD(dumped, VBD) NP(sacks,NNS) PP(into,P))would be

<a name="_page14_x179.85_y203.74"></a>Count(VP(dumped,VBD)! VBD(dumped, VBD) NP(sacks,NNS) PP(into,P))

(C.22) Count(VP(dumped,VBD))

But there’s no way we can get good estimates of counts like those in [(C.22)](#_page14_x179.85_y203.74) because they are so specific: we’re unlikely to see many (or even any) instances of a sentence with a verb phrase headed by dumped that has one NP argument headed by sacks and a PP argument headed by into. In other words, counts of fully lexicalized PCFG rules like this will be far too sparse, and most rule probabilities will come out 0.

The idea of lexicalized parsing is to make some further independence assump- tions to break down each rule so that we would estimate the probability

P(VP(dumped,VBD)! VBD(dumped, VBD) NP(sacks,NNS) PP(into,P))

as the product of smaller independent probability estimates for which we could ac- quire reasonable counts. The next section summarizes one such method, the Collins parsing method.

C.6.1 The Collins Parser

Statistical parsers differ in exactly which independence assumptions they make. Let’s look at the assumptions in a simplified version of the Collins parser. The first intuition of the Collins parser is to think of the right-hand side of every (internal) CFG rule as consisting of a head non-terminal, together with the non-terminals to the left of the head and the non-terminals to the right of the head. In the abstract, we think about these rules as follows:

LHS! Ln Ln 1 :::L1 HR1 :::Rn 1 Rn (C.23)

Since this is a lexicalized grammar, each of the symbols like L1 or R3 or H or LHS is actually a complex symbol representing the category and its head and head tag, like VP(dumped,VP)or NP(sacks,NNS).

Now, instead of computing a single MLE probability for this rule, we are going to break down this rule via a neat generative story, a slight simplification of what is called Collins Model 1. This new generative story is that given the left-hand side, we first generate the head of the rule and then generate the dependents of the head, one by one, from the inside out. Each of these steps will have its own probability.

We also add a special STOP non-terminal at the left and right edges of the rule; this non-terminal allows the model to know when to stop generating dependents on a givenside. Wegeneratedependentsontheleftsideoftheheaduntilwe’vegenerated STOP on the left side of the head, at which point we move to the right side of the head and start generating dependents there until we generate STOP. So it’s as if we are generating a rule augmented as follows:

P(VP(dumped,VBD)! (C.24)

STOP VBD(dumped, VBD) NP(sacks,NNS) PP(into,P)STOP)

16  APPENDIX C • STATISTICAL CONSTITUENCY PARSING

Let’s see the generative story for this augmented rule. We make use of three kinds of probabilities: PH for generating heads, PL for generating dependents on the left, and PR for generating dependents on the right.![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.052.png)

VP(dumped,VBD)

1. Generate the head VBD(dumped,VBD) with probability ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.053.png)

PH(H j LHS) = PH(VBD(dumped,VBD) j VP(dumped,VBD)) VBD(dumped,VBD)

2. Generatetheleftdependent(whichisSTOP,sincethereisn’t VP(dumped,VBD)

one) with probability ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.054.png)

PL(STOP j VP(dumped,VBD) VBD(dumped,VBD)) STOP VBD(dumped,VBD)

VP(dumped,VBD)

3. Generate right dependent NP(sacks,NNS) with probability ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.055.png)PR(NP(sacks,NNS) j VP(dumped,VBD), VBD(dumped,VBD)) 

   STOP VBD(dumped,VBD) NP(sacks,NNS) VP(dumped,VBD) 4. Generate the right dependent PP(into,P) with probability ![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.056.png)

   PR(PP(into,P) j VP(dumped,VBD), VBD(dumped,VBD))

STOP VBD(dumped,VBD) NP(sacks,NNS) PP(into,P) VP(dumped,VBD)

\5) Generate the right dependent STOP with probability P![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.057.png)R(STOP j VP(dumped,VBD), VBD(dumped,VBD))

STOP VBD(dumped,VBD) NP(sacks,NNS) PP(into,P) STOP![](Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.058.png)

In summary, the probability of this rule

<a name="_page15_x203.22_y489.95"></a>P(VP(dumped,VBD)! (C.25)

VBD(dumped, VBD) NP(sacks,NNS) PP(into,P))

is estimated (simplifying the notation a bit from the steps above):

PH(VBDjVP, dumped)  PL(STOPjVP;VBD;dumped) (C.26)

- PR(NP(sacks,NNS)jVP;VBD;dumped)
- PR(PP(into,P)jVP;VBD;dumped)
- PR(STOPjVP;VBD;dumped)

Each of these probabilities can be estimated from much smaller amounts of data than the full probability in [(C.25](#_page15_x203.22_y489.95)). For example, the maximum likelihood estimate for the component probability PR(NP(sacks,NNS)jVP;VBD;dumped) is

Count(VP(dumped,VBD) with NNS(sacks)as a daughter somewhere on the right) Count( VP(dumped,VBD))

(C.27) These counts are much less subject to sparsity problems than are complex counts like those in [(C.25](#_page15_x203.22_y489.95)).


C.7 • SUMMARY 17

More generally, if H is a head with head word hw and head tag ht, lw=lt and rw=rt are the word/tag on the left and right respectively, and P is the parent, then the probability of an entire rule can be expressed as follows:

1. Generate the head of the phrase H(hw;ht) with probability:

PH(H(hw;ht)jP;hw;ht)

2. Generate modifiersto the left of the head with total probability

nY+1

PL(Li(lwi;lti)jP;H;hw;ht)

i=1

such that Ln+1(lwn+1;ltn+1)= STOP, and we stop generating once we’ve gen- erated a STOP token.

3. Generate modifiersto the right of the head with total probability:

nY+1

PR(Ri(rwi;rti)jP;H;hw;ht)

i=1

such that Rn+1(rwn+1;rtn+1)= STOP, and we stop generating once we’ve gen- erated a STOP token.

The parsing algorithm for the Collins model is an extension of probabilistic CKY. Extending the CKY algorithm to handle basic lexicalized probabilities is left as Exercises 14.5 and 14.6 for the reader.

C.7 Summary

This chapter has sketched the basics of probabilistic parsing, concentrating on probabilistic context-free grammars.

- Probabilistic grammars assign a probability to a sentence or string of words while attempting to capture sophisticated grammatical information.
- A probabilistic context-free grammar (PCFG) is a context-free grammar in which every rule is annotated with the probability of that rule being chosen. Each PCFG rule is treated as if it were conditionally inde- pendent; thus, the probability of a sentence is computed by multiplying the probabilities of each rule in the parse of the sentence.
- TheprobabilisticCKY(Cocke-Kasami-Younger)algorithmisaprobabilistic version of the CKY parsing algorithm.
- PCFG probabilities can be learned by counting in a parsed corpus or by pars- ing a corpus. The inside-outside algorithm is a way of dealing with the fact that the sentences being parsed are ambiguous.
- RawPCFGssufferfrompoorindependenceassumptionsamongrulesandlack of sensitivity to lexical dependencies.
- One way to deal with this problem is to split and merge non-terminals (auto- matically or by hand).
- Probabilistic lexicalized CFGs are another solution to this problem in which the basic PCFG model is augmented with a lexical head for each rule. The probability of a rule can then be conditioned on the lexical head or nearby heads.
- ParsersforlexicalizedPCFGs(liketheCollinsparser)arebasedonextensions to probabilistic CKY parsing.

Bibliographical and Historical Notes

Many of the formal properties of probabilistic context-free grammars were first workedout by[Booth(1969)](#_page19_x72.42_y265.86) and[Salomaa(1969](#_page19_x278.29_y554.26)).[ Baker(1979)](#_page19_x72.42_y131.43)proposedtheinside- outside algorithm for unsupervised training of PCFG probabilities, and used a CKY- style parsing algorithm to compute inside probabilities.[ Jelinek and Lafferty (1991) ](#_page19_x72.42_y636.99)extended the CKY algorithm to compute probabilities for prefixes. [Stolcke (1995) ](#_page19_x278.29_y689.06)adapted the Earley algorithm to use with PCFGs.

A number of researchers starting in the early 1990s worked on adding lexical de- pendencies to PCFGs and on making PCFG rule probabilities more sensitive to sur- rounding syntactic structure. For example,[ Schabes et al. (1988)](#_page19_x278.29_y627.57) and[ Schabes (1990) ](#_page19_x278.29_y575.55)presented early work on the use of heads. Many papers on the use of lexical depen- dencies were firstpresented at the DARPA Speech and Natural Language Workshop in June 1990. A paper by[ Hindle and Rooth (1990)](#_page19_x72.42_y583.97) applied lexical dependencies to the problem of attaching prepositional phrases; in the question session to a later paper, Ken Church suggested applying this method to full parsing [(Marcus, 1990](#_page19_x278.29_y379.25)). Early work on such probabilistic CFG parsing augmented with probabilistic depen- dency information includes[ Magerman and Marcus (1991](#_page19_x278.29_y336.69)),[ Black et al. (1992](#_page19_x72.42_y193.91)),[ Bod (1993](#_page19_x72.42_y244.08)), and[ Jelinek et al. (1994](#_page19_x72.42_y677.69)), in addition to[ Collins (1996](#_page19_x72.42_y465.62)),[ Charniak (1997](#_page19_x72.42_y422.07)), and [Collins (1999)](#_page19_x72.42_y487.40) discussed above. Other recent PCFG parsing models include[ Klein and Manning (2003a)](#_page19_x278.29_y223.17) and[ Petrov et al. (2006](#_page19_x278.29_y440.75)).

This early lexical probabilistic work led initially to work focused on solving specific parsing problems like preposition-phrase attachment by using methods in- cluding transformation-based learning (TBL) [(Brill and Resnik, 1994](#_page19_x72.42_y350.12)), maximum entropy [(Ratnaparkhi et al., 1994](#_page19_x278.29_y492.77)), memory-based learning [(Zavrel and Daelemans, 1997](#_page20_x90.42_y109.65)), log-linear models [(Franz, 1997](#_page19_x72.42_y540.42)), decision trees that used semantic distance between heads (computed from WordNet) [(Stetina and Nagao, 1997](#_page19_x278.29_y658.32)), and boosting [(Abney et al., 1999](#_page19_x72.42_y109.65)). Another direction extended the lexical probabilistic parsing work to build probabilistic formulations of grammars other than PCFGs, such as probabilistic TAG grammar [(Resnik 1992,](#_page19_x278.29_y523.52)[ Schabes 1992](#_page19_x278.29_y606.29)), based on the TAG gram- mars discussed in Chapter 12, probabilistic LR parsing [(Briscoe and Carroll, 1993](#_page19_x72.42_y381.36)), and probabilistic link grammar [(Lafferty et al., 1992](#_page19_x278.29_y265.74)). The supertagging approach we saw for CCG was developed for TAG grammars [(Bangalore and Joshi 1999, ](#_page19_x72.42_y162.67)[Joshi and Srinivas 1994](#_page19_x278.29_y180.61)), based on the lexicalized TAG grammars of[ Schabes et al. (1988](#_page19_x278.29_y627.57)).

Exercises

<a name="_page17_x142.20_y724.32"></a>C.1 Implement the CKY algorithm.


EXERCISES 19

C.2 Modify the algorithm for conversion to CNF from Chapter 13 to correctly

handle rule probabilities. Make sure that the resulting CNF assigns the same total probability to each parse tree.

<a name="_page18_x160.20_y149.67"></a>C.3 Recall that Exercise 13.3 asked you to update the CKY algorithm to han-

dle unit productions directly rather than converting them to CNF. Extend this change to probabilistic CKY.

<a name="_page18_x160.20_y190.02"></a>C.4 Fill out the rest of the probabilistic CKY chart in Fig.[ C.4.](#_page6_x493.20_y642.53)

C.5 Sketch how the CKY algorithm would have to be augmented to handle lexi-

calized probabilities.

C.6 Implement your lexicalized extension of the CKY algorithm.

20 Appendix C • Statistical Constituency Parsing![ref4]

<a name="_page19_x72.42_y109.65"></a>Abney, S. P., R. E. Schapire, and Y. Singer. 1999. Boosting<a name="_page19_x278.29_y109.65"></a>applied to tagging and PP attachment. EMNLP/VLC.

Baker, J. K. 1979. Trainable grammars for speech recogni-

tion. Speech Communication Papers for the 97th Meeting of the Acoustical Society of America.

<a name="_page19_x72.42_y162.67"></a>Bangalore, S. and A. K. Joshi. 1999. Supertagging: An

approach to almost parsing. Computational Linguistics,<a name="_page19_x278.29_y180.61"></a>25(2):237–265.

Black, E., F. Jelinek, J. D. Lafferty, D. M. Magerman, R. L.

Mercer, and S. Roukos. 1992. Towards history-based grammars: Using richer models for probabilistic pars- ing. Proceedings DARPA Speech and Natural Language Workshop.

<a name="_page19_x72.42_y244.08"></a>Bod, R. 1993. Using an annotated corpus as a stochastic

<a name="_page19_x278.29_y244.45"></a>grammar. EACL.

Booth, T. L. 1969. Probabilistic representation of formal

languages. IEEE Conference Record of the 1969 Tenth Annual Symposium on Switching and Automata Theory.

<a name="_page19_x72.42_y297.10"></a>Booth, T. L. and R. A. Thompson. 1973. Applying proba-

<a name="_page19_x278.29_y305.95"></a>bility measures to abstract languages. IEEE Transactions on Computers, C-22(5):442–450.

Bresnan, J., editor. 1982. The Mental Representation of

<a name="_page19_x278.29_y336.69"></a>Grammatical Relations. MIT Press.

Brill, E. and P. Resnik. 1994. A rule-based approach to

<a name="_page19_x278.29_y357.97"></a>prepositional phrase attachment disambiguation. COL- ING.

Briscoe, T. and J. Carroll. 1993. Generalized proba-

bilistic LR parsing of natural language (corpora) with unification-based grammars. Computational Linguistics, 19(1):25–59.

<a name="_page19_x278.29_y410.00"></a>Charniak, E. 1997. Statistical parsing with a context-free

grammar and word statistics. AAAI.

<a name="_page19_x278.29_y440.75"></a>Chelba, C. and F. Jelinek. 2000. Structured language model-

ing. Computer Speech and Language, 14:283–332.

<a name="_page19_x72.42_y465.62"></a>Collins, M. 1996. A new statistical parser based on bigram

<a name="_page19_x278.29_y471.49"></a>lexical dependencies. ACL.

Collins, M. 1999. Head-Driven Statistical Models for Natu-

<a name="_page19_x278.29_y492.77"></a>ral Language Parsing. Ph.D. thesis, University of Penn- sylvania, Philadelphia.

Francis,H.S.,M.L.Gregory,andL.A.Michaelis.1999.Are<a name="_page19_x278.29_y523.52"></a>lexical subjects deviant? CLS-99. University of Chicago.

Franz, A. 1997. Independence assumptions considered

harmful. ACL.

<a name="_page19_x278.29_y554.26"></a>Givon,´ T. 1990. Syntax: A Functional Typological Introduc-

tion. John Benjamins.

<a name="_page19_x278.29_y575.55"></a>Hindle, D. and M. Rooth. 1990. Structural ambiguity and

lexical relations. Proceedings DARPA Speech and Natu- ral Language Workshop.

<a name="_page19_x278.29_y606.29"></a>Hindle, D. and M. Rooth. 1991. Structural ambiguity and

lexical relations. ACL.

<a name="_page19_x278.29_y627.57"></a>Jelinek, F. and J. D. Lafferty. 1991. Computation of the

probability of initial substring generation by stochas- tic context-free grammars. Computational Linguistics,<a name="_page19_x278.29_y658.32"></a>17(3):315–323.

Jelinek, F., J. D. Lafferty, D. M. Magerman, R. L. Mercer,

A. Ratnaparkhi, and S. Roukos. 1994. Decision tree pars-<a name="_page19_x278.29_y689.06"></a>ing using a hidden derivation model. ARPA Human Lan- guage Technologies Workshop.

Johnson, M. 1998. PCFG models of linguistic tree represen-

tations. Computational Linguistics, 24(4):613–632.

<a name="_page19_x72.42_y131.43"></a><a name="_page19_x278.29_y130.94"></a>Joshi, A. K. 1985. Tree adjoining grammars: How

muchcontext-sensitivityisrequiredtoprovidereasonable structural descriptions? In David R. Dowty, Lauri Kart- tunen, and Arnold Zwicky, editors, Natural Language Parsing, pages 206–250. Cambridge University Press.

Joshi, A. K. and B. Srinivas. 1994. Disambiguation of super <a name="_page19_x72.42_y193.91"></a>parts of speech (or supertags): Almost parsing. COLING.

Klein, D. and C. D. Manning. 2001. Parsing and hyper-

graphs. IWPT-01.

<a name="_page19_x278.29_y223.17"></a>Klein, D. and C. D. Manning. 2003a.[ A* parsing: Fast exact](https://www.aclweb.org/anthology/N03-1016)

[Viterbi parse selection.](https://www.aclweb.org/anthology/N03-1016) HLT-NAACL.

Klein, D. and C. D. Manning. 2003b. Accurate unlexicalized

parsing. HLT-NAACL.

<a name="_page19_x72.42_y265.86"></a><a name="_page19_x278.29_y265.74"></a>Lafferty, J. D., D. Sleator, and D. Temperley. 1992. Gram-

matical trigrams: A probabilistic model of link gram- mar. AAAI Fall Symposium on Probabilistic Approaches to Natural Language.

Lari, K. and S. J. Young. 1990. The estimation of stochas-

tic context-free grammars using the Inside-Outside algo- <a name="_page19_x72.42_y328.34"></a>rithm. Computer Speech and Language, 4:35–56.

Magerman, D. M. and M. P. Marcus. 1991. Pearl: A proba-

<a name="_page19_x72.42_y350.12"></a>bilistic chart parser. EACL.

Manning, C. D. and H. Schutze.¨ 1999. Foundations of Sta-

tistical Natural Language Processing. MIT Press.

<a name="_page19_x72.42_y381.36"></a><a name="_page19_x278.29_y379.25"></a>Marcus, M. P. 1990. Summary of session 9: Automatic

acquisition of linguistic structure. Proceedings DARPA Speech and Natural Language Workshop.

Ney, H. 1991. Dynamic programming parsing for context-

<a name="_page19_x72.42_y422.07"></a>free grammars in continuous speech recognition. IEEE Transactions on Signal Processing, 39(2):336–340.

<a name="_page19_x72.42_y443.84"></a>Petrov,S.,L.Barrett,R.Thibaux,andD.Klein.2006.[ Learn-](http://www.aclweb.org/anthology/P/P06/P06-1055)

[ing accurate, compact, and interpretable tree annotation. ](http://www.aclweb.org/anthology/P/P06/P06-1055)COLING/ACL.

Pollard, C. and I. A. Sag. 1994. Head-Driven Phrase Struc-

<a name="_page19_x72.42_y487.40"></a>ture Grammar. University of Chicago Press.

Ratnaparkhi, A., J. C. Reynar, and S. Roukos. 1994. A max-

imum entropy model for prepositional phrase attachment. <a name="_page19_x72.42_y518.64"></a>ARPA Human Language Technologies Workshop.

Resnik, P. 1992. Probabilistic tree-adjoining grammar as

<a name="_page19_x72.42_y540.42"></a>a framework for statistical natural language processing. COLING.

<a name="_page19_x72.42_y562.19"></a>Salomaa, A. 1969. Probabilistic and weighted grammars.

Information and Control, 15:529–544.

<a name="_page19_x72.42_y583.97"></a>Schabes, Y. 1990. Mathematical and Computational As-

pects of Lexicalized Grammars. Ph.D. thesis, University of Pennsylvania, Philadelphia, PA.

Schabes, Y. 1992. Stochastic lexicalized tree-adjoining

grammars. COLING.

<a name="_page19_x72.42_y636.99"></a>Schabes, Y., A. Abeille,´ and A. K. Joshi. 1988. Parsing

strategies with ‘lexicalized’ grammars: Applications to Tree Adjoining Grammars. COLING.

Stetina, J. and M. Nagao. 1997. Corpus based PP attachment

ambiguity resolution with a semantic dictionary. Pro- <a name="_page19_x72.42_y677.69"></a>ceedings of the Fifth Workshop on Very Large Corpora.

Stolcke, A. 1995. An efficient probabilistic context-free

parsing algorithm that computes prefix probabilities. Computational Linguistics, 21(2):165–202.

Exercises 21![ref4]

<a name="_page20_x90.42_y109.65"></a>Zavrel, J.andW.Daelemans.1997. Memory-basedlearning:

Using similarity for smoothing. ACL.

[ref1]: Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.006.png
[ref2]: Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.007.png
[ref3]: Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.008.png
[ref4]: Aspose.Words.7856884f-5e5c-48a2-a825-084a504f18d8.059.png
