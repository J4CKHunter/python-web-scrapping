from flask import Flask, render_template, request, url_for, redirect
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from nltk import tokenize
from operator import itemgetter
import math
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stop_words = set(stopwords.words('english'))
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


#deneme linkleri :
#https://stackoverflow.com/questions/1080411/retrieve-links-from-web-page-using-python-and-beautifulsoup
#https://www.bbc.com/news/health-56411561
#https://www.bbc.com
#https://nayn.co/mansur-yavas-twitch-kanali-acti-selam-chat/

class frekansFinder:
    def __init__(self,link = {},total_word_length= {},total_sent_len= {},tf_score= {}):
        self.link = link
        req = Request(self.link, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "lxml")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        total_words = text.split()
        self.total_word_length = len(total_words)

        total_sentences = tokenize.sent_tokenize(text)
        self.total_sent_len = len(total_sentences)

        self.tf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words:
                if each_word in self.tf_score:
                    self.tf_score[each_word] += 1
                else:
                    self.tf_score[each_word] = 1
        # her kelimenin kaç kere yer aldığı

    def get_total_word_length(self):
        return self.total_word_length

    def get_total_sent_len(self):
        return self.total_sent_len

    def get_tf_score(self):
        return self.tf_score

class keywordSimilarity:

    def __init__(self,link= {},keywordFrekanslari= {},sonuc= {}):
        self.link=link
        req = Request(self.link, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "lxml")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        total_words = text.split()
        total_word_length = len(total_words)

        total_sentences = tokenize.sent_tokenize(text)
        total_sent_len = len(total_sentences)

        tf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words:
                if each_word in tf_score:
                    tf_score[each_word] += 1
                else:
                    tf_score[each_word] = 1
        # her kelimenin kaç kere yer aldığı

        tumKelimeler1 = tf_score.copy()

        # Dividing by total_word_length for each dictionary element
        tf_score.update((x, y / int(total_word_length)) for x, y in tf_score.items())

        def check_sent(word, sentences):
            final = [all([w in x for w in word]) for x in sentences]
            sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
            return int(len(sent_len))

        idf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words:
                if each_word in idf_score:
                    idf_score[each_word] = check_sent(each_word, total_sentences)
                else:
                    idf_score[each_word] = 1

        # Performing a log and divide
        idf_score.update((x, math.log(int(total_sent_len) / y)) for x, y in idf_score.items())

        tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}

        def get_top_n(dict_elem, n):
            result = dict(sorted(dict_elem.items(), key=itemgetter(1), reverse=True)[:n])
            return result

        self.sonuc = get_top_n(tf_idf_score, 5)

        kelimeler = []
        sayilari = []

        for key in self.sonuc.keys():
            kelimeler.append(key)
            sayilari.append(tumKelimeler1.get(key))

        self.keywordFrekanslari = dict(zip(kelimeler, sayilari))

    def get_keywordFrekanslari(self):
        return self.keywordFrekanslari

    def get_sonuc(self):
        return self.sonuc

class textSimilarity:
    def __init__(self,link1 = { },link2= { },result={}):
        self.link1=link1
        self.link2=link2

        req = Request(link1, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "lxml")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text1 = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines1 = (line.strip() for line in text1.splitlines())
        # break multi-headlines into a line each
        chunks1 = (phrase.strip() for line in lines1 for phrase in line.split("  "))
        # drop blank lines
        text1 = '\n'.join(chunk for chunk in chunks1 if chunk)


        req = Request(link2, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "lxml")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text2 = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines2 = (line.strip() for line in text2.splitlines())
        # break multi-headlines into a line each
        chunks2 = (phrase.strip() for line in lines2 for phrase in line.split("  "))
        # drop blank lines
        text2 = '\n'.join(chunk for chunk in chunks2 if chunk)

        def clean_string(text):
            # text = ''.join([word for word in text if word not in string.punctuation])
            exclist = string.punctuation
            table_ = str.maketrans(exclist, ' ' * len(exclist))
            text = ' '.join(text.translate(table_).split())
            text = text.lower()
            text = ' '.join([word for word in text.split() if word not in stop_words])

            return text

        sentences = {text1,text2}
        cleaned = list(map(clean_string, sentences))

        vectorizer = CountVectorizer().fit_transform(cleaned)
        vectors = vectorizer.toarray()

        csim = cosine_similarity(vectors)

        def cosine_sim_vectors(vec1, vec2):
            vec1 = vec1.reshape(1, -1)
            vec2 = vec2.reshape(1, -1)

            return cosine_similarity(vec1, vec2)[0][0]

        try:
            self.result = cosine_sim_vectors(vectors[0], vectors[1])
        except:
            self.result = 1.0000000000000000


    def get_result(self):
        return self.result


app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/frekans')
def frekans():
        return render_template('frekans.html')


@app.route('/frekansResult', methods=["GET","POST"])
def frekansResult():

    if request.method == "POST":
        link = request.form.get("link")
        frekans = frekansFinder(link)
        return render_template('frekansResult.html',
                               total_word_length=frekans.get_total_word_length(),
                               total_sent_len=frekans.get_total_sent_len(),
                               tf_score=frekans.get_tf_score())

    else :
        return render_template('frekansResult.html')

@app.route('/keywordAndSimilarity')
def keywordAndSimilarity():
        return render_template('keywordAndSimilarity.html')

@app.route('/keywordAndSimilarityResult', methods=["GET","POST"])
def keywordAndSimilarityResult():

    if request.method == "POST":
        link1 = request.form.get("link1")
        link2 = request.form.get("link2")
        keySim = keywordSimilarity(link1)
        keySim2 = keywordSimilarity(link2)
        textSim = textSimilarity(link1,link2)
        return render_template('keywordAndSimilarityResult.html',
                               keywordFrekanslari=keySim.get_keywordFrekanslari(),
                               topFive=keySim.get_sonuc(),
                               keywordFrekanslari2=keySim2.get_keywordFrekanslari(),
                               topFive2=keySim2.get_sonuc(),
                               result=textSim.get_result()
                               )
    else    :
        return render_template('keywordAndSimilarityResult.html')


if __name__ == '__main__':
    app.run()
