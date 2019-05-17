import pandas as pd
import numpy as np
import json
from tqdm import tqdm   
import io     

from flatten_json import flatten
import time
# 获取JSON文件
#Json_name="BeiJingZhongLiu提交文件20190408.xlsx_ID"
#dat=json.load(open(path + str(Json_name) + ".json",'r',encoding='UTF-8'))
#df=pd.DataFrame((flatten(d) for d in dat))
#df.columns.values.tolist()

    
#打印列名，去重
def Column_name(df):
    column_name=[]
    for value in df.columns.values.tolist():
        column_name.append(value.split("%%%")[-1])
    columns=list(set(column_name))
    return columns


#tt=list(set([s.split('_')[-1] for s in result.columns.values]))

#测试
#temp=Column_name(df)



#计算某一指标的完整性和各分类的个数
def Target(df,target):
    result = {}
    result["Index"] = target
    columns=df.columns.values.tolist()      
    col_target=[]
    for i in columns:
        if target == i.split("%%%")[-1]:
            col_target.append(i)
    
    df_result=df[col_target] #得到特定列
    #计算完整率
    nan_lines = df_result.isnull().all(1)
    complete=1-nan_lines.sum()/df_result.shape[0]
    #result["completeness"] = "%.2f%%" % (complete * 100)
    result["completeness"] = round(complete,4)
    #合并所有列
    Hebing=[]
    for i in range(0,df_result.shape[0]):
        temp=[]
        for j in range(0,df_result.shape[1]):
            if str(df_result.iloc[i,j])!= "nan":
                temp.append(df_result.iloc[i,j])
        #print(temp)
        Hebing.append('%%%'.join(list(set(temp))))
    hebing1='%%%'.join(list(set(Hebing))).split('%%%')
    hebing_end=list(filter(None, list(set(hebing1))))
    #统计每个分类的个数
    for value in hebing_end:
        k=0
        for V in Hebing:
            if value in V:
                k=k+1
        result[value] = k
    return result


#测试
#result_target=Target(end_result,"年龄")

#将字典存入list
def File_end(path):
    datas = []
    print('0')
    ####
    dat=json.load(io.open(path,'r',encoding='UTF-8'))
    df=pd.DataFrame((flatten(d, separator='%%%') for d in dat))
    ####
    print('a')
    Column_temp=Column_name(df)
    print('b')
    for value in tqdm(Column_temp):
        result_end=Target(df,str(value))
        datas.append(result_end)
    return datas
    
#测试
#Result_end=File_end("BeiJingZhongLiu提交文件20190408.xlsx_ID")


#转化为dataframe
def End(Json_name):
    df_end=pd.DataFrame()
    Result_end=File_end(Json_name)
    for row in Result_end:
        Index=row["Index"]
        Index=[Index]*len(row)
        temp=pd.DataFrame.from_dict(row, orient='index',columns=["freq"])
        temp=temp.reset_index().rename(columns={"index":"target"})
        temp.insert(0,'Index',Index)
        df_end=df_end.append(temp,ignore_index=True)
    data=df_end[-df_end.target.isin(["Index"])]
    return data



#测试
#path='D:/肺癌多中心/北肿/北肿提交文件测试_ycxu.xlsx_ID.JSON'
#data=End(path)
#data.to_csv(path+'_treat.csv',index=0)
#print(data[data.target.isin(["未知"])])