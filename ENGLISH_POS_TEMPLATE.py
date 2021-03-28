
"""
# IMPORTING MODULES
"""
print('\n')
print('\n')
# HLPER FUNCTION: Get Time Now:
import os
from datetime import datetime
def time_now():
    '''Get Current Time'''
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    return now

##_comment_here
print('Please enter name of the pickle file containing the text to be processed.')
print('The file must be a pandas DataFrame; the text column must have TEXT as its name.')
pickle_text = input("ENTER FILE NAME: ") # WORK ON THIS FIRST [TODO]
pickle_text = str(pickle_text)

print('Please enter where you want to save output files:')
output_dir = input("ENTER FOLDER NAME: ")

if pickle_text in os.listdir():
    print('OK')
elif os.path.exists(pickle_text):
    print('OK')
else:
    print('WARNING: The file path you entered is not valid!')


print('\n')
############
print('Starting...')
start = time_now()
############

##_comment_here
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
from time import sleep
import pandas as pd
import regex as re
from itertools import chain
from collections import Counter
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib
import matplotlib.pyplot as plt

##_comment_here
import spacy
nlp = spacy.load("en_core_web_sm")

##_comment_here
akbar_colors = ['#009933',
 '#006699',
 '#333333',
 '#669999',
 '#990066',
 '#996666',
 '#cc3333',
 '#cc6633',
 '#cc6666',
 '#ff6633',
 '#990000',
 '#003366',
 '#339966',
 '#cc3399',
 '#3333ff']
my_cmap = matplotlib.colors.ListedColormap(akbar_colors, name='my_colormap_name', N=45)


##_comment_here
df01 = pd.read_pickle(pickle_text)

##_comment_here
df01['LENGTH'] = df01['TEXT'].apply(lambda x: len(x.split()))
total_words_count = df01['LENGTH'].sum()

##_comment_here
print('Analyzing text using spaCy; This might take few minutes... be patient!')
df01['NLP'] =  df01['TEXT'].apply(lambda x: nlp(x))

##_comment_here
df01['Noun_Phrases'.upper()] = df01['NLP'].apply(lambda x: [chunk.text for chunk in x.noun_chunks])

##_comment_here
df01['Verbs'] = df01['NLP'].apply(lambda x: [token.lemma_ for token in x if token.pos_ == "VERB"])
df01['ADJ'] = df01['NLP'].apply(lambda x: [token.lemma_ for token in x if token.pos_ == "ADJ"])
df01['NOUN'] = df01['NLP'].apply(lambda x: [token.lemma_ for token in x if token.pos_ == "NOUN"])
df01['PROPN'] = df01['NLP'].apply(lambda x: [token.lemma_ for token in x if token.pos_ == "PROPN"])
df01['ADV'] = df01['NLP'].apply(lambda x: [token.lemma_ for token in x if token.pos_ == "ADV"])

##_comment_here
col = 'TEXT	LENGTH		NOUN_PHRASES	Verbs	ADJ	NOUN	PROPN	ADV'
col = col.split()
df01 = df01[col]

##_comment_here


##_comment_here
"""
# Titling Function for the Noun Phrases
"""

##_comment_here
def proper_case(text):
    '''Given a string, convert its words to the Title form, unless the word is ACRONYM!'''
    pc = " ".join([i.title() if not i.isupper() else i for i in text.split()])
    return pc

##_comment_here
stop_words = "how very nbsp will years year be other only often first how him rather another but he have many three near yours won us to we'll usually ours haven't their couldn't together thing please with through an is been ain within since vi one do much your she's after all iii is't self for could away done thus always some also doing will where and does iv aren wasn than well about a truth till even mrs just get are therefore little didn't yet until me who won't they almost far doesn't in we because third else once enough himself father's such be from while should things when too weren't thoughts speed you've not hadn't less on between without was ii why them here's i ha never v that's yourself each last his being say age any shouldn't if make shall had themselves nor there which herself said her though half it's i'll these viii needn't by so out same were didn am ll myself my give hour now shouldn she you'd way ve vii still keep take no here mustn't cannot indeed our as you'll having under couldn gone you're can yes at theirs i' before long let's whose hers the two nothing few may over whom what wish isn't might des there's again ix mightn't should've hadn given wrong come yourselves shan old wasn't own he's sit this its thousand seen that'll o must what's hasn enter very alone below wouldn aren't x tell it mine love more during don't name those wouldn't hasn't others has every forth then itself further against would into both none mightn did most ourselves or you back ever that"
stop_words = stop_words.split()
stop_words = set(stop_words)

