# IntelDragon Backend
# Written by David Freiberg and Christine Palmer
# Created April 6th, 2022.
# Last updated April 6th, 2022

from __future__ import print_function
import gensim, logging
from nltk.tokenize import RegexpTokenizer
import streamlit as st
import pandas as pd

from localVariables import stop

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

tokenizer = RegexpTokenizer(r'[0-9A-Za-z]*[A-Za-z][0-9A-Za-z]*')

# Tokenizer function, takes a string and returns a list of tokens.

def convert_to_tokens(text):
	intermediate = tokenizer.tokenize(text)
	intermediate = [(i.lower() if i[1:].lower()==i[1:] else i) for i in intermediate]
	intermediate = [i for i in intermediate if i not in stop]
	return intermediate

model = gensim.models.Word2Vec.load('Cybersecurity_Unigram_01.bin')
#len(model.wv.vocab)

#[print(i) for i in model.wv.most_similar(positive=['password'])]

st.title("IntelDragon")

with st.expander("Word Similarity", expanded=False):
	with st.form(key="word_similarity_form"):

		similarityInputPositive = st.text_area("Like these words:", "RCE")
		similarityInputNegative = st.text_area("Unlike these words:", "")
		similarityColumns = ["Word", "Similarity"]

		similarityOutput = \
			pd.DataFrame(
			model.wv.most_similar(
				positive=convert_to_tokens(similarityInputPositive), 
				negative=convert_to_tokens(similarityInputNegative))
			)
		similarityOutput.columns = similarityColumns

		st.table(similarityOutput)
		
		submit_button_similarity = st.form_submit_button(label="Refresh results")

with st.expander("One of These Things is Not Like the Others", expanded=False):
	with st.form(key="odd_man_out_form"):

		oddManOutInput = st.text_area("", "WannaCry EternalBlue ryuk petya REvil")
		# "WannaCry EternalBlue ryuk petya REvil" #EternalBlue

		oddManOutOutput = model.wv.doesnt_match(convert_to_tokens(oddManOutInput)) #EternalBlue

		submit_button_oddManOut = st.form_submit_button(label="Refresh results")

		oddManOutOutput