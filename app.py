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
    review_text = BeautifulSoup(raw_review, 'lxml').get_text()
    letters_only = re.sub("[^a-zA-Z]", " ", review_text)
    words = letters_only.lower().split()
    stops = set(stopwords.words("english"))
    meaningful_words = [w for w in words if not w in stops]
    return " ".join(meaningful_words)


def search(input):
    url = "https://api.jikan.moe/v4/anime"

    querystring = {"q": input, "limit": 10}

    headers = {
        "X-RapidAPI-Key": "ef33758c26msh90b77f1145da547p18115fjsnb013a57e8018",
        "X-RapidAPI-Host": "jikan1.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    output = json.loads(response.text)['data']

    results = []
    for x in output:
        title = x['title_english']
        imgurl = x['images']['jpg']['large_image_url']
        link = x['url']
        year = x['aired']['string']
        type = x['type']
        id = x['mal_id']
        synopsis = x['synopsis']
        japanese_title = x['title_japanese']
        results.append([link, imgurl, title, year, type,
                       id, synopsis, japanese_title])

    return results


# def getReviews(titleId):
    # start_url = 'https://www.imdb.com/title/%s/reviews?ref_=tt_urv' % titleId
    # link = 'https://www.imdb.com/title/%s/reviews/_ajax' % titleId

    # params = {
    #     'ref_': 'undefined',
    #     'paginationKey': ''
    # }
    # reviews = []
    # with requests.Session() as s:
    #     s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    #     res = s.get(start_url)

    #     while True:
    #         soup = BeautifulSoup(res.text, "lxml")
    #         for item in soup.select(".review-container"):
    #             review = item.select_one("div.show-more__control")
    #             reviews.append(review)

    #         try:
    #             pagination_key = soup.select_one(
    #                 ".load-more-data[data-key]").get("data-key")
    #         except AttributeError:
    #             break
    #         params['paginationKey'] = pagination_key
    #         res = s.get(link, params=params)
    # return reviews


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input = request.form['title']

        output = search(input)

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

        return render_template('reviews.html', title=title, imgurl=imgurl, year=year, jap_title=jap_title, plot=plot)
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
