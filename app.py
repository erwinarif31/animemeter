from flask import Flask, render_template, request
import json
import requests
import pickle
import re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords


filename = 'model.sav'
model = pickle.load(open(filename, 'rb'))

tfidffile = 'tfidf.sav'
tf_idf = pickle.load(open(tfidffile, 'rb'))


def review_to_words(raw_review):
    review_text = BeautifulSoup(raw_review, 'html.parser').get_text()
    letters_only = re.sub("[^a-zA-Z]", " ", review_text)
    words = letters_only.lower().split()
    stops = set(stopwords.words("english"))
    meaningful_words = [w for w in words if not w in stops]
    return " ".join(meaningful_words)


def search(input, type_title):
    url = "https://api.jikan.moe/v4/anime"

    querystring = {"q": input, "limit": 20,
                   "type": type_title, "order_by": "ranking"}

    headers = {
        "X-RapidAPI-Key": "ef33758c26msh90b77f1145da547p18115fjsnb013a57e8018",
        "X-RapidAPI-Host": "jikan1.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    output = json.loads(response.text)['data']

    results = []
    for x in output:
        title = x['titles'][0]['title']
        imgurl = x['images']['jpg']['large_image_url']
        link = x['url']
        year = x['aired']['string']
        type = x['type']
        id = x['mal_id']
        synopsis = x['synopsis']
        japanese_title = x['titles'][1]['title']
        results.append([link, imgurl, title, year, type,
                       id, synopsis, japanese_title])

    return results


def get_reviews(soup):
    get_reviews = soup.find_all('div', 'text')
    return get_reviews


def get_all_reviews(url):
    reviews = []
    user_agent = {'User-agent': 'Mozilla/5.0'}
    session_object = requests.Session()
    page = session_object.get(url, headers=user_agent)
    soup = BeautifulSoup(page.text, 'html.parser')
    reviews.extend(get_reviews(soup))
    nextpage = soup.find_all(
        attrs={"data-ga-click-type": "review-more-reviews"})
    while (nextpage):
        page = session_object.get(nextpage[0]['href'], headers=user_agent)
        soup = BeautifulSoup(page.text, 'html.parser')
        reviews.extend(get_reviews(soup))
        nextpage = soup.find_all(
            attrs={"data-ga-click-type": "review-more-reviews"})
    return reviews


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input = request.form.get('title')
        type_title = request.form.get('type')

        output = search(input, type_title)

        return render_template('index.html', output=output)
    else:
        return render_template('index.html', test='')


@app.route('/reviews/<id>', methods=['GET', 'POST'])
def reviews(id):

    if request.method == 'POST':
        title = request.form['title']
        imgurl = request.form['imgurl']
        plot = request.form['sinopsis']
        year = request.form['tahun']
        jap_title = request.form['jap_title']
        review_url = request.form['url'] + '/reviews'
        reviews = get_all_reviews(review_url)

        clean_reviews = []
        for i in reviews:
            clean_reviews.append(review_to_words(i.text))

        test_input = tf_idf.transform(clean_reviews)
        good_reviews = 0
        for review in test_input:
            pred = model.predict(review)[0]
            if pred == 1:
                good_reviews += 1

        good_reviews = round((good_reviews / len(clean_reviews)) * 100)

        return render_template('reviews.html', title=title, imgurl=imgurl, year=year, jap_title=jap_title, plot=plot, reviews=len(reviews), rating=good_reviews)
    #     for i in reviews:
    #         test_processes = [review_to_words(i)]
    #         test_input = tf_idf.transform(test_processes)
    #         res = model.predict(test_input)[0]
    #         if res == 1:
    #             good_reviews += 1
    #         else:
    #             bad_reviews += 1

    #     total_reviews = good_reviews + bad_reviews
    #     good_reviews_perc = round((good_reviews/total_reviews) * 100)
    #     return render_template('reviews.html', image=image, plot=plot, title=movieTitle, year=year, genres=genres, total=total_reviews, perc=good_reviews_perc)
