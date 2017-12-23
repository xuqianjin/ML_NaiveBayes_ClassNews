# coding:utf-8
import pymongo
import numpy as np
import keras
import GetIfengNews
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib


def initDB():
    client = pymongo.MongoClient("localhost", 27017)
    db = client.python_data
    collection = db.data_collection
    source = collection.find()
    data = []
    for item in source:
        data.append(item)
    np.random.shuffle(data)
    return data


def getYdata(data):
    y_data = [item['tag'] for item in data]
    return y_data


def getXdata(data):
    x_data = [item['title'] for item in data]
    x_data = [' '.join(jieba.cut(item)) for item in x_data]
    return x_data


def getStopWords():
    stpwrdpath = "stop_words.txt"
    stpwrd_dic = open(stpwrdpath, 'rb')
    stpwrd_content = stpwrd_dic.read()
    # 将停用词表转换为list
    stpwrdlst = stpwrd_content.splitlines()
    stpwrd_dic.close()
    return stpwrdlst


if __name__ == '__main__':
    np.random.seed(10)
    class_to_int = GetIfengNews.getMap()  # 生成映射表
    int_to_class = {value: key for key, value in class_to_int.items()}
    trainNum = 0.8  # 训练测试比例
    data = initDB()
    stopwords = getStopWords()

    # 标题文本较短,不适宜用TFIDF处理文本
    # 用TF(词语在字典出现次数)
    x_data = getXdata(data)
    vectorizer = CountVectorizer(stop_words=stopwords)
    x_data = vectorizer.fit_transform(x_data).toarray()
    y_data = getYdata(data)
    y_data = [class_to_int[item] for item in y_data]  # 转化文字为整数

    # 分离测试和训练数据
    trainNum = int(len(x_data) * trainNum)
    x_train, y_train = x_data[:trainNum], y_data[:trainNum]
    x_test, y_test = x_data[trainNum:], y_data[trainNum:]

    model = MultinomialNB()
    model.fit(x_train, y_train)
    joblib.dump(model, 'my_model.model')
    pred = model.predict(x_test)
    right = 0
    wrong = 0
    for i in range(len(pred)):
        if (pred[i] == y_test[i]):
            right = right + 1
        else:
            wrong = wrong + 1
            # print(getXdata(data)[trainNum + i], '===>', getYdata(data)[trainNum + i], int_to_class[pred[i]])
    print('训练数据%d 测试数据%d  正确%d 错误%d 正确率%f' % (trainNum, len(x_data) - trainNum, right, wrong, right / (right + wrong)))
