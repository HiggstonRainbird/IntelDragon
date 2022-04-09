# IntelDragon Backend
# Written by David Freiberg and Christine Palmer
# Created April 6th, 2022.
# Last updated April 8th, 2022

from __future__ import print_function
import gensim, logging
from nltk.tokenize import RegexpTokenizer
import streamlit as st
import pandas as pd
import numpy as np

from localVariables import stop, article_list

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

tokenizer = RegexpTokenizer(r'[0-9A-Za-z]*[A-Za-z][0-9A-Za-z]*')

# Tokenizer function, takes a string and returns a list of tokens.

model = gensim.models.Word2Vec.load('Cybersecurity_Unigram_01.bin')
def convert_to_tokens(text):
	intermediate = tokenizer.tokenize(text)
	intermediate = [(i.lower() if i[1:].lower()==i[1:] else i) for i in intermediate]
	intermediate = [i for i in intermediate if i not in stop]
	# Check if each token is in the model.
	intermediate = [i for i in intermediate if i in model.wv.key_to_index]
	return intermediate

def custom_cosine_similarity(a, b):
	return np.dot(gensim.matutils.unitvec(a), gensim.matutils.unitvec(b))

# Preprocessing of cached articles.

article_titles = []
article_vectors = []
article_texts = []
article_url = []
article_sentences = []
for article in article_list:
	banned_titles = ["Types of Cyber Attacks:", "Subscribe to read"]
	if any(b in article["title"] for b in banned_titles):
		continue
	article_vector = []
	sentences = []
	for line in article["text"].replace("\n","  ").split(". "):
		line_vector = []
		for word in convert_to_tokens(line):
			try:
				line_vector.append(model.wv.get_vector(word))
			except:
				pass
		if len(line_vector)>0:
			article_vector.append(np.mean(line_vector, axis=0))
			sentences.append(line + ".")	
	article_vectors.append(article_vector)
	article_titles.append(article["title"])
	article_url.append(article["url"])
	article_texts.append(article["text"])
	article_sentences.append(sentences)
		
data = np.array(article_vectors) # sentence vectors
labels = np.array(article_titles) # article titles
texts = np.array(article_texts) # article texts
urls = np.array(article_url)
sentences = np.array(article_sentences)

# Main function.

st.title("IntelDragon")

with st.expander("Word Similarity", expanded=False):
	with st.form(key="word_similarity_form"):

		similarityInputPositive = st.text_area("Like these words:", "WannaCry")
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
		# st.markdown(f"")

		submit_button_similarity = st.form_submit_button(label="Refresh results")

with st.expander("One of These Things is Not Like the Others", expanded=False):
	with st.form(key="odd_man_out_form"):

		oddManOutInput = st.text_area("", "WannaCry Bitcoin Ryuk Petya REvil")
		parsedInput = convert_to_tokens(oddManOutInput)
		# "WannaCry Bitcoin ryuk petya REvil" #EternalBlue

		oddManOutOutput = model.wv.doesnt_match(parsedInput) #EternalBlue

		submit_button_oddManOut = st.form_submit_button(label="Refresh results")

		# Make similarity matrix of the input words.
		similarityMatrix = []
		for i in range(0,len(parsedInput)):
			tmpMatrix = []
			for j in range(0, len(parsedInput)):
				tmpMatrix.append(model.wv.similarity(parsedInput[i], parsedInput[j]))
			similarityMatrix.append(tmpMatrix)
		
		st.markdown("## Least Similar:")
		st.markdown(f"{oddManOutOutput}")

		st.markdown("## Similarity Matrix")
		similarityMatrix = pd.DataFrame(similarityMatrix, columns=parsedInput, index=parsedInput)
		st.table(similarityMatrix.style.format("{:.3f}").highlight_min(axis=0))

initial_input_text = "I'm mostly interested in Bitcoin, Ethereum, and potential financial and cryptocurrency scams."
with st.form(key="relevant_article_form"):
	input_text = st.text_area("Your interests and needs:", initial_input_text)

	sentence_vector = []
	line_vector = []
	input_sentence = ""
	for sentence in input_text.replace("\n","").split(". "):
		line_vector = []
		for word in convert_to_tokens(sentence):
			try:
				line_vector.append(model.wv.get_vector(word))
			except:
				pass
			if len(line_vector)>0:
				sentence_vector = np.mean(line_vector, axis=0)
				input_sentence = sentence

	sorted_articles = []
	for a in range(0,len(article_vectors)-1):
		if len(article_vectors[a]) < 10:
			continue
		relevance = -1.0
		most_relevant_sentence_id = 0
		for s in range(0,len(article_vectors[a])-1):
			dist = custom_cosine_similarity(sentence_vector, article_vectors[a][s])
			if dist > relevance:
				relevance = dist
				most_relevant_sentence_id = s
		sorted_articles.append([a, most_relevant_sentence_id, relevance])

	sorted_articles.sort(key=lambda l: -l[-1])

	sorted_articles_df = pd.DataFrame(sorted_articles, columns=["article_id", "key_sentence", "relevance"])

	submit_button_relevantArticles = st.form_submit_button("Find Relevant Articles")

# Display the text corresponding to the top 5 articles.
col0, col1, col2, col3, col4 = st.columns(5)
with col0:
	i = 0
	article_id = sorted_articles_df["article_id"][i]
	st.markdown(f"**[{article_titles[article_id]}]({article_url[article_id]})**")
	st.markdown(f"*Relevance: {round(sorted_articles_df['relevance'][i],3)}*")
	st.markdown(f"{sentences[article_id][sorted_articles_df['key_sentence'][i]]}")
	st.markdown("")

with col1:
	i = 1
	article_id = sorted_articles_df["article_id"][i]
	st.markdown(f"**[{article_titles[article_id]}]({article_url[article_id]})**")
	st.markdown(f"*Relevance: {round(sorted_articles_df['relevance'][i],3)}*")
	st.markdown(f"{sentences[article_id][sorted_articles_df['key_sentence'][i]]}")
	st.markdown("")

with col2:
	i = 2
	article_id = sorted_articles_df["article_id"][i]
	st.markdown(f"**[{article_titles[article_id]}]({article_url[article_id]})**")
	st.markdown(f"*Relevance: {round(sorted_articles_df['relevance'][i],3)}*")
	st.markdown(f"{sentences[article_id][sorted_articles_df['key_sentence'][i]]}")
	st.markdown("")

with col3:
	i = 3
	article_id = sorted_articles_df["article_id"][i]
	st.markdown(f"**[{article_titles[article_id]}]({article_url[article_id]})**")
	st.markdown(f"*Relevance: {round(sorted_articles_df['relevance'][i],3)}*")
	st.markdown(f"{sentences[article_id][sorted_articles_df['key_sentence'][i]]}")
	st.markdown("")

with col4:
	i = 4
	article_id = sorted_articles_df["article_id"][i]
	st.markdown(f"**[{article_titles[article_id]}]({article_url[article_id]})**")
	st.markdown(f"*Relevance: {round(sorted_articles_df['relevance'][i],3)}*")
	st.markdown(f"{sentences[article_id][sorted_articles_df['key_sentence'][i]]}")
	st.markdown("")