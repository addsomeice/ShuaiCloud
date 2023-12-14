import csv
from collections import Counter

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

def get_reviews():
    csv_data = []
    filename='amazon-reviews.csv'
    with open(filename, 'r') as f:
        csv_file = csv.DictReader(f)
        for data in csv_file:
            csv_data.append(data)
    return csv_data


# 这是读取城市信息的方法
def get_cities():
    filename = 'us-cities.csv'
    city_population = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            city_population[row['city']] = int(row['population'])
    return city_population


def write_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

@app.route('/words')
def word():
    return render_template('word.html')

@app.route('/popular_words1', methods=['GET'])
def popular_words():
    reviews_data = get_reviews()
    city = request.args.get('city')
    limit = request.args.get('limit', type=int, default=10)
    if city:
        filtered_reviews = [review for review in reviews_data if review['city'] == city]
    else:
        filtered_reviews = reviews_data
    word_counts = Counter()
    for review in filtered_reviews:
        words = review['review'].split()
        word_counts.update(words)
    common_words = word_counts.most_common(limit)
    response = [{"term": word, "popularity": count} for word, count in common_words]
    return jsonify(response)


@app.route('/popular_words2', methods=['GET'])
def popular_words2():
    # 读取评论数据
    reviews_data = get_reviews()
    city = request.args.get('city')
    limit = request.args.get('limit', type=int, default=10)

    # 筛选符合城市条件的评论
    if city:
        filtered_reviews = [review for review in reviews_data if review['city'] == city]
    else:
        filtered_reviews = reviews_data

    # 统计单词出现频率
    word_counts = Counter()
    for review in filtered_reviews:
        words = review['review'].split()
        word_counts.update(words)

    # 获取最常见的单词
    common_words = word_counts.most_common(limit)

    # 搜索评论中出现的常见单词，并获取城市列表及人口总数
    city_population = get_cities()
    city_popularity = {}
    for word, count in common_words:
        word_city_popularity = 0
        for review in filtered_reviews:
            if word in review['review']:
                city_name = review['city']
                population = city_population.get(city_name, 0)
                word_city_popularity += population
        city_popularity[word] = word_city_popularity

    # 构建响应
    response = [{"term": word, "popularity": city_popularity[word]} for word, _ in common_words]
    print(response)
    return jsonify(response)

@app.route('/substitute_words', methods=['POST'])
def substitute_words():
    request_data = request.get_json()
    original_word = request_data.get('word')
    new_word = request_data.get('substitute')

    reviews_data = get_reviews()
    affected_reviews = 0

    for review in reviews_data:
        if original_word in review['review']:
            review['review'] = review['review'].replace(original_word, new_word)
            affected_reviews += 1
    filename='amazon-reviews.csv'
    write_csv(filename, reviews_data)

    return jsonify({"affected_reviews": affected_reviews})

if __name__ == '__main__':
    app.run()
