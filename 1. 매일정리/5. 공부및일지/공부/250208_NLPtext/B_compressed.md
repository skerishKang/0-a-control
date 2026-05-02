Speech and Language Processing. Daniel Jurafsky & James H. Martin. Copyright © 2021. All rights reserved. Draft of September 21, 2021.

CHAPTER ![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.001.png)

B SpellingNoisy ChannelCorrection and the

ALGERNON: But my own sweet Cecily, I have never written you any letters. CECILY: You need hardly remind me of that, Ernest. I remember only too well that I was forced to write your letters for you. I wrote always three times a week, and sometimes oftener.

ALGERNON: Oh, do let me read them, Cecily?

CECILY: Oh, I couldn’t possibly. They would make you far too conceited. The three you wrote me after I had broken off the engagement are so beautiful, and so badly spelled, that even now I can hardly read them without crying a little.

Oscar Wilde, The Importance of Being Earnest

Like Oscar Wilde’s fabulous Cecily, a lot of people were thinking about spelling during the last turn of the century. Gilbert and Sullivan provide many examples. The Gondoliers’Giuseppe, forexample,worriesthathisprivatesecretaryis“shakyinhis spelling”, while Iolanthe’s Phyllis can “spell every word that she uses”. Thorstein Veblen’s explanation (in his 1899 classic The Theory of the Leisure Class) was that a main purpose of the “archaic, cumbrous, and ineffective” English spelling system was to be difficultenough to provide a test of membership in the leisure class.

Whatever the social role of spelling, we can certainly agree that many more of us are like Cecily than like Phyllis. Estimates for the frequency of spelling errors in human-typed text vary from 1-2% for carefully retyping already printed text to 10-15% for web queries.

In this chapter we introduce the problem of detecting and correcting spelling errors. Fixing spelling errors is an integral part of writing in the modern world, whether this writing is part of texting on a phone, sending email, writing longer documents,orfindinginformationontheweb. Modernspellcorrectorsaren’tperfect (indeed, autocorrect-gone-wrong is a popular source of amusement on the web) but

they are ubiquitous in pretty much any software that relies on keyboard input. Spellingcorrectionisoftenconsideredfromtwoperspectives. Non-wordspelling correction is the detection and correction of spelling errors that result in non-words (like graffe for giraffe). By contrast, real word spelling correction is the task of detecting and correcting spelling errors even if they accidentally result in an actual

real-werrordors word of English (real-word errors). This can happen from typographical errors (insertion, deletion, transposition) that accidentally produce a real word (e.g., there

for three), or cognitive errors where the writer substituted the wrong spelling of a homophone or near-homophone (e.g., dessert for desert, or piece for peace).

Non-word errors are detected by looking for any word not found in a dictio- nary. For example, the misspelling graffe above would not occur in a dictionary. The larger the dictionary the better; modern systems often use enormous dictio- naries derived from the web. To correct non-word spelling errors we first generate

2  APPENDIX B • SPELLING CORRECTION AND THE NOISY CHANNEL

candidates candidates: real words that have a similar letter sequence to the error. Candidate

corrections from the spelling error graffe might include giraffe, graf, gaffe, grail, or craft. We then rank the candidates using a distance metric between the source and the surface error. We’d like a metric that shares our intuition that giraffe is a more likely source than grail for graffe because giraffe is closer in spelling to graffe than grail is to graffe. The minimum edit distance algorithm from Chapter 2 will play a role here. But we’d also like to prefer corrections that are more frequent words, or more likely to occur in the context of the error. The noisy channel model introduced in the next section offers a way to formalize this intuition.

Realwordspellingerror detectionisamuchmoredifficulttask, sinceanyword in the input text could be an error. Still, it is possible to use the noisy channel to find candidates for each word w typed by the user, and rank the correction that is most likely to have been the user’s original intention.

B.1 The Noisy Channel Model![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.002.png)