##_comment_here
print(f'English Stopwords Count: {len(stop_words)}')

print('\n')
print('Extracting Noun-Phrases / Terms:')
##_comment_here
np_list = list(df01['NOUN_PHRASES'])

##_comment_here
np_list = list(chain(*np_list))

##_comment_here
np_list = [proper_case(i) for i in np_list]

##_comment_here
noun_phrases_freq = Counter(np_list)

##_comment_here
noun_phrases_freq  = dict(noun_phrases_freq)

##_comment_here
df_phrases = pd.DataFrame.from_dict(noun_phrases_freq, orient='index').reset_index()

##_comment_here
df_phrases = df_phrases.rename(columns={'index':'Phrase', 0:'Freq'})

##_comment_here
df_phrases = df_phrases.sort_values('Freq', ascending=False)

##_comment_here
"""
# Get rid of stopwords
"""

##_comment_here
df_phrases['Phrase_sw'] = df_phrases['Phrase'].apply(lambda x: " ".join([i.strip() if i.lower() not in stop_words else "" for i in x.split()]))

##_comment_here
df_phrases['Length'] = df_phrases['Phrase_sw'].apply(lambda x: len(x.split()))
df_phrases = df_phrases[df_phrases['Length']>1]

##_comment_here
df_phrases =  df_phrases['Freq	Phrase_sw'.split()]

##_comment_here
df_phrases['Phrase_sw_new'] = df_phrases['Phrase_sw'].apply(lambda x: x.title())

##_comment_here
df_phrases = df_phrases.drop_duplicates(['Phrase_sw_new'])
df_phrases = df_phrases.reset_index(drop=True)

##_comment_here
df_phrases = df_phrases[df_phrases['Freq']>2]
df_phrases = df_phrases.reset_index(drop=True)

##_comment_here
df_phrases = df_phrases['Phrase_sw_new Freq'.split()]
df_phrases = df_phrases.rename(columns={'Phrase_sw_new':'TERM', 'Freq':'FREQ'})

##_comment_here
terms_dict = df_phrases.head(1000)

##_comment_here
terms_dict  = dict(df_phrases.values.tolist())


print('Creating Noun-Phrases / Terms Wordcloud...')
##_comment_here
wordcloud_terms = WordCloud(width=1920*2, height=1080*2, background_color="#F4ECF7", colormap=my_cmap, font_path='./font/Roboto-Regular.ttf').generate_from_frequencies(terms_dict)
wordcloud_terms.to_file(f'./{output_dir}/TERMS.png')

##_comment_here
print('Outputing Terms / Noun-Phrases to xlsx file:')
df_phrases.to_excel(f'./{output_dir}/TERMS.xlsx', encoding='utf-8', index=False)

print('\n')
##_comment_here


##_comment_here
print('Extracting Verbs:')
verbs_list = list (df01['Verbs'])

##_comment_here
verbs_list = list(chain(*verbs_list))

##_comment_here
verbs_list = [i for i in verbs_list if i.lower() not in stop_words]

##_comment_here
verb_freq = Counter(verbs_list)

##_comment_here
verb_freq  = dict(verb_freq)

##_comment_here
df_verbs = pd.DataFrame.from_dict(verb_freq, orient='index').reset_index()

##_comment_here
df_verbs = df_verbs.rename(columns={'index':'Verb', 0:'Freq'})

##_comment_here
df_verbs = df_verbs.sort_values('Freq', ascending=False).reset_index(drop=True)

##_comment_here
df_verbs = df_verbs[df_verbs['Freq']>2]

##_comment_here
df_verbs = df_verbs[df_verbs['Verb'].apply(lambda x: x.isalpha())].reset_index(drop=True)

##_comment_here
print('Outputing Verbs to xlsx file:')
df_verbs.to_excel(f'./{output_dir}/VERBS.xlsx', encoding='utf-8', index=False)

