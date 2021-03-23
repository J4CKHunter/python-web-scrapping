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

#deneme linkleri :
#https://stackoverflow.com/questions/1080411/retrieve-links-from-web-page-using-python-and-beautifulsoup
#https://www.bbc.com/news/health-56411561
#https://www.bbc.com
#https://nayn.co/mansur-yavas-twitch-kanali-acti-selam-chat/



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
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
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


        return render_template('frekansResult.html',
                               total_word_length=total_word_length,
                               total_sent_len=total_sent_len,
                               tf_score=tf_score)
    else :
        return render_template('frekansResult.html')

@app.route('/keywordAndSimilarity')
def keywordAndSimilarity():
        return render_template('keywordAndSimilarity.html')

@app.route('/keywordAndSimilarityResult', methods=["GET","POST"])
def keywordAndSimilarityResult():

    if request.method == "POST":
        link = request.form.get("link1")
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
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

        sonuc = get_top_n(tf_idf_score, 5)

        kelimeler = []
        sayilari = []

        for key in sonuc.keys():
            kelimeler.append(key)
            sayilari.append(tumKelimeler1.get(key))


        keywordFrekanslari = dict(zip(kelimeler, sayilari))

        return render_template('keywordAndSimilarityResult.html',
                               keywordFrekanslari=keywordFrekanslari,
                               topFive=get_top_n(tf_idf_score, 5))




    else    :
        return render_template('keywordAndSimilarityResult.html')


if __name__ == '__main__':
    app.run()
