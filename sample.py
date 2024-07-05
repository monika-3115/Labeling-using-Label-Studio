
LABEL_STUDIO_URL = 'https://labelstudio.dealwallet.com/'
API_KEY = 'ad1a15ed77550e5ff082b9fb10d7e7af18662118'

import pandas as pd
from label_studio_sdk.client import LabelStudio
import spacy
from heapq import nlargest

print("connecting..")

ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)
print("connected..!")

print("loading the nlp model..")
nlp = spacy.load('en_core_web_md')
if nlp:
    print("loaded successfully...")

class Project:
    def __init__(self, id):
        self.id = id

project = Project(id="4")

df = pd.read_csv('scrapped_data.csv')

df.dropna(subset=['header'], inplace=True)
df = df[df['header'].str.strip().astype(bool)]

df["question"] = "What is your final conclusion?"

clms  = []
for _, row in df.iterrows():
    if row["header"] == "" or row["link"] == "" :
        continue

    text = row["text"]
    question = row["question"]
    
    def labeling(text, max_length=15):
        doc = nlp(text)
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

        ans = ' '.join([word.text for word in summarized_sentence[0] if not word.is_stop and not word.is_punct])
        summary_words = ans.split()
        if len(summary_words) > max_length:
            ans = ' '.join(summary_words[:max_length])

        return ans
    
    relevant_answer = labeling(text)


    clm = {
        "data" : {  "text" : row["text"], 
                    "header" : row["header"], 
                    "link" : row["link"], 
                    "question" : row["question"],
                },

            


        "annotations": [
            {
                "result": [
                    {
                        "from_name": "intent",
                        "to_name": row["question"],
                        "type": "choices",
                        "value": {
                            "choices": ["General Inquiry"]
                        }
                    },
                    {
                        "from_name": "entities",
                        "to_name": row["text"],
                        "type": "labels",
                        "value": [
                            {
                                "labels": relevant_answer
                            }
                        ]
                    }
                ]
            }
        ],
        "predictions": [
            {
                "result": [
                    {
                        "from_name": "intent",
                        "to_name": row["question"],
                        "type": "choices",
                        "value": {
                            "choices": ["General Inquiry"]
                        }
                    },
                    {
                        "from_name": "entities",
                        "to_name": row["text"],
                        "type": "labels",
                        "value": [
                            {
                                "labels": relevant_answer
                            }
                        ]
                    }
                ]
            }
        ]
    }

    
    clms.append(clm)

try:
    response = ls.projects.import_tasks(
        id=project.id,
        request=clms
    )
    print("Tasks imported successfully")
    print(response)
except Exception as e:
    print(f"An error occurred: {e}")

print("coloumns imported successfully..")