##_comment_here
verb_dict = {k:v for k,v in zip(df_verbs['Verb'], df_verbs['Freq'])}

##_comment_here
print('Creating Verbs Wordcloud....')
wordcloud_verbs = WordCloud(width=1920*2, height=1080*2, background_color="#F5EEF8", colormap=my_cmap, font_path='font/Roboto-Regular.ttf').generate_from_frequencies(verb_dict)

##_comment_here
wordcloud_verbs.to_file(f'./{output_dir}/VERBS.png')


print('\n')
##_comment_here
print('Extracting Nouns:')
noun_list = list (df01['NOUN'])

##_comment_here
noun_list = list(chain(*noun_list))

##_comment_here
noun_list = [i for i in noun_list if i.lower() not in stop_words]

##_comment_here
noun_freq = Counter(noun_list)

##_comment_here
noun_freq  = dict(noun_freq)

##_comment_here
df_noun = pd.DataFrame.from_dict(noun_freq, orient='index').reset_index()

##_comment_here
df_noun = df_noun.rename(columns={'index':'Noun', 0:'Freq'})

##_comment_here
df_noun = df_noun.sort_values('Freq', ascending=False).reset_index(drop=True)

##_comment_here
df_noun = df_noun[df_noun['Freq']>2]

##_comment_here
print('Outputing Nouns to xlsx file:')
df_noun.to_excel(f'./{output_dir}/NOUNS.xlsx', encoding='utf-8', index=False)

##_comment_here
noun_dict = {k:v for k,v in zip(df_noun['Noun'] , df_noun['Freq'])}

##_comment_here
noun_dict = {k:v for k,v in noun_dict.items() if k.isalpha()}

##_comment_here
print('Creating Nouns Wordcloud....')
wordcloud_noun = WordCloud(width=1920*2, height=1080*2, background_color="#E8F8F5", colormap=my_cmap, font_path='font/Roboto-Regular.ttf').generate_from_frequencies(noun_dict)

##_comment_here
wordcloud_noun.to_file(f'./{output_dir}/NOUN.png')

print('\n')

##_comment_here
print('Extracting Proper-Nouns:')
pnoun_list = list (df01['PROPN'])

##_comment_here
pnoun_list = list(chain(*pnoun_list))

##_comment_here
pnoun_list = [i for i in pnoun_list if i.lower() not in stop_words]

##_comment_here
pnoun_freq = Counter(pnoun_list)

##_comment_here
pnoun_freq  = dict(pnoun_freq)

##_comment_here
df_pnoun = pd.DataFrame.from_dict(pnoun_freq, orient='index').reset_index()

##_comment_here
df_pnoun = df_pnoun.rename(columns={'index':'Proper_Noun', 0:'Freq'})

##_comment_here
df_pnoun = df_pnoun.sort_values('Freq', ascending=False).reset_index().drop(columns=['index'])

##_comment_here
df_pnoun = df_pnoun[df_pnoun['Freq']>2]

##_comment_here
df_pnoun = df_pnoun[df_pnoun['Proper_Noun'].apply(lambda x: x not in [',', '.', '_', '×', 'Q', 'et', 'al', '=', '|', '\\', '#'])]
df_pnoun['GROUP'] = df_pnoun['Proper_Noun'].apply(lambda x: x.lower())
df_pnoun = df_pnoun.groupby('GROUP').agg({'Proper_Noun': 'first', 'Freq':'sum'}).reset_index()
df_pnoun = df_pnoun.sort_values(['Freq'], ascending=False).reset_index(drop=True)
df_pnoun['Proper_Noun'] = df_pnoun['Proper_Noun'].apply(lambda x: x.title() if x.islower() else x)

##_comment_here
print('Outputing Proper-Nouns to xlsx file:')
df_pnoun.to_excel(f'./{output_dir}/PROPER_NOUNS.xlsx', encoding='utf-8', index=False)

##_comment_here
pnoun_dict = {k:v for k,v in zip(df_pnoun['Proper_Noun'] , df_pnoun['Freq'])}

##_comment_here
pnoun_dict = {k:v for k,v in pnoun_dict.items() if k.isalpha()}

##_comment_here
pnoun_dict

