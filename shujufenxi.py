import pandas as pd
from matplotlib import pyplot as plt
import jieba
data = pd.read_csv('data.csv')
data.head()


# 构建label值
def zhuanhuan(score):
    if score > 3:
        return 1
    elif score < 3:
        return 0
    else:
        return None


# 特征值转换
data['target'] = data['stars'].map(lambda x: zhuanhuan(x))
data_model = data.dropna()
# 切分测试集、训练集
from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(data_model['cus_comment'], data_model['target'], random_state=3,
                                                    test_size=0.25)

# 引入停用词
infile = open("stopwords.txt", encoding='utf-8')
stopwords_lst = infile.readlines()
stopwords = [x.strip() for x in stopwords_lst]


# 中文分词
def fenci(train_data):
    words_df = train_data.apply(lambda x: ' '.join(jieba.cut(x)))
    return words_df


x_train[:5]
#print(x_train[:5])
#使用TF-IDF进行文本转向量处理
from sklearn.feature_extraction.text import TfidfVectorizer
tv = TfidfVectorizer(stop_words=stopwords, max_features=3000, ngram_range=(1,2))
tv.fit(x_train)
#print(tv.fit(x_train))
#计算分类效果的准确率
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import roc_auc_score, f1_score
classifier = MultinomialNB()
classifier.fit(tv.transform(x_train), y_train)
classifier.score(tv.transform(x_test), y_test)
#print(classifier.score(tv.transform(x_test), y_test))
y_pred = classifier.predict_proba(tv.transform(x_test))[:,1]
roc_auc_score(y_test,y_pred)
#print(roc_auc_score(y_test,y_pred))
def ceshi(model,strings):
    strings_fenci = fenci(pd.Series([strings]))
    return float(model.predict_proba(tv.transform(strings_fenci))[:,1])
#从大众点评网找两条评论来测试一下
test1 = '很好吃，环境好，所有员工的态度都很好，上菜快，服务也很好，味道好吃，都是用蒸馏水煮的，推荐，超好吃' #5星好评
test2 = '糯米外皮不绵滑，豆沙馅粗躁，没有香甜味。12元一碗不值。' #1星差评
print('好评实例的模型预测情感得分为{}\n差评实例的模型预测情感得分为{}'.format(ceshi(classifier,test1),ceshi(classifier,test2)))
from sklearn.metrics import confusion_matrix
y_predict = classifier.predict(tv.transform(x_test))
cm = confusion_matrix(y_test, y_predict)
print(cm)
data['target'].value_counts()
#把0类样本复制10次，构造训练集
index_tmp = y_train==0
y_tmp = y_train[index_tmp]
x_tmp = x_train[index_tmp]
x_train2 = pd.concat([x_train,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp,x_tmp])
y_train2 = pd.concat([y_train,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp,y_tmp])
#使用过采样样本(简单复制)进行模型训练，并查看准确率
clf2 = MultinomialNB()
clf2.fit(tv.transform(x_train2), y_train2)
y_pred2 = clf2.predict_proba(tv.transform(x_test))[:,1]
roc_auc_score(y_test,y_pred2)
print(roc_auc_score(y_test,y_pred2))
#查看此时的混淆矩阵
y_predict2 = clf2.predict(tv.transform(x_test))
cm = confusion_matrix(y_test, y_predict2)
print(cm)
print(ceshi(clf2,'排队人太多，环境不好，口味一般'))
#使用SMOTE进行样本过采样处理
from imblearn.over_sampling import SMOTE
oversampler=SMOTE(random_state=0)
x_train_vec = tv.transform(x_train)
x_resampled, y_resampled = oversampler.fit_sample(x_train_vec, y_train)
#原始的样本分布
y_train.value_counts()
#print(y_train.value_counts())
#经过SMOTE算法过采样后的样本分布情况
pd.Series(y_resampled).value_counts()
#使用过采样样本(SMOTE)进行模型训练，并查看准确率
clf3 = MultinomialNB()
clf3.fit(x_resampled, y_resampled)
y_pred3 = clf3.predict_proba(tv.transform(x_test))[:,1]
roc_auc_score(y_test,y_pred3)
print(roc_auc_score(y_test,y_pred3))
#查看此时的准确率
y_predict3 = clf3.predict(tv.transform(x_test))
cm = confusion_matrix(y_test, y_predict3)
print(cm)
#到网上找一条差评来测试一下情感评分的预测效果
test3 = '糯米外皮不绵滑，豆沙馅粗躁，没有香甜味。12元一碗不值。'
ceshi(clf3,test3)
print(ceshi(clf3,test3))
#词向量训练
tv2 = TfidfVectorizer(stop_words=stopwords, max_features=3000, ngram_range=(1,2))
tv2.fit(data_model['cus_comment'])

#SMOTE插值
X_tmp = tv2.transform(data_model['cus_comment'])
y_tmp = data_model['target']
sm = SMOTE(random_state=0)
X,y = sm.fit_sample(X_tmp, y_tmp)

clf = MultinomialNB()
clf.fit(X, y)

def fenxi(strings):
    strings_fenci = fenci(pd.Series([strings]))
    return float(clf.predict_proba(tv2.transform(strings_fenci))[:,1])
#到网上找一条差评来测试一下
print(fenxi('糯米外皮不绵滑，豆沙馅粗躁，没有香甜味。12元一碗不值。'))