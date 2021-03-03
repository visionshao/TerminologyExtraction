import re
import json
from pattern.Method_Regex import *
from parsers.BaseMethodParser import *
import collections



class ExtractResult:
    def __init__(self, s_index, e_index, text, flag, matched_string, pos_dict):
        self.start = s_index
        self.end = e_index
        self.text = text
        self.length = e_index-s_index + 1
        self.flag = flag
        self.matched_string = matched_string
        self.pos_dict = pos_dict


class MethodExtractor:
    def __init__(self, patterns):
        self.patterns = patterns

    def extract(self, text, pos_dict):
        ers = []
        for pattern, flag, _ in self.patterns:
            temp_regex = re.compile(pattern)
            match = temp_regex.match(text)
            if match:
                m_string = match.groupdict()["method"]
                s = match.start("method")
                e = match.end("method")
                er = ExtractResult(s, e, text, flag, m_string, pos_dict)
                ers.append(er)
        return ers



all_regexes = MethodPatterns.values()
method_extractor = MethodExtractor(MethodPatterns.values())
method_parser = MethodParser(0)

DATA_PATH = r'D:\科研\文本信息\方法抽取小组\数据\原始数据\content_dic.json'
fp = open(DATA_PATH, "r", encoding="utf-8")
data = dict(json.load(fp))

sentences_list = data["sentenize_abstracts"]
pos_cut_abstracts = data["pos_cut_abstracts"]

flag_1 = []
flag_0 = []
extracted_sentence_list = []
unextracted_sentence_list = []

for sentence_list, pos_cut_abstract in zip(sentences_list, pos_cut_abstracts):
    for sentence, pos_sentence in zip(sentence_list, pos_cut_abstract):
        pos_dict = dict(pos_sentence)
        # 抽取句子
        rs = method_extractor.extract(sentence, pos_dict)
        if len(rs) > 0:
            for r in rs:
                strings = r.matched_string

                #提取去除标点后的词性标注结果
                pos_list = [v for v in r.pos_dict.values()]
                string_dic = ""
                # print(r.start)
                # print(r.end)
                # print(len(pos_list))

                for i in  range(len(pos_list)):
                    value = pos_list[i]
                    #if value != "," and value != "." and value != ":" and value != "":
                    string_dic = string_dic + " " + value
                #print(string_dic)

                #print(string_dic)

                if r.flag == 1:
                    flag_1.append(string_dic)
                else:
                    flag_0.append(string_dic)

            extracted_sentence_list.append([sentence, pos_sentence])
        else:
            unextracted_sentence_list.append([sentence, pos_sentence])

flag_0 = sorted(collections.Counter(flag_0).items(), key=lambda x: x[1], reverse=True)
flag_1 = sorted(collections.Counter(flag_1).items(), key=lambda x: x[1], reverse=True)
flag_0 = flag_0[:int(len(flag_0)/10)]
flag_1 = flag_1[:int(len(flag_1)/10)]
flags = flag_0 + flag_1

# print(len(flag_0))
# print(len(flag_1))
# print(len(extracted_sentence_list))

# for i in flags:
#     print(i)

# 遍历未抽取的句子

for sentence, pos_sentence in unextracted_sentence_list:
    exit = 0
    for flag, freq in flags:
            pos_string = ""
            for p in pos_sentence:
                pos_string = pos_string + " " + p[1]

                if flag in pos_string or pos_string in flag:
                    print(sentence)
                    exit = 1
                    break
            if exit == 1:
                break
    if exit == 1:
        continue




                # if "V" in pos:
                #     candidate_patterns = [pattern.replace(extend, candidate_word) for pattern, flag, extend in all_regexes]
                #     #print(candidate_patterns)
                #     for candidate_pattern in candidate_patterns:
                #         match = re.compile(candidate_pattern).match(sentence)
                #         if match:
                #             m_string = match.groupdict()["method"]
                #             # match质量检测
                #             # print("**"+m_string)
                #             print(sentence)
                #             break