In this section we introduce the noisy channel model and show how to apply it to the task of detecting and correcting spelling errors. The noisy channel model was appliedtothespellingcorrectiontaskataboutthesametimebyresearchersatAT&T Bell Laboratories [(Kernighan et al. 1990,](#_page13_x72.42_y499.21)[ Church and Gale 1991)](#_page13_x72.42_y229.51) and IBM Watson Research [(Mays et al., 1991](#_page13_x72.42_y604.35)).

noisy channel![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.003.png)

original word

noisy word

decoder

word hyp1 ![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.004.png)

guessed word word hyp2 noisy 1![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.005.png)

... noisy 2 ![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.006.png)word hyp3 noisy N

<a name="_page1_x142.20_y545.47"></a>Figure B.1 In the noisy channel model, we imagine that the surface form we see is actually a “distorted” form of an original word passed through a noisy channel. The decoder passes each hypothesis through a model of this channel and picks the word that best matches the surface noisy word.

noisy channel The intuition of the noisy channel model (see Fig.[ B.1)](#_page1_x142.20_y545.47) is to treat the misspelled

word as if a correctly spelled word had been “distorted” by being passed through a noisy communication channel.

This channel introduces “noise” in the form of substitutions or other changes to the letters, making it hard to recognize the “true” word. Our goal, then, is to build a model of the channel. Given this model, we then findthe true word by passing every word of the language through our model of the noisy channel and seeing which one comes the closest to the misspelled word.

Bayesian This noisy channel model is a kind of Bayesian inference. We see an obser-

B.1 • THE NOISY CHANNEL MODEL 5

vation x (a misspelled word) and our job is to find the word w that generated this misspelled word. Out of all possible words in the vocabulary V we want to find the word wsuch that P(wjx) is highest. We use the hat notation ˆ to mean “our estimate of the correct word”.

<a name="_page2_x160.20_y155.12"></a>wˆ = argmaxP(wjx) (B.1)

w2V

argmax The function argmaxx f(x) means “the x such that f(x) is maximized”. Equa- tion[ B.1 ](#_page2_x160.20_y155.12)thus means, that out of all words in the vocabulary, we want the particular

word that maximizes the right-hand side P(wjx). TheintuitionofBayesianclassificationistouseBayes’ruletotransformEq.[B.1 ](#_page2_x160.20_y155.12)into a set of other probabilities. Bayes’ rule is presented in Eq.[ B.2;](#_page2_x477.77_y251.72) it gives us a w<a name="_page2_x477.77_y251.72"></a>ay

to break down any conditional probability P(ajb) into three other probabilities:

P(bja)P(a)

P(ajb) = (B.2)

P(b)

We can then substitute Eq.[ B.2 ](#_page2_x477.77_y251.72)into Eq.[ B.1 ](#_page2_x160.20_y155.12)to get Eq.[ B.3:](#_page2_x396.61_y306.92)

<a name="_page2_x396.61_y306.92"></a>P(xjw)P(w)

wˆ = argmax (B.3)

w2V P(x)

We can conveniently simplify Eq.[ B.3 ](#_page2_x396.61_y306.92)by dropping the denominator P(x). Why is that? Since we are choosing a potential correction word out of all words, we will be computing P(xjPw()xP)(w) for each word. But P(x) doesn’t change for each word; we

are always asking about the most likely word for the same observed error x, which must have the same probability P(x). Thus, we can choose the word that maximizes this simpler formula:

<a name="_page2_x160.20_y439.88"></a>wˆ = argmaxP(xjw)P(w) (B.4)

w2V

To summarize, the noisy channel model says that we have some true underlying word w, and we have a noisy channel that modifies the word into some possible

likelihood misspelled observed surface form. The likelihood or channel model of the noisy channel model channel producing any particular observation sequence xis modeled by P(xjw). The

probabilityprior prior probability of a hidden word is modeled by P(w). We can compute the most probable word wˆ given that we’ve seen some observed misspelling x by multiply-

ing the prior P(w) and the likelihood P(xjw) and choosing the word for which this

product is greatest.

We apply the noisy channel approach to correcting non-word spelling errors by taking any word not in our spelling dictionary, generating a list of candidate words, ranking them according to Eq.[ B.4,](#_page2_x160.20_y439.88) and picking the highest-ranked one. We can modify Eq.[ B.4 ](#_page2_x160.20_y439.88)<a name="_page2_x215.83_y617.47"></a>to refer to this list of candidate words instead of the full vocabulary V as follows:

channel model prior

z~~ }|~~ { z}|~~ {![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.007.png)

wˆ = argmax P(xjw) P(w) (B.5)

w2C

The noisy channel algorithm is shown in Fig.[ B.2.](#_page3_x475.20_y164.71)

To see the details of the computation of the likelihood and the prior (language model), let’s walk through an example, applying the algorithm to the example mis- spelling acress. The first stage of the algorithm proposes candidate corrections by



|<p>function NOISY CHANNEL SPELLING(word x,dict D,lm,editprob) returns correction</p><p>if x 2= D</p><p>candidates, edits All strings at edit distance 1 from xthat are 2 D, and their edit for each c;e in candidates, edits</p><p><a name="_page3_x475.20_y164.71"></a>channel editprob(e)</p><p>prior lm(x)</p><p>score[c] = log channel + log prior</p><p>return argmaxc score[c]</p>|
| - |

finding words that have a similar spelling to the input word. Analysis of spelling

error data has shown that the majority of spelling errors consist of a single-letter

change and so we often make the simplifying assumption that these candidates have

an edit distance of 1 from the error word. To find this list of candidates we’ll use

the minimum edit distance algorithm introduced in Chapter 2, but extended so that

in addition to insertions, deletions, and substitutions, we’ll add a fourth type of edit,

transpositions, in which two letters are swapped. The version of edit distance with LeDamerau-venshtein transposition is called Damerau-Levenshtein edit distance. Applying all such sin-

gle transformations to acress yields the list of candidate words in Fig.[ B.3.](#_page3_x142.20_y483.78)



||||||Transformation|||
| :- | :- | :- | :- | :- | - | :- | :- |
|||||Correct|Error Position|||
|Error||Correction||Letter|Letter (Letter #)|T|ype|
|acress||actress|t||— 2||deletion|
|acress||cress||—|a 0||insertion|
|acress||caress|c|a|ac 0||transposition|
|acress||access|c||r 2||substitution|
|acress||across|o||e 3||substitution|
|acress||acres||—|s 5||insertion|
|<a name="_page3_x142.20_y483.78"></a>acress||acres||—|s 4||insertion|

Figure B.3 Candidate corrections for the misspelling acress and the transformations that would have produced the error (after[ Kernighan et al. (1990](#_page13_x72.42_y499.21))). “—” represents a null letter.

Once we have a set of a candidates, to score each one using Eq.[ B.5 ](#_page2_x215.83_y617.47)requires that we compute the prior and the channel model.

The prior probability of each correction P(w) is the language model probability of the word w in context, which can be computed using any language model, from unigram to trigram or 4-gram. For this example let’s start in the following table by assuming a unigram language model. We computed the language model from the 404,253,213 words in the Corpus of Contemporary English (COCA).



|w|count(w)|p(w)|
| - | - | - |
|actress|9,321|.0000231|
|cress|220|.000000544|
|caress|686|.00000170|
|access|37,038|.0000916|
|across|120,844|.000299|
|acres|12,874|.0000318|

channel model How can we estimate the likelihood P(xjw), also called the channel model or

B.1 • THE NOISY CHANNEL MODEL 7

error model error model? Aperfectmodeloftheprobabilitythatawordwillbemistypedwould

condition on all sorts of factors: who the typist was, whether the typist was left- handed or right-handed, and so on. Luckily, we can get a pretty reasonable estimate of P(xjw) just by looking at local context: the identity of the correct letter itself, the misspelling, and the surrounding letters. For example, the letters m and n are often substituted for each other; this is partly a fact about their identity (these two letters are pronounced similarly and they are next to each other on the keyboard) and partly afactaboutcontext(becausetheyarepronouncedsimilarlyandtheyoccurinsimilar contexts).

A simple model might estimate, for example, p(acressjacross) just using the number of times that the letter e was substituted for the letter o in some large corpus

of errors. To compute the probability for each edit in this way we’ll need a confu- confusionmatrix sion matrix that contains counts of errors. In general, a confusion matrix lists the

number of times one thing was confused with another. Thus for example a substi-

tution matrix will be a square matrix of size 2626 (or more generally jAjjAj, for an alphabet A) that represents the number of times one letter was incorrectly used instead of another. Following[ Kernighan et al. (1990)](#_page13_x72.42_y499.21) we’ll use four confusion

matrices.

del[x;y]: count(xy typed as x) ins[x;y]: count(x typed as xy) sub[x;y]: count(x typed as y) trans[x;y]: count(xy typed as yx)

Note that we’ve conditioned the insertion and deletion probabilities on the previ- ous character; we could instead have chosen to condition on the following character.

Where do we get these confusion matrices? One way is to extract them from lists of misspellings like the following:

additional: addional, additonal

environments: enviornments, enviorments, enviroments preceded: preceeded

...

There are lists available on Wikipedia and from Roger Mitton [(http://www. dcs.bbk.ac.uk/~ROGER/corpora.html) and ](http://www.dcs.bbk.ac.uk/~ROGER/corpora.html)Peter Norvig ([http://norvig. com/ngrams/).](http://norvig.com/ngrams/) Norvig also gives the counts for each single-character edit that can be used to directly create the error model probabilities.

An alternative approach used by[ Kernighan et al. (1990)](#_page13_x72.42_y499.21) is to compute the ma- trices by iteratively using this very spelling error correction algorithm itself. The iterative algorithm firstinitializes the matrices with equal values; thus, any character is equally likely to be deleted, equally likely to be substituted for any other char- acter, etc. Next, the spelling error correction algorithm is run on a set of spelling errors. Given the set of typos paired with their predicted corrections, the confusion matrices can now be recomputed, the spelling algorithm run again, and so on. This iterative algorithm is an instance of the important EM algorithm [(Dempster et al., 1977](#_page13_x72.42_y344.12)), which we discuss in Appendix A.

Once we have the confusion matrices, we can estimate P(xjw) as follows (where


6 i >>>>>>>>>< countdel[x[i xi1 ;1ww]i]i]; if deletion

APPENDIX B • SPELLING CORRECTION AND THE NOISY CHANNEL

w is the ith character of the correct word w) and xi is the ith character of the typo x:

<a name="_page5_x142.20_y121.28"></a>8

\>>

\>

P(xjw) = >>>>>>>>>>>>: inssubcount[[xxi i[;w1w;i iw]1i;]if; ifsubstitution;insertionif transposition (B.6)

count[wi]

trans[wi;wi+ 1]

count[wiwi+ 1]

Using the counts from[ Kernighan et al. (1990)](#_page13_x72.42_y499.21) results in the error model proba- bilities for acress shown in Fig.[ B.4.](#_page5_x142.20_y379.05)



|Candidate||Correct||Error||||
| - | :- | - | :- | - | :- | :- | :- |
|Correction||Letter||Letter||x jw|P(xjw)|
|actress||t||-||c|ct|.000117|
|cress||-||a||a|#|.00000144|
|caress||ca||ac||ac|ca|.00000164|
|access||c||r||r|c|.000000209|
|across||o||e||e|o|.0000093|
|acres||-||s||es|e|.0000321|
|<a name="_page5_x142.20_y379.05"></a>acres||-||s||ss|s|.0000342|

Figure B.4 Channel model for acress; the probabilities are taken from the del[], ins[], sub[], and trans[] confusion matrices as shown in [Kernighan et al. ](#_page13_x72.42_y499.21)([1990).](#_page13_x72.42_y499.21)

Figure[ B.5 ](#_page5_x142.20_y580.06)shows the final probabilities for each of the potential corrections; the unigram prior is multiplied by the likelihood (computed with Eq.[ B.6 ](#_page5_x142.20_y121.28)and the confusion matrices). The finalcolumn shows the product, multiplied by 109 just for readability.



|Candidate Correction|Correct Letter|Error Letterx|jw|P(xjw)|P(w)|109\*P(xjw)P(w)|
| - | :- | :- | - | - | - | - |
|actress t|-|c|c|t|.000117|.0000231|2\.7|
|cress -|a|a||#|.00000144|.000000544|0\.00078|
|caress c|a a|c a|c|ca|.00000164|.00000170|0\.0028|
|access|c r|r||c|.000000209|.0000916|0\.019|
|across|o|e e||o|.0000093|.000299|2\.8|
|acres|- s|e|s|e|.0000321|.0000318|1\.0|
|<a name="_page5_x142.20_y580.06"></a>acres|- s|s|s|s|.0000342|.0000318|1\.0|

Figure B.5 Computation of the ranking for each candidate correction, using the language model shown earlier and the error model from Fig.[ B.4.](#_page5_x142.20_y379.05) The final score is multiplied by 109

for readability.

The computations in Fig.[ B.5 ](#_page5_x142.20_y580.06)show that our implementation of the noisy channel model chooses across as the best correction, and actress as the second most likely word.

Unfortunately, the algorithm was wrong here; the writer’s intention becomes clear from the context: ...was called a “stellar and versatile acress whose com- bination of sass and glamour has defined her... ”. The surrounding words make it clear that actress and not across was the intended word.

B.2 • REAL-WORD SPELLING ERRORS 

For this reason, it is important to use larger language models than unigrams. For example, if we use the Corpus of Contemporary American English to compute bigram probabilities for the words actress and across in their context using add-one smoothing, we get the following probabilities:

P(actressjversatile) = :000021 P(acrossjversatile) = :000021 P(whosejactress) = :0010

P(whosejacross) = :000006

Multiplying these out gives us the language model estimate for the two candi- dates in context:

P(“versatile actress whose”) = :000021:0010 = 21010 10 P(“versatile across whose”) = :000021:000006 = 110 10

Combining the language model with the error model in Fig.[ B.5,](#_page5_x142.20_y580.06) the bigram noisy channel model now chooses the correct word actress.

Evaluating spell correction algorithms is generally done by holding out a train- ing, development and test set from lists of errors like those on the Norvig and Mitton sites mentioned above.

B.2 Real-word spelling errors

The noisy channel approach can also be applied to detect and correct real-word real-worddetectionerror spelling errors, errors that result in an actual word of English. This can happen from

typographical errors (insertion, deletion, transposition) that accidentally produce a

real word (e.g., there for three) or because the writer substituted the wrong spelling

of a homophone or near-homophone (e.g., dessert for desert, or piece for peace). A

number of studies suggest that between 25% and 40% of spelling errors are valid

English words as in the following examples [(Kukich, 1992](#_page13_x72.42_y551.78)):

This used to belong to thewqueen. They are leaving in about fifteenminuetsto go to her house. The design an construction of the system will take more than a year.

Can they lave him my messages?

The study was conducted mainly be John Black.

The noisy channel can deal with real-word errors as well. Let’s begin with a version of the noisy channel model first proposed by[ Mays et al. (1991)](#_page13_x72.42_y604.35) to deal with these real-word spelling errors. Their algorithm takes the input sentence X = fx1;x2;:::;xk;:::;xng, generates a large set of candidate correction sentencesC(X), then picks the sentence with the highest language model probability.

To generate the candidate correction sentences, we start by generating a set of candidate words for each input word xi. The candidates, C(xi), include every En- glish word with a small edit distance from xi. With edit distance 1, a common choice [(Mays et al., 1991](#_page13_x72.42_y604.35)), the candidate set for the real word error thew(a rare word mean- ing‘muscularstrength’)mightbeC(thew)=fthe,thaw,threw,them,thweg. Wethen make the simplifying assumption that every sentence has only one error. Thus the set of candidate sentences C(X) for a sentence X = Only two of thew apples would be:

8  APPENDIX B • SPELLING CORRECTION AND THE NOISY CHANNEL

only two of thew apples oily two of thew apples only too of thew apples only to of thew apples only tao of the apples only two on thew apples only two off thew apples only two of the apples only two of threw apples only two of thew applies only two of thew dapples ...

Each sentence is scored by the noisy channel:

Wˆ = argmaxP(XjW)P(W) (B.7)

W2C(X)

For P(W), we can use the trigram probability of the sentence.

What about the channel model? Since these are real words, we need to consider the possibility that the input word is not an error. Let’s say that the channel proba- bility of writing a word correctly, P(wjw), is a ; we can make different assumptions about exactly what the value of a is in different tasks; perhaps a is .95, assum- ing people write 1 word wrong out of 20, for some tasks, or maybe .99 for others. [Mays et al. (1991)](#_page13_x72.42_y604.35) proposed a simple model: given a typed word x, let the channel model P(xjw) be a when x= w, and then just distribute 1 a evenly over all other candidate corrections C(x):

<a name="_page7_x142.20_y413.20"></a>8

\>>>< 1 a a if x= w

p(xjw) = >>>: jC(x)j if x2 C(x) (B.8)

0 otherwise

Nowwecanreplacetheequaldistributionof1 a overallcorrectionsinEq.[B.8; ](#_page7_x142.20_y413.20)we’llmakethedistributionproportionaltotheeditprobabilityfromthemoresophis- ticated channel model from Eq.[ B.6 ](#_page5_x142.20_y121.28)that used the confusion matrices.

Let’s see an example of this integrated noisy channel model applied to a real word. Suppose we see the string two of thew. The author might have intended to type the real word thew (‘muscular strength’). But thew here could also be a typo for the or some other word. For the purposes of this example let’s consider edit distance 1, and only the following five candidates the, thaw, threw, and thwe (a rare name) and the string as typed, thew. We took the edit probabilities from Norvig’s[ 2009 ](#_page13_x72.42_y687.94)analysis of this example. For the language model probabilities, we used a Stupid Backoff model (Section ??) trained on the Google n-grams:

P(thejtwo of) = 0.476012 P(thewjtwo of) = 9.95051 10 8 P(thawjtwo of) = 2.09267 10 7 P(threwjtwo of) = 8.9064 10 7

P(themjtwo of) = 0.00144488 P(thwejtwo of) = 5.18681 10 9

Here we’ve just computed probabilities for the single phrase two of thew, but the model applies to entire sentences; so if the example in context was two of thew

B.3 • NOISY CHANNEL MODEL: THE STATE OF THE ART 13

people, we’d need to also multiply in probabilities for P(peoplejof the), P(peoplejof thew), P(peoplejof threw), and so on.

Following[ Norvig (2009](#_page13_x72.42_y687.94)), we assume that the probability of a word being a typo in this task is .05, meaning that a = P(wjw) is .95. Fig.[ B.6 ](#_page8_x160.20_y230.48)shows the computation.



|x|w|xjw|P(xjw)|<p>P(wjw ;w )</p><p>i 2 i 1</p>|<p>108P(xjw)P(wjwi 2;w )</p><p>i 1</p>|
| - | - | - | - | - | - |
|thew thew thew thew thew|the thew thaw threw thwe|<p>ewje</p><p>eja hjhr ewjwe</p>|0\.000007 a =0.95 0.001 0.000008 <a name="_page8_x160.20_y230.48"></a>0.000003|<p>0\.48</p><p>9\.95 10 8</p><p>2\.1 10 7</p><p>8\.9 10 7</p><p>5\.2 10 9</p>|<p>333</p><p>9\.45 0.0209 0.000713 0.00000156</p>|

Figure B.6 The noisy channel model on 5 possible candidates for thew, with a Stupid Backoff trigram language model computed from the Google n-gram corpus and the error model from[ Norvig (2009](#_page13_x72.42_y687.94)).

For the error phrase two of thew, the model correctly picks the as the correction. But note that a lower error rate might change things; in a task where the probability of an error is low enough (a is very high), the model might instead decide that the word thewwas what the writer intended.

B.3 Noisy Channel Model: The State of the Art

State of the art implementations of noisy channel spelling correction make a number of extensions to the simple models we presented above.

First, rather than make the assumption that the input sentence has only a sin- gle error, modern systems go through the input one word at a time, using the noisy channel to make a decision for that word. But if we just run the basic noisy chan- nel system described above on each word, it is prone to overcorrecting, replacing correct but rare words (for example names) with more frequent words [(Whitelaw et al. 2009,](#_page13_x278.29_y303.93)[ Wilcox-O’Hearn 2014](#_page13_x278.29_y335.31)). Modern algorithms therefore need to augment the noisy channel with methods for detecting whether or not a real word should ac- tually be corrected. For example state of the art systems like Google’s [(Whitelaw et al., 2009)](#_page13_x278.29_y303.93) use a blacklist, forbidding certain tokens (like numbers, punctuation, and single letter words) from being changed. Such systems are also more cautious in deciding whether to trust a candidate correction. Instead of just choosing a candi- date correction if it has a higher probability P(wjx) than the word itself, these more careful systems choose to suggest a correction w over keeping the non-correction x only if the difference in probabilities is sufficiently great. The best correction w is chosen only if:

logP(wjx) logP(xjx) > q

autocorrect Depending on the specific application, spell-checkers may decide to autocorrect

(automatically change a spelling to a hypothesized correction) or merely to flag the error and offer suggestions. This decision is often made by another classifierwhich decides whether the best candidate is good enough, using features such as the dif- ference in log probabilities between the candidates (we’ll introduce algorithms for classificationin the next chapter).

Modern systems also use much larger dictionaries than early systems. [Ahmad and Kondrak (2005)](#_page13_x72.42_y109.65) found that a 100,000 word UNIX dictionary only contained

73% of the word types in their corpus of web queries, missing words like pics, mul- tiplayer, google, xbox, clipart, and mallorca. For this reason modern systems often use much larger dictionaries automatically derived from very large lists of unigrams like the Google n-gram corpus.[ Whitelaw et al. (2009](#_page13_x278.29_y303.93)), for example, used the most frequently occurring ten millionword typesina largesample ofwebpages. Because this list will include lots of misspellings, their system requires a more sophisticated error model. The fact that words are generally more frequent than their misspellings can be used in candidate suggestion, by building a set of words and spelling vari- ations that have similar contexts, sorting by frequency, treating the most frequent variant as the source, and learning an error model from the difference, whether from web text [(Whitelaw et al., 2009)](#_page13_x278.29_y303.93) or from query logs [(Cucerzan and Brill, 2004](#_page13_x72.42_y260.53)). Words can also be automatically added to the dictionary when a user rejects a cor- rection, and systems running on phones can automatically add words from the user’s address book or calendar.

We can also improve the performance of the noisy channel model by changing how the prior and the likelihood are combined. In the standard model they are just multiplied together. But often these probabilities are not commensurate; the lan- guage model or the channel model might have very different ranges. Alternatively for some task or dataset we might have reason to trust one of the two models more. Therefore we use a weighted combination, by raising one of the factors to a power l :

wˆ = argmaxP(xjw)P(w)l (B.9)

w2V

or in log space:

wˆ = argmaxlogP(xjw)+ l logP(w) (B.10)

w2V

We then tune the parameter l on a development test set.

Finally, if our goal is to do real-word spelling correction only for specific con- confusion sets fusion sets like peace/piece, affect/effect, weather/whether, or even grammar cor- rection examples like among/between, we can train supervised classifiersto draw on

many features of the context and make a choice between the two candidates. Such classifiers can achieve very high accuracy for these specific sets, especially when drawing on large-scale features from web statistics [(Golding and Roth 1999,](#_page13_x72.42_y384.60)[ Lapata](#_page13_x72.42_y573.33)

[and Keller 2004,](#_page13_x72.42_y573.33)[ Bergsma et al. 2009,](#_page13_x72.42_y143.30)[ Bergsma et al. 2010](#_page13_x72.42_y164.85)).

B.3.1 Improved Edit Models: Partitions and Pronunciation

Other recent research has focused on improving the channel model P(tjc). One important extension is the ability to compute probabilities for multiple-letter trans- formations. For example[ Brill and Moore (2000)](#_page13_x72.42_y207.96) propose a channel model that (informally) models an error as being generated by a typist first choosing a word, then choosing a partition of the letters of that word, and then typing each partition, possibly erroneously. For example, imagine a person chooses the word physical, then chooses the partition ph y s i c al. She would then generate each parti- tion, possibly with errors. For example the probability that she would generate the string fisikle with partition f i s i k le would be p(fjph)p(ijy)p(sjs) p(iji)p(kjk)p(lejal). Unlike the Damerau-Levenshtein edit distance, the Brill- Moore channel model can thus model edit probabilities like P(fjph) or P(lejal), or

B.3 • NOISY CHANNEL MODEL: THE STATE OF THE ART 

the high likelihood of P(entjant). Furthermore, each edit is conditioned on where it is in the word (beginning, middle, end) so instead of P(fjph) the model actually estimates P(fjph;beginning).

More formally, let R be a partition of the typo string x into adjacent (possibly empty) substrings, and T be a partition of the candidate string. [Brill and Moore (2000)](#_page13_x72.42_y207.96) then approximates the total likelihood P(xjw) (e.g., P(fisiklejphysical))

by the probability of the single best partition:

XjRj

P(xjw)  max P(TijRi;position) (B.11)

R;Ts:t:jTj= jRj

i=1

The probability of each transform P(TijRi) can be learned from a training set of triples of an error, the correct string, and the number of times it occurs. For example given a training pair akgsual/actual, standard minimum edit distance is used to produce an alignment:

a c t u a l

a k g s u a l![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.008.png)![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.009.png)![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.010.png)![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.011.png)![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.012.png)![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.013.png)

This alignment corresponds to the sequence of edit operations:

a!a, c!k, !g t!s, u!u, a!a, l!l

Each nonmatch substitution is then expanded to incorporate up to N additional edits; For N=2, we would expand c!k to:

ac!ak c!cg ac!akg ct!kgs

Each of these multiple edits then gets a fractional count, and the probability for each edit a ! b is then estimated from counts in the training corpus of triples as

count(a !b)

count(a )~~ .

Another research direction in channel models is the use of pronunciation in ad- dition to spelling. Pronunciation is an important feature in some non-noisy-channel

aspell algorithms for spell correction like the GNU aspell algorithm [(Atkinson, 2011](#_page13_x72.42_y131.21)), which makes use of the metaphone pronunciation of a word [(Philips, 1990](#_page13_x278.29_y153.49)). Meta-

phone is a series of rules that map a word to a normalized representation of its

pronunciation. Some example rules:

- “Drop duplicate adjacent letters, except for C.”
- “If the word begins with ‘KN’, ‘GN’, ‘PN’, ‘AE’, ‘WR’, drop the firstletter.”
- “Drop ‘B’ if after ‘M’ and if it is at the end of the word”

Aspellworkssimilarlytothechannelcomponentofthenoisychannelmodel,finding all words in the dictionary whose pronunciation string is a short edit distance (1 or 2 pronunciation letters) from the typo, and then scoring this list of candidates by a metric that combines two edit distances: the pronunciation edit distance and the weighted letter edit distance.

Pronunciationcanalsobeincorporateddirectlythenoisychannelmodel. Forex- ample the[ Toutanova and Moore (2002)](#_page13_x278.29_y238.17) model, like aspell, interpolates two channel

12  APPENDIX B • SPELLING CORRECTION AND THE NOISY CHANNEL



|<p>function SOUNDEX(name) returns soundex form</p><p>1. Keep the firstletter of name</p><p>2. Drop all occurrences of non-initial a, e, h, i, o, u, w, y.</p><p>3. Replace the remaining letters with the following numbers:</p><p>b, f, p, v ! 1</p><p>c, g, j, k, q, s, x, z ! 2</p><p>d, t ! 3</p><p><a name="_page11_x475.20_y198.63"></a>l ! 4</p><p>m, n ! 5</p><p>r ! 6</p><p>4. Replace any sequences of identical numbers, only if they derive from two or more letters that were adjacent in the original name, with a single number (e.g., 666 ! 6). 5.Converttotheform Letter Digit Digit Digit bydroppingdigitspastthethird (if necessary) or padding with trailing zeros (if necessary).</p>|
| - |

models, one based on spelling and one based on pronunciation. The pronunciation letter-to-sound model is based on using letter-to-sound models to translate each input word and phones each dictionary word into a sequences of phones representing the pronunciation of

the word. For example actress and aktress would both map to the phone string

ae k t r ix s. See Chapter 26 on the task of letter-to-sound or grapheme-to- phoneme.

Some additional string distance functions have been proposed for dealing specif- deduplication ically with names. These are mainly used for the task of deduplication (deciding if two names in a census list or other namelist are the same) rather than spell-checking.

The Soundex algorithm [(Knuth 1973,](#_page13_x72.42_y530.22)[ Odell and Russell 1918/1922)](#_page13_x278.29_y109.65) is an older methodusedoriginallyforcensusrecordsforrepresentingpeople’snames. Ithasthe advantage that versions of the names that are slightly misspelled will still have the same representation as correctly spelled names. (e.g., Jurafsky, Jarofsky, Jarovsky,

and Jarovski all map to J612). The algorithm is shown in Fig.[ B.7.](#_page11_x475.20_y198.63)

Jaro-Winkler Instead of Soundex, more recent work uses Jaro-Winkler distance, which is

an edit distance algorithm designed for names that allows characters to be moved longer distances in longer names, and also gives a higher similarity to strings that have identical initial characters [(Winkler, 2006](#_page13_x278.29_y407.54)).

Bibliographical and Historical Notes

Algorithms for spelling error detection and correction have existed since at least [Blair (1960](#_page13_x72.42_y186.40)). Most early algorithms were based on similarity keys like the Soundex algorithm [(Odell and Russell 1918/1922,](#_page13_x278.29_y109.65)[ Knuth 1973](#_page13_x72.42_y530.22)). [Damerau (1964)](#_page13_x72.42_y291.55) gave a dictionary-basedalgorithmforerrordetection; mosterror-detectionalgorithmssince then have been based on dictionaries. Early research [(Peterson, 1986)](#_page13_x278.29_y131.57) had suggested that spelling dictionaries might need to be kept small because large dictionaries con- tain very rare words (wont, veery) that resemble misspellings of other words, but [Damerau and Mays (1989)](#_page13_x72.42_y313.10) found that in practice larger dictionaries proved more helpful. [Damerau (1964)](#_page13_x72.42_y291.55) also gave a correction algorithm that worked for single errors.

The idea of modeling language transmission as a Markov source passed through


EXERCISES 13

a noisy channel model was developed very early on by Claude[ Shannon (1948](#_page13_x278.29_y206.79)). The idea of combining a prior and a likelihood to deal with the noisy channel was developed at IBM Research by[ Raviv (1967](#_page13_x278.29_y175.41)), for the similar task of optical char- acter recognition (OCR). While earlier spell-checkers like [Kashyap and Oommen (1983)](#_page13_x72.42_y468.19) had used likelihood-based models of edit distance, the idea of combining a prior and a likelihood seems not to have been applied to the spelling correction task until researchers at AT&T Bell Laboratories [(Kernighan et al. 1990,](#_page13_x72.42_y499.21)[ Church and Gale 1991)](#_page13_x72.42_y229.51) and IBM Watson Research [(Mays et al., 1991)](#_page13_x72.42_y604.35) roughly simultaneously proposed noisy channel spelling correction. Much later, the[ Mays et al. (1991)](#_page13_x72.42_y604.35) algo- rithm was reimplemented and tested on standard datasets by[ Wilcox-O’Hearn et al. (2008](#_page13_x278.29_y366.69)), who showed its high performance.

Most algorithms since[ Wagner and Fischer (1974)](#_page13_x278.29_y282.01) have relied on dynamic pro- gramming.

Recent focus has been on using the web both for language models and for train- ing the error model, and on incorporating additional features in spelling, like the pronunciation models described earlier, or other information like parses or semantic relatedness [(Jones and Martin 1997,](#_page13_x72.42_y446.64)[ Hirst and Budanitsky 2005](#_page13_x72.42_y415.62)).

See[ Mitton (1987)](#_page13_x72.42_y635.37) for a survey of human spelling errors, and[ Kukich (1992) ](#_page13_x72.42_y551.78)for an early survey of spelling error detection and correction. [Norvig (2007)](#_page13_x72.42_y666.39) gives a nice explanation and a Python implementation of the noisy channel model, with more details and an efficientalgorithm presented in[ Norvig (2009](#_page13_x72.42_y687.94)).

Exercises

B.1 Suppose we want to apply add-one smoothing to the likelihood term (channel

model) P(xjw) of a noisy channel model of spelling. For simplicity, pretend that the only possible operation is deletion. The MLE estimate for deletion

is given in Eq.[ B.6,](#_page5_x142.20_y121.28) which is P(xjw) = countdel[xi( x1;wwi]) . What is the estimate for P(xjw) if we use add-one smoothing on the deletioni 1 i edit model? Assume the

only characters we use are lower case a-z, that there are V word types in our corpus, and N total characters, not counting spaces.

14 Appendix B • Spelling Correction and the Noisy Channel![](Aspose.Words.37ef1e78-b924-49f9-9d1c-d5eaa3168b65.014.png)


<a name="_page13_x72.42_y109.65"></a>Ahmad, F. and G. Kondrak. 2005. Learning a spelling error

<a name="_page13_x278.29_y109.65"></a>model from search query logs. EMNLP.

<a name="_page13_x72.42_y131.21"></a>Atkinson, K. 2011.[ Gnu aspell.](aspell.net)

<a name="_page13_x278.29_y131.57"></a>Bergsma,S., D.Lin, andR.Goebel.2009. Web-scalen-gram

models for lexical disambiguation. IJCAI.

<a name="_page13_x278.29_y153.49"></a>Bergsma, S., E. Pitler, and D. Lin. 2010. Creating robust supervised classifiersvia web-scale n-gram data. ACL.

<a name="_page13_x278.29_y175.41"></a>Blair, C. R. 1960. A program for correcting spelling errors.

Information and Control, 3:60–67.

Brill, E. and R. C. Moore. 2000. An improved error model

for noisy channel spelling correction. ACL.

<a name="_page13_x72.42_y229.51"></a>Church, K. W. and W. A. Gale. 1991. Probability scoring for

<a name="_page13_x278.29_y238.17"></a>spelling correction. Statistics and Computing, 1(2):93– 103.

Cucerzan, S. and E. Brill. 2004. Spelling correction as an

iterative process that exploits the collective knowledge of web users. EMNLP, volume 4.

<a name="_page13_x278.29_y282.01"></a>Damerau, F.J.1964. Atechniqueforcomputerdetectionand

correction of spelling errors. CACM, 7(3):171–176.

<a name="_page13_x278.29_y303.93"></a>Damerau, F. J. and E. Mays. 1989. An examination of un-

detected typing errors. Information Processing and Man- agement, 25(6):659–664.

<a name="_page13_x278.29_y335.31"></a>Dempster, A. P., N. M. Laird, and D. B. Rubin. 1977. Max-

imum likelihood from incomplete data via the EM algo- rithm. Journal of the Royal Statistical Society, 39(1):1–<a name="_page13_x278.29_y366.69"></a>21.

Golding, A. R. and D. Roth. 1999. A Winnow based ap-

proach to context-sensitive spelling correction. Machine Learning, 34(1-3):107–130.

<a name="_page13_x278.29_y407.54"></a>Hirst, G. and A. Budanitsky. 2005. Correcting real-word

spelling errors by restoring lexical cohesion. Natural Language Engineering, 11:87–111.

<a name="_page13_x72.42_y446.64"></a>Jones, M. P. and J. H. Martin. 1997. Contextual spelling cor-

rection using latent semantic analysis. ANLP.

<a name="_page13_x72.42_y468.19"></a>Kashyap, R. L. and B. J. Oommen. 1983. Spelling correction

using probabilistic methods. Pattern Recognition Letters, 2:147–154.

<a name="_page13_x72.42_y499.21"></a>Kernighan, M. D., K. W. Church, and W. A. Gale. 1990.

A spelling correction program base on a noisy channel model. COLING, volume II.

<a name="_page13_x72.42_y530.22"></a>Knuth, D. E. 1973. Sorting and Searching: The Art of Com-

puter Programming Volume 3. Addison-Wesley.

<a name="_page13_x72.42_y551.78"></a>Kukich, K. 1992. Techniques for automatically correcting words in text. ACM Computing Surveys, 24(4):377–439.

<a name="_page13_x72.42_y573.33"></a>Lapata, M. and F. Keller. 2004. The web as a baseline: Eval-

uating the performance of unsupervised web-based mod- els for a range of NLP tasks. HLT-NAACL.

<a name="_page13_x72.42_y604.35"></a>Mays, E., F. J. Damerau, and R. L. Mercer. 1991. Context

based spelling correction. Information Processing and Management, 27(5):517–522.

<a name="_page13_x72.42_y635.37"></a>Mitton, R. 1987. Spelling checkers, spelling correctors and the misspellings of poor spellers. Information processing & management, 23(5):495–505.

<a name="_page13_x72.42_y666.39"></a>Norvig, P. 2007. How to write a spelling corrector.[ http:](http://www.norvig.com/spell-correct.html)

[//www.norvig.com/spell-correct.html.](http://www.norvig.com/spell-correct.html)

<a name="_page13_x72.42_y687.94"></a>Norvig, P. 2009. Natural language corpus data. In Toby

Segaran and Jeff Hammerbacher, editors, Beautiful data: the stories behind elegant data solutions. O’Reilly.

Odell, M. K. and R. C. Russell. 1918/1922. U.S. Patents 1261167 (1918), 1435663 (1922). Cited in Knuth (1973).

Peterson, J. L. 1986. A note on undetected typing errors.

<a name="_page13_x72.42_y143.30"></a>CACM, 29(7):633–637.

Philips, L. 1990. Hanging on the metaphone. Computer

<a name="_page13_x72.42_y164.85"></a>Language, 7(12).

Raviv, J. 1967. Decision making in Markov chains applied

<a name="_page13_x72.42_y186.40"></a>to the problem of pattern recognition. IEEE Transactions on Information Theory, 13(4):536–551.

<a name="_page13_x72.42_y207.96"></a><a name="_page13_x278.29_y206.79"></a>Shannon, C. E. 1948. A mathematical theory of commu-

nication. Bell System Technical Journal, 27(3):379–423. Continued in the following volume.

Toutanova, K. and R. C. Moore. 2002. Pronunciation mod-

eling for improved spelling correction. ACL.

<a name="_page13_x72.42_y260.53"></a>Veblen, T. 1899. Theory of the Leisure Class. Macmillan,

New York.

Wagner, R. A. and M. J. Fischer. 1974. The string-to-string <a name="_page13_x72.42_y291.55"></a>correction problem. Journal of the ACM, 21:168–173.

<a name="_page13_x72.42_y313.10"></a>Whitelaw, C., B. Hutchinson, G. Y. Chung, and G. El-

lis. 2009. Using the web for language independent spellchecking and autocorrection. EMNLP.

<a name="_page13_x72.42_y344.12"></a>Wilcox-O’Hearn, L. A. 2014. Detection is the central prob-

lem in real-word spelling correction. [http://arxiv. org/abs/1408.3153.](http://arxiv.org/abs/1408.3153)

Wilcox-O’Hearn, L. A., G. Hirst, and A. Budanitsky. 2008.

<a name="_page13_x72.42_y384.60"></a>Real-word spelling correction with trigrams: A recon- sideration of the Mays, Damerau, and Mercer model. CICLing-2008.

<a name="_page13_x72.42_y415.62"></a>Winkler, W.E.2006. Overviewofrecordlinkageandcurrent

research directions. Technical report, Statistical Research Division, U.S. Census Bureau.
