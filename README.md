# animemeter
### Data
Data terdiri dari 25000 review dari IMDB dengan label sentimen negatif atau positif.
```python
data_review = pd.read_csv("data/labeledTrainData.tsv", header=0, delimiter="\t", quoting=3)
data_review.head()
```
![image](https://user-images.githubusercontent.com/87022160/208854148-1b753a8d-66f9-4298-806c-42165d8a1533.png)
### Data Cleaning and Text Preprocessing
Dalam data cleaning dan preprocessing data, dilakukan hal-hal berikut
- Menghilangkan Tag HTML
- Menghilangkan tanda baca dan angka
- Mengubah ke lowercase
- Menghilangkan [stop word](https://en.wikipedia.org/wiki/Stop_word)
```python
nltk.download("stopwords")

def review_to_words(raw_review):
    review_text = BeautifulSoup(raw_review, 'html.parser').get_text()
    letters_only = re.sub("[^a-zA-Z]", " ", review_text)
    words = letters_only.lower().split()
    stops = set(stopwords.words("english"))
    meaningful_words = [w for w in words if not w in stops]
    return " ".join(meaningful_words)
```
```python
x_not_clean = data_review["review"].values
y = data_review["sentiment"]
X = []

for i in range(0, len(x_not_clean)):
    X.append(review_to_words(x_not_clean[i]))
```
### Train-test Split
```python
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2, random_state=26)
```
### TF-IDF Vectorization
```python
tf_idf = TfidfVectorizer()
X_train_tf = tf_idf.fit_transform(X_train)
X_test_tf = tf_idf.transform(X_test)
```
### Naive Bayes Classifier
Untuk melakukan classification, digunakan metode Naive Bayes
```python
naive_bayes_classifier = MultinomialNB()
naive_bayes_classifier.fit(X_train_tf, y_train)
```
Dengan hasil prediksi
```python
y_pred = naive_bayes_classifier.predict(X_test_tf)
print(classification_report(y_test, y_pred))
```
![image](https://user-images.githubusercontent.com/87022160/208856955-d5cc52b7-bb99-4019-a646-83d2c7799444.png)
