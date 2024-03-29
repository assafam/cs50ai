import math
import os
import re
import string
import sys

import nltk

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            files[filename] = f.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    contents = []
    for word in nltk.word_tokenize(document):
        word = re.sub(f"[{re.escape(string.punctuation)}]", "", word.lower())
        if word != "" and word not in nltk.corpus.stopwords.words("english"):
            contents.append(word)

    return contents


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Get all words in corpus and count number of documents in which they appear
    words_freq = dict()
    for document in documents.keys():
        doc_words = set(documents[document])
        for word in doc_words:
            if word not in words_freq:
                words_freq[word] = 1
            else:
                words_freq[word] += 1

    # Calculate IDFs
    idfs = dict()
    num_documents = len(documents)
    for word in words_freq.keys():
        idfs[word] = math.log(num_documents / words_freq[word])

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Calculate TF-IDF per file
    tfidf = {file: 0 for file in files.keys()}
    for word in query:
        try:
            idf = idfs[word]
            for file in files.keys():
                tf = files[file].count(word)
                tfidf[file] += tf * idf
        except KeyError:
            # Words that don't appear in any file are ignored
            pass

    return sorted(tfidf, key=tfidf.get, reverse=True)[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # Calculate sentence IDF (sum of IDF of all words which appear in query) and term density
    sent_data = {sentence: {"idf": 0, "term_cnt": 0} for sentence in sentences.keys()}
    for sentence, sentence_words in sentences.items():
        term_cnt = 0
        for word in query:
            if word in sentence_words:
                sent_data[sentence]["idf"] += idfs[word]
                term_cnt += 1
        sent_data[sentence]["term_cnt"] = term_cnt / len(sentence.split())

    return sorted(
        sent_data,
        key=lambda x: (sent_data[x]["idf"], sent_data[x]["term_cnt"]),
        reverse=True
        )[:n]


if __name__ == "__main__":
    main()
