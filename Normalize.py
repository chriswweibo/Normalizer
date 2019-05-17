import json
import itertools
from flatten_json import flatten
from flatten_json import unflatten_list


# 获取JSON文件
#json_path='D:/Normalize/北肿tests.JSON'
#norm_path='D:/Normalize/normalize.txt'

#json_path = "GuangDongShengRenMinYiYuan提交文件20190408.xlsx_ID"
#dat = json.load(open(path + str(json_path) + ".json", 'r', encoding='UTF-8'))
#df = pd.DataFrame((flatten(d) for d in dat))


# 获取标识符所在的行号
def col_number(norm_path):
    with open(norm_path, 'r') as f:
        Num = []
        count = 0
        for (num, value) in enumerate(f):
            count += 1
            if "&&&" in value:
                Num.append(num)
        Num.append(count)
    return Num

#归一化
def Normalize(json_path,norm_path):
    dat=json.load(open(json_path, 'r', encoding='UTF-8'))
    Num = col_number(norm_path)
    result_delete = []
    result_absolute = []
    result_relative = []
    with open(norm_path, 'r') as f:
        for (num, value) in enumerate(f):
            if num > Num[0] and num < Num[1]:
                result_delete.append(list(value.strip('\n').split('@@')))
            elif num > Num[1] and num < Num[2]:
                result_absolute.append(list(value.strip('\n').split('@@')))
            elif num > Num[2]:
                result_relative.append(list(value.strip('\n').split('@@')))
        result_delete = list(itertools.chain.from_iterable(result_delete))
        result_absolute = list(itertools.chain.from_iterable(result_absolute))
        result_relative = list(itertools.chain.from_iterable(result_relative))
        # 删除键值对
        Arr_delete = []
        for d in dat:
            temp = flatten(d, separator='%%%')
            for key in list(temp.keys()):
                for value in result_delete:
                    temp_1 = value.split(':')
                    if key.endswith(temp_1[0]):
                        if temp[key] == temp_1[1]:
                            del temp[key]
            Arr_delete.append(temp)
        # 绝对文本替换
        Arr_absolute = []
        for i in range(0, len(Arr_delete)):
            temp = Arr_delete[i]
            for key, values in list(temp.items()):
                for value in result_absolute:
                    temp_1 = value.split('|')
                    if values == temp_1[0]:
                        temp[key] = temp_1[1]
                    elif key.split("%%%")[-1] == temp_1[0]:
                        key_temp = key.split("%%%")[0:-1] + [temp_1[1]]
                        temp["%%%".join(key_temp)] = values
                        del temp[key]
            Arr_absolute.append(temp)
        # 相对文本替换
        Arr_relative = []
        for i in range(0, len(Arr_absolute)):
            temp = Arr_absolute[i]
            for key, values in list(temp.items()):
                for value in result_relative:
                    temp_1 = value.split('|')
                    if key.endswith(temp_1[0][0:temp_1[0].rfind(':', 1)]) and values == temp_1[0][temp_1[0].rfind(':', 1) + 1:(len(temp_1[0]) + 1)]:temp[key] = temp_1[1]
            Arr_relative.append(temp)
    return Arr_relative


#转换成JSON格式
def Json_Normalize(json_path,norm_path):
    Normalize_result=Normalize(json_path,norm_path)
    result = []
    for i in range(0, len(Normalize_result)):
        temp = Normalize_result[i]
        result.append(unflatten_list(temp, separator='%%%'))
    #return result
    return json.dumps(result,indent=True,ensure_ascii=False)
    # for windows input
    # return json.dumps(result,indent=True,ensure_ascii=False).encode('UTF-8')

#测试
#json_path,norm_path='D:/肺癌多中心/吉大一院/JiDaYiYuan提交文件20190515.xlsx_ID.JSON','D:/肺癌多中心/吉大一院/normGuide20190514.txt'
#result=Json_Normalize(json_path,norm_path)
#f=open(json_path+'_norm.json','wb')
#f.write(result)
#f.close()
#print(result)
