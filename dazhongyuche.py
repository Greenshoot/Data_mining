import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
import csv # 这个库是python自带的用来处理csv数据的库
# 读取csv数据文件
allElectronicsData = open('D:/设计论文/大众点评数据分析/大众点评（量化第二次）.csv', 'r')
reader = csv.reader(allElectronicsData) # 按行读取内容
headers=next(reader) #读取第一行的标题
# 对数据进行预处理，转换为字典形式
featureList = []
labelList = []

# 将每一行的数据编程字典的形式存入列表
for row in [rows for rows in reader]:
    # print(row)
    labelList.append(row[len(row) - 1]) # 存入目标结果的数据最后一列的
    rowDict = {}
    for i in range(1, len(row) - 1):
        # print(row[i])
        rowDict[headers[i]] = row[i]
        # print('rowDict:', rowDict)
    featureList.append(rowDict)
print(featureList)
from sklearn.feature_extraction import DictVectorizer
from sklearn import preprocessing

# 将原始数据转换成矩阵数据
vec=DictVectorizer()
dummyX=vec.fit_transform(featureList).toarray() # 将参考的列转化维数组

print('dummyX:'+str(dummyX))
print(vec.get_feature_names())

print('labellist:'+str(labelList))

# 将要预测的列转化为数组
lb=preprocessing.LabelBinarizer()
dummyY=lb.fit_transform(labelList)
print('dummyY:'+str(dummyY))
from sklearn import tree
# 创建决策树
clf=tree.DecisionTreeClassifier(criterion='entropy')#指明为那个算法
clf=clf.fit(dummyX,dummyY)
print('clf:'+str(clf))
# 直接导出为pdf树形结构
#import pydot
from sklearn.externals.six import StringIO
import pydotplus
dot_data = StringIO()
tree.export_graphviz(clf, out_file=dot_data)
# graph = pydot.graph_from_dot_data(dot_data.getvalue())
# graph[0].write_pdf("iris.pdf")
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
graph.write_pdf("mytree.pdf")
one=dummyX[3, :]
print('原第四组数据'+str(one))
new=one
new[1]=1
new[0]=0
# new[10]=1
# new[15]=0
# new[17]=1
# new[23]=0
print('测试数据'+str(new))
predictedY=clf.predict(new.reshape(-1,16))# 对新数据进行预测
print('预测结果:'+str(predictedY)) # 输出为predictedY:[0]，表示收入低，0表示低收入人群
# print('new'+str(new))
# predictedY=clf.predict(new.reshape(-1,11))# 对新数据进行预测
# print('predictedY:'+str(predictedY))