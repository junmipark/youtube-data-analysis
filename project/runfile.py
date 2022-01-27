#-*- coding: utf-8 -*-

import os, io, re
import sqlite3
from flask import Flask, request,jsonify, session, g, redirect, url_for, abort, \
     render_template, flash

entries = []
category = ['1', '2', '10', '15', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44']
category_id = '1' # category_id 기본값 설정
tag = '먹방' # tag 기본값 설정

app = Flask(__name__)
app.config.from_object(__name__)        

# Database Configuration

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'youtube.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

DIRECTORY=os.path.join(app.root_path, 'KRvideos.csv')

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
        g.db = connect_db()
        
@app.teardown_request
def teardown_request(exception):
        g.db.close()

def get_title(category_id): # 카테고리 타이틀 조회
    sql = 'select category_title from category where category_id = {};'.format(category_id)
    cur = g.db.execute(sql)
    chategory_title = [row[0] for row in cur.fetchall()]
    ct = ''.join(chategory_title)
    return ct

# 카테고리 별 영상 조회
@app.route('/search_category', methods = ['POST'])
def search_category() :
    category_id = request.form['category']
    option = request.form['option']
    sql = '''SELECT distinct title, views, likes, dislikes, publish_time
    FROM video NATURAL JOIN category NATURAL JOIN information natural join date
    WHERE category_id = {}
    ORDER BY {};'''.format(category_id, option)
    cur = g.db.execute(sql)
    ent = [dict(title = row[0], views = row[1], likes = row[2], dislikes = row[3], publish_time = row[4][:10]) for row in cur.fetchall()]
    ent.insert(0, dict(title = get_title(category_id), views = '', likes = '', dislikes = '', publish_time = ''))
    return render_template('search_category.html', ent = ent)

# 카테고리 별 태그 빈도수 검색
@app.route('/search_tag', methods = ['POST'])
def search_tag():
    tag = request.form['variable']
    sql = '''SELECT DISTINCT tag,COUNT(tag), category_title
    FROM video JOIN category USING(category_id) NATURAL JOIN tags
    WHERE tag = '{}'
    GROUP BY tag, category_title
    ORDER BY COUNT(tag) DESC;'''.format(tag)
    cur = g.db.execute(sql)
    entries2 = [dict(tag = row[0], count = row[1], ct = row[2]) for row in cur.fetchall()]
    return render_template('search_tag.html', entries2 = entries2)

# 관련 태그 영상 검색
@app.route('/search_tag2', methods = ['POST'])
def search_tag2():
    tag = request.form['variable']
    sql = '''SELECT DISTINCT title, views, likes, dislikes,publish_time
    FROM video NATURAL JOIN information NATURAL JOIN tags natural join date
    WHERE tag = '{}'
    ORDER BY views DESC;'''.format(tag)
    print(type(tag))
    cur = g.db.execute(sql)
    ent = [dict(title = row[0], views = row[1], likes = row[2], dislikes = row[3], publish_time = row[4][:10]) for row in cur.fetchall()]
    ent.insert(0, dict(title = tag, views = '', likes = '', dislikes = '', publish_time = ''))
    return render_template('search_tag2.html', ent = ent)

# 카테고리 별 인기 태그 상위 10개
def get_entries():
    all_entries = list()

    for category_id in category:
        sql = '''SELECT DISTINCT tag,COUNT(tag), category_title
        FROM video JOIN category USING(category_id) NATURAL JOIN tags
        WHERE category_id = {}
        GROUP BY tag, category_id
        ORDER BY COUNT(tag) DESC LIMIT 10;'''.format(category_id)
        cur = g.db.execute(sql)
        entries = [dict(tag = row[0].replace(';',''), count = row[1], ct = row[2]) for row in cur.fetchall()]
        if len(entries) < 1 : continue
        entries.insert(0, dict(tag = get_title(category_id), count = '[' + category_id + ']'))
        all_entries.append(entries)

    return all_entries

@app.route('/show_entries',methods = ['POST'])
def show_entries() :
    all_entries = get_entries()
    return render_template('show_entries.html', all_entries = all_entries)

##### Data Mining #####

###############################
# category 정보 읽기...
import json
CATEGORY = dict()
with open('KR_category_id.json') as f:
    data = json.load(f)
for x in data['items']:
    CATEGORY[x['id']] = x['snippet']['title']

HEAD = (
'video_id',   # 0
'trending_date',  # 1
'title', # 2
'channel_title', # 3
'category_id', # 4
'publish_time', # 5
'tags', # 6
'views', # 7
'likes', # 8
'dislikes', # 9
'comment_count', # 10
'thumbnail_link', # 11
'comments_disabled', # 12
'ratings_disabled', # 13
'video_error_or_removed', # 14
'description' # 15
)

def make_word_list(s):
    w_lst = list()
    for x in s.split('|'):        
        x = x.replace('"', '')
        x = x.replace("'", '')
        for z in x.split(' '):
            if z != '' and z != ' ':
                w_lst.append(z)
    return w_lst

def get_data():
    with open(DIRECTORY, encoding='utf8') as f:
        all_lines = f.readlines()

    all_lines.pop(0)  # title line

    valid_data = list()

    for line in all_lines:
        items = line.strip().split(',')
        
        ## 데이터가 제대로 들어있지 않은 경우
        if len(items) != 16: continue

        ## 카테고리 정보가 존재하지 않은 경우
        if items[4] not in category: continue

        ## 태그 테이터가 존재하지 않은 경우
        if items[6] == '[none]': continue

        valid_data.append(line)

    return valid_data

all_lines = get_data()

import numpy as np

########### (1) FEATURE 추출해 보기 ###############
def extract_features():
    Cats = dict()
    
    FEATURES = [];

    for line in all_lines:
        items = line.strip().split(',')

        t_lst = make_word_list(items[6]) # tag list
        cat = items[4] # category id

        # 카테고리별로 태그 저장
        if cat in Cats:
            for t in t_lst:
                if t in Cats[cat]:
                    Cats[cat][t] += 1
                else:
                    Cats[cat][t] = 1
        else:
            Cats[cat] = dict()
            for t in t_lst:
                Cats[cat][t] = 1

    for Tags in Cats.values():
        freq = list(set(Tags.values()))
        median = np.median(freq) # 태그 등장 빈도수에 대한 중간값 찾기

        for tag in Tags:
            if Tags[tag] > median:
                FEATURES.append(tag)   
            
    return FEATURES

FEATURES = extract_features()

########### (2) FEATURE 저장 : 학습데이터 구성해보기 ###############
def make_feature(items):
    feature = [0 for _ in range(len(FEATURES))]
    w_lst = make_word_list(items[6])    
    for w in w_lst:
        if w in FEATURES:                
            feature[FEATURES.index(w)] = 1
    feature.append(int(items[7]))   # view
    feature.append(int(items[8]))   # like
    feature.append(int(items[9]))   # dislike
        
    return feature

######### (3) Decision Trees
import numpy as np
from sklearn.tree import DecisionTreeClassifier
    
def make_dec_tree(tree):
    Video = dict()

    for line in all_lines:
        items = line.strip().split(',')

        v_key = items[0]
        target = items[4]    # category_id --> TARGET
        Video[v_key] = make_feature(items) + [target]

    lst = list()
    for key, val in Video.items(): 
        lst.append([x for x in val])
    
    data = np.array(lst)

    bound = len(data)//2

    # x_train, x_test => feature
    # t_train, t_test => target
    x_train, t_train = data[:bound, :-1], data[:bound, -1]
    x_test, t_test = data[bound:, :-1], data[bound:, -1]
                        
    tree.fit(x_train, t_train)

    score = dict()

    score['tr'] = str(tree.score(x_train, t_train))[:5] # 훈련세트 정확도
    score['ts'] = str(tree.score(x_test, t_test))[:5] # 테스트 세트 정확도

    res = dict() # tree와 score 데이터를 반환할 변수
    
    res['tree'] = tree
    res['score'] = score

    return res

tree = DecisionTreeClassifier(random_state=0, max_depth=5)
res = make_dec_tree(tree)

tree = res['tree']
score = res['score']

import random

# 웹에 표시할 샘플 데이터 만들기
def get_random_data():
    group_of_items = all_lines # 샘플을 만들 데이터
    num_to_select = 10 # 샘플 크기

    sample_data = random.sample(group_of_items, num_to_select)
    
    return sample_data

# 예제 적용
@app.route('/data_mining', methods = ['POST'])
def data_mining() :
    all_entries = []

    sample_data = get_random_data()

    sample_size = len(sample_data)
    sample_score = 0

    for real in sample_data:
        items = real.strip().split(',')
                
        one = make_feature(items)
        target = items[4]  # -->  이것을 맞춰야 함...

        predicted_cat = tree.predict([one])

        predicted_data = CATEGORY[predicted_cat[0]] # 예측한 카테고리
        real_data = CATEGORY[target] # 실제 카테고리

        entry = dict()
        
        entry['title'] = items[2]
        entry['tags'] = '/'.join(make_word_list(items[6]))
        entry['view'] = items[7]
        entry['like'] = items[8]
        entry['dislike'] = items[9]
        entry['predict'] = predicted_data
        entry['real'] = real_data
        
        if predicted_data == real_data :
            entry['TF'] = 'T'
            sample_score += 1
        else:
            entry['TF'] = 'F'
            
        all_entries.append([entry])
        
        score['sample'] = str(sample_score / sample_size)[:5]
        score['size'] = sample_size
    
    return render_template('data_mining.html', all_entries=all_entries, score = [score])

@app.route('/')
def main() :
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
