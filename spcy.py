import spacy
from heapq import nlargest

# Load the English NLP model
nlp = spacy.load('en_core_web_md')

def summarize_sentence(sentence, max_length=15):
    doc = nlp(sentence)
    word_frequencies = {}
    for word in doc:
        if word.is_stop is False and word.is_punct is False:
            if word.text.lower() not in word_frequencies.keys():
                word_frequencies[word.text.lower()] = 1
            else:
                word_frequencies[word.text.lower()] += 1

    max_freq = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_freq

    sentence_scores = {}
    for sent in doc.sents:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    summarized_sentence = nlargest(1, sentence_scores, key=sentence_scores.get)

    summary = ' '.join([word.text for word in summarized_sentence[0] if not word.is_stop and not word.is_punct])
    summary_words = summary.split()
    if len(summary_words) > max_length:
        summary = ' '.join(summary_words[:max_length])

    return summary

# Example usage
paragraph = ("When you’re running a production workload on Azure, get Azure technical support initial response times between one hour and one business day, based on case severity, with the Standard plan.")

question = "What is ur conclusion?"


short_answer = summarize_sentence(paragraph)

print("Short Answer:", short_answer)

