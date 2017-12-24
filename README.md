# 基于朴素贝叶斯的新闻分类

# 概述
本文是基于朴素贝叶斯的新闻分类,数据来源是[凤凰网](http://imil.ifeng.com)各个板块新闻,爬取了娱乐,社会,体育,科技,军事,历史,财经板块数据,源码可以修改爬取地址和总数,本文总共抓取了1200多条记录,每个分类平均200条,训练/测试=8/2
#环境依赖：

> * Windows
> * Keras 
> * TensorFlow
> * MongoDB

# python包赖:
> * pymongo 
> * requests
> * numpy
> * jieba
> * sklearn


> 上面的包都可以使用pip安装

------

# 数据抓取
这里只引出main函数
```python
if __name__ == '__main__':
    client = pymongo.MongoClient("localhost", 27017) #连接到mongo数据库
    db = client.python_data
    collection = db.data_collection #连接到名为data_collection的集合
    source = getProject() #获取新闻:地址映射表
    collection.remove({}) #删除本地数据(避免多次insert)
    for key, value in source.items(): #循环抓取取各个分类
        data = getNewsDataAll(key, page) #获取一个分类的数据 page表示页数 
        data = unique(data) #数据去重(爬去的数据很有可能有重复,会干扰训练,建议去除)
        collection.insert(data) #插入到本地数据库
```


# 数据预处理 
> * 需要将分类做char_to_int映射
> * 将数据标题栏进行jieba分词
> * 使用sklean提供的CountVectorizer统计词
> * 使用停用词(避免类似'这个','是''等高频但不影响主题的词语干扰训练)


分类转换成int类型是为了方便计算
输入数据库是一段文本,必须要使用jieba将文本转化为词语
这里为什么使用**CountVectorizer**而不是**TfidfVectorizer**?我用这两种都试过,发现TfidfVectorizer训练准确度不如CountVectorizer,大概问题是因为我们的新闻标题一般都是短文本,使用TFIDF的收效不大,如果是整篇文章的话,TFIDF会比较有效一点

# 开始训练
> * 将训练数据进行2/8分成,即80%的训练数据,20%的测试数据
> * 使用多项式朴素贝叶斯(贝叶斯公式这里不再赘述,基于Keras的贝叶斯使用很简单)
> * 训练完毕保存模型
> * 预测模型,算出准确度

```python

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
```
# 预测结果
    准确率为79%
# 进一步提高预测结果方法
    1.由于是抓取数据,依赖网页本身的标记,网页本身的归类可能就误差,如果有时间的话,人工check一把,修改分类标签,可以提高准确度
    2.部分分类科技和数码,本身界限就很模糊,这里可能导致预测误差
    3.娱乐版块和体育版块标题出现的经常是人名,这对机器本身是陌生词,而人本身对名人较为熟悉.例如标题一提到 周杰伦  三个字,分类是娱乐版块的概率应该较大,但是系统却不敏感

# TODO 
  接下来会做一个斗鱼/虎牙的弹幕过滤,屏蔽那些喷子的弹幕.做好之后也会上传GitHub