##_comment_here
print('Creating Proper-Nouns Wordcloud....')
wordcloud_pnoun = WordCloud( width=1920*2, height=1080*2, background_color="#F9EBEA", colormap=my_cmap, font_path = 'font/Roboto-Regular.ttf').generate_from_frequencies(pnoun_dict)
wordcloud_pnoun.to_file(f'./{output_dir}/PROPER_NOUNS.png')

print('\n')

##_comment_here


##_comment_here
print('Extracting Adjectives:')
adj_list = list (df01['ADJ'])

##_comment_here
adj_list = list(chain(*adj_list))

##_comment_here
adj_list = [i for i in adj_list if i.lower() not in stop_words]

##_comment_here
adj_freq = Counter(adj_list)

##_comment_here
adj_freq  = dict(adj_freq)

##_comment_here
df_adj = pd.DataFrame.from_dict(adj_freq, orient='index').reset_index()

##_comment_here
df_adj = df_adj.rename(columns={'index':'Adjective', 0:'Freq'})

##_comment_here
df_adj = df_adj.sort_values('Freq', ascending=False).reset_index().drop(columns=['index'])

##_comment_here
df_adj = df_adj[df_adj['Freq']>2]

##_comment_here
df_adj = df_adj[df_adj['Adjective'].apply(lambda x: x not in [',', '.', '_', '×', 'Q', 'et', 'al', '='])]

##_comment_here
print('Outputing Adjectives to xlsx file:')
df_adj.to_excel(f'./{output_dir}/ADJECTIVES.xlsx', encoding='utf-8', index=False)

##_comment_here
adjective_dict = {k:v for k,v in zip(df_adj.Adjective , df_adj.Freq )}

##_comment_here
adjective_dict = {k:v for k,v in adjective_dict.items() if k.isalpha()}

##_comment_here
print('Creating Adjectives Wordcloud....')
wordcloud_adj = WordCloud( width=1920*2, height=1080*2, background_color="#EBF5FB", colormap=my_cmap, font_path='font/Roboto-Regular.ttf').generate_from_frequencies(adjective_dict)

##_comment_here
wordcloud_adj.to_file(f'./{output_dir}/ADJECTIVES.png')

print('\n')

##_comment_here
print('Extracting Adverbs:')
adv_list = list (df01['ADV'])

##_comment_here
adv_list = list(chain(*adv_list))

##_comment_here
adv_list = [i for i in adv_list if i.lower() not in stop_words]

##_comment_here
adv_freq = Counter(adv_list)

##_comment_here
adv_freq  = dict(adv_freq)

##_comment_here
df_adv = pd.DataFrame.from_dict(adv_freq, orient='index').reset_index()

##_comment_here
df_adv = df_adv.rename(columns={'index':'Adverb', 0:'Freq'})

##_comment_here
df_adv = df_adv.sort_values('Freq', ascending=False).reset_index().drop(columns=['index'])

##_comment_here
df_adv = df_adv[df_adv['Freq']>2]

##_comment_here
df_adv = df_adv[df_adv['Adverb'].apply(lambda x: x not in [',', '.', '_', '×', 'Q', 'et', 'al', '='])]

##_comment_here
print('Outputing Adverbs to xlsx file:')
df_adv.to_excel(f'./{output_dir}/ADVERBS.xlsx', encoding='utf-8', index=False)

##_comment_here
adverb_dict = {k:v for k,v in zip(df_adv['Adverb'] , df_adv['Freq'])}

##_comment_here
adverb_dict = {k:v for k,v in adverb_dict.items() if k.isalpha()}

##_comment_here
adverb_dict

##_comment_here
print('Creating Adjectives Wordcloud....')
wordcloud_adv = WordCloud( width=1920*2, height=1080*2, background_color="#EBF5FB", colormap=my_cmap, font_path='font/Roboto-Regular.ttf').generate_from_frequencies(adverb_dict)

##_comment_here
wordcloud_adv.to_file(f'./{output_dir}/ADVERBS.png')

print('\n')
############
print('Finished...')
end = time_now()
############
duration = end - start
duration_min = round(duration.seconds/60, 3)
if duration_min < 2:
    time_unit = 'minute'
else:
    time_unit = 'minutes'
print(f'Total words count: {total_words_count:,} words')
print(f'Time elapsed is: {duration_min} {time_unit}.')