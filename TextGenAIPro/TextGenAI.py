import pickle
import random
import numpy as np
import pandas as pd
from keras import Sequential
from keras.src.layers import LSTM, Dense, Activation
from keras.src.optimizers import RMSprop
from keras.src.saving import load_model
from nltk.tokenize import RegexpTokenizer



text_df = pd.read_csv('us_election_2020_1st_presidential_debate.csv')
#print(text_df)

text = list(text_df.text.values)
joined_text=" ".join(text)

partial_text= joined_text[:1000000]
tokenizer = RegexpTokenizer(r'\w+')
tokens=tokenizer.tokenize(partial_text.lower())
#print(tokens)

unique_tokens=np.unique(tokens)
unique_token_index= {token: idx for idx, token in enumerate(unique_tokens)}
#print(unique_token_index)

n_words=10
input_words=[]
next_words=[]

for i in range (len(tokens)- n_words):
    input_words.append(tokens[i:i+n_words])
    next_words.append(tokens[i+n_words])

#print(next_words)
#print(input_words)

X=np.zeros((len(input_words),n_words,len(unique_tokens)),dtype=bool)
Y=np.zeros((len(next_words),len(unique_tokens)))

for i,words in enumerate(input_words):
    for j,word in enumerate(words):
        X[i, j, unique_token_index[word]] = 1
    Y[i, unique_token_index[next_words[i]]] = 1
#print(X)

model = Sequential()
model.add(LSTM(128, input_shape=(n_words, len(unique_tokens)), return_sequences=True))
model.add(LSTM(128))
model.add(Dense(len(unique_tokens)))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer=RMSprop(learning_rate=0.01), metrics=['accuracy'])
model.fit(X, Y, batch_size=128, epochs=15, shuffle=True)

model.save('model.h5')
model=load_model('model.h5')

def predict_next_word(input_text,n_best):
    input_text=input_text.lower()
    X=np.zeros((1,n_words,len(unique_tokens)))
    for i, word in enumerate(input_text.split()):
        X[0, i, unique_token_index[word]] = 1

    predictions=model.predict(X)[0]
    return np.argpartition(predictions, -n_best)[-n_best:]

possible=predict_next_word("He will have to look into this thing and he",5)
print(possible)
print([unique_tokens[idx] for idx in possible])

def generate_text(input_text, text_length, n_words, creativity=3):
    word_sequence= input_text.split()
    current=0
    for _ in range(text_length):
        sub_sequence=" ".join(tokenizer.tokenize(" ".join(word_sequence).lower())[current:current+n_words])
        try:
            choice = unique_tokens[random.choice(predict_next_word(sub_sequence,creativity))]
        except:
            choice = random.choice(unique_tokens)
        word_sequence.append(choice)
        current +=1
    return " ".join(word_sequence)
print(generate_text("He will have to look into this thing and he", 100,5))

model = load_model("model.h5")