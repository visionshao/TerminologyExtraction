import re
import json
from information_extraction_main_system.pattern.Method_Regex import *
from information_extraction_main_system.parsers.BaseMethodParser import *
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
                for index in range(len(match.groups())):
                    m_string = match.groups(index)
                    s = match.start(index)
                    e = match.end(index)
                    er = ExtractResult(s, e, text, flag, m_string, pos_dict)
                    ers.append(er)
        return ers

all_regexes = MethodPatterns.values()

method_extractor = MethodExtractor(MethodPatterns.values())
method_parser = MethodParser(0)

DATA_PATH = r'D:\PyCodes\Wos_IE\result\content_dic.json'
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
                start_strings = r.matched_string.strip(";").strip(",").strip(".").split(" ")[0]
                end_strings = r.matched_string.strip(";").strip(",").strip(".").split(" ")[-1]
                if start_strings != "" and end_strings != "":
                    if r.flag == 1:
                        flag_1.append(start_strings+"---"+end_strings)
                    else:
                        flag_0.append(start_strings+"---"+end_strings)
            extracted_sentence_list.append([sentence, pos_sentence])
        else:
            unextracted_sentence_list.append([sentence, pos_sentence])

flag_0 = sorted(collections.Counter(flag_0).items(), key=lambda x: x[1], reverse=True)
flag_1 = sorted(collections.Counter(flag_1).items(), key=lambda x: x[1], reverse=True)
flag_0 = flag_0[:int(len(flag_0)/10)]
flag_1 = flag_1[:int(len(flag_1)/10)]

# print(len(flag_0))
# print(len(flag_1))
# print(len(unextracted_sentence_list))

# 遍历未抽取的句子
for sentence, pos_sentence in unextracted_sentence_list:
    for flag, freq in flag_0:
        es = flag.split("---")
        # print(es)
        if es[0] in sentence.split(" ") and es[1] in sentence.split(" ") and sentence.find(es[0]) < sentence.find(es[1]):
            for candidate_word, pos in pos_sentence:
                if "V" in pos:
                    candidate_patterns = [pattern.replace(extend, candidate_word) for pattern, flag, extend in all_regexes]
                    for candidate_pattern in candidate_patterns:
                        match = re.compile(candidate_pattern).match(sentence)
                        if match:
                            m_string = match.groupdict()["method"]
                            # match质量检测
                            print(sentence)
                            print(m_string)







