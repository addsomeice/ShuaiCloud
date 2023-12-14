def read_city():
    city_population = {}
    with open('static/us-cities.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            city_population[row['city']] = int(row['population'])
    return city_population

@app.route('/popular_words2', methods=['GET'])
def popular_words2():
    # 读取评论数据
    reviews_data = read_csv()
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
    city_population = read_city()
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