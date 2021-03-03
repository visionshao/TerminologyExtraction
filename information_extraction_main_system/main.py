import tqdm
import json
import copy
import collections
from PATH.stanford_path import *
from information_extraction_main_system.utils import *
from information_extraction_main_system.pattern.Method_Regex import *
from information_extraction_main_system.extractors.BaseMethodExtractor_new import *
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(stanford_corenlp)


# 初始pattern抽取
def init_extract(extractor, sentences_list_, pos_cut_abstracts_):
    flag_1_ = []
    flag_0_ = []
    extracted_sentence_list_ = []
    unextracted_sentence_list_ = []
    for sentence_list, pos_cut_abstract in zip(sentences_list_, pos_cut_abstracts_):
        for sentence, pos_sentence in zip(sentence_list, pos_cut_abstract):
            pos_dict = dict(pos_sentence)
            # 抽取句子
            rs = extractor.extract(sentence, pos_dict)
            if len(rs) > 0:
                for r in rs:
                    strings = r.matched_string
                    match_list = nlp.word_tokenize(strings)
                    # 提取去除标点后的词性标注结果
                    temp_pos_list = [pos_dict[word] for word in match_list]
                    filter_methods = item_filter(match_list, temp_pos_list)
                    # 从过滤后的方法词中选择词性组合pattern
                    for i, filtered_m in enumerate(filter_methods):
                        # 词性组合pattern需要有一定长度
                        # 包含字符控制的
                        if len(filtered_m[0]) > 2:
                            if r.flag == 1:
                                flag_1_.append(" ".join(filtered_m[1]))
                            else:
                                flag_0_.append(" ".join(filtered_m[1]))

                extracted_sentence_list_.append([sentence, list(pos_dict.values()), list(pos_dict.keys()), pos_dict])
            else:
                unextracted_sentence_list_.append([sentence, list(pos_dict.values()), list(pos_dict.keys()), pos_dict])

    return extracted_sentence_list_, unextracted_sentence_list_, flag_0_, flag_1_


# 对初始的extracted_match_pos排序，这时主动被动分开排序，后面不分开
def sort_init_extracted_pos_list(flag_0, flag_1):
    flag_0_count = collections.Counter(flag_0)
    flag_1_count = collections.Counter(flag_1)
    flag_0 = sorted(flag_0_count, key=lambda x: x[1], reverse=True)
    flag_1 = sorted(flag_1_count, key=lambda x: x[1], reverse=True)
    flag_0 = flag_0[:int(len(flag_0) / 20)]
    flag_1 = flag_1[:int(len(flag_1) / 20)]
    flags = flag_0 + flag_1
    return flags


# 获取新类型的句式, 输入的是匹配成功的术语词性列表，句子，和句子词性序列
def get_new_pattern(item_pos_list, matched_sentence, matched_sentence_pos):

    temp_lists = []
    temp_list = []
    print("matched_sentence", matched_sentence)
    print("matched_sentence_pos", matched_sentence_pos)
    copy_sentence = copy.copy(matched_sentence)
    copy_sentence_pos = copy.copy(matched_sentence_pos)
    for idx, word, pos in zip(range(len(matched_sentence_pos)), copy_sentence, copy_sentence_pos):
        if pos == item_pos_list[0] and len(temp_list) == 0:
            temp_list.append(idx)
        elif pos == item_pos_list[len(temp_list)] and idx == temp_list[-1] + 1:
            temp_list.append(idx)
            if len(temp_list) == len(item_pos_list):
                for i in temp_list:
                    copy_sentence[i] = " "
                    copy_sentence_pos[i] = " "
                temp_lists.extend(temp_list)
                temp_list = []
        else:
            temp_list = []
    # print("temp_lists", temp_lists)
    # print("item_pos_list", item_pos_list)
    print("replaced_matched_sentence", copy_sentence)
    print("repalced_matched_sentence_pos", copy_sentence_pos)
    for i, word, pos in zip(range(len(copy_sentence),copy_sentence, copy_sentence_pos)):
        if pos in ["DT", "JJ", "NN"]:
            pass

    print("***********************************************************")


# 利用更多信息获取新类型句式
def get_patterns(sentence_with_pos_words_pos_):
    sorted_data = sorted(sentence_with_pos_words_pos_, key=lambda x: len(x[2]), reverse=True)
    candidate_data = sorted_data[:10]
    new_generated_patterns = []
    for sentence_words, pos_sentence, candidate_pos_list in candidate_data:
        print(sentence_words)
        print(pos_sentence)
        print("###################################################")
        copy_sentence = copy.copy(sentence_words)
        copy_sentence_pos = copy.copy(pos_sentence)
        for candidate_pos in candidate_pos_list:
            temp_list = []
            for idx, word, pos in zip(range(len(sentence_words)), sentence_words, pos_sentence):
                if pos == candidate_pos[0] and len(temp_list) == 0:
                    temp_list.append(idx)
                elif pos == candidate_pos[len(temp_list)] and idx == temp_list[-1] + 1:
                    temp_list.append(idx)
                    if len(temp_list) == len(candidate_pos):
                        for i in temp_list:
                            copy_sentence[i] = "<ITEM_PADDING>"
                            copy_sentence_pos[i] = "<ITEM_PADDING>"
                        temp_list = []
                else:
                    temp_list = []

        for idx, word, pos in zip(range(len(copy_sentence)), copy_sentence, copy_sentence_pos):
            if pos in ["RPP", "TO", "VB", "IN", "CC"]:
                continue
            elif pos in ["DT", "JJ", "NN", "NNS"]:
                copy_sentence_pos[idx] = "<PADDING>"
                copy_sentence[idx] = "<PADDING>"
        new_generated_patterns.append((copy_sentence, copy_sentence_pos))
    return new_generated_patterns


# 从一次迭代结果中获取学术名词
def get_words(new_pattern_match_strings_):
    return [[" ".join(single_result[0]), " ".join(single_result[1])] for pattern_result_ in
            new_pattern_match_strings_.values() for sentence_result in pattern_result_ for single_result in
            sentence_result if len(single_result[1]) > 2]


# 一次迭代
def iterate(unextracted_sentence_pool, new_extracted_pos_list, extracted_sentence_pool, original_regexes):
    # unextracted_sentence_pool: sentence_string, pos_sentence, pos_dict
    # 迭代的本质是依赖词性序列
    # 上一次得到的词性序列匹配新的sentence
    new_pattern_match_count = dict()
    new_pattern_match_strings = dict()
    new_pattern_info = dict()
    # 句子，词性，与句子对应的方法词及词性
    sentence_with_pos_extracted_pos = []
    for sentence, pos_sentence, sentence_words, pos_dict in tqdm.tqdm(unextracted_sentence_pool):
        pos_string = " ".join(pos_sentence)
        candidate_words = [sentence_words[i] for i in range(len(pos_sentence)) if pos_sentence[i][:1] == "V"]
        # candidate_pos_list = [new_extracted_pos for new_extracted_pos in new_extracted_pos_list
        #                    if new_extracted_pos in pos_string]
        candidate_pos_list = []
        for new_extracted_pos in new_extracted_pos_list:
            if new_extracted_pos in pos_string:
                # print(new_extracted_pos)
                # print(pos_sentence)
                candidate_pos_list.append(new_extracted_pos.split())

        sentence_with_pos_extracted_pos.append([sentence_words, pos_sentence, candidate_pos_list])

        # 如果可以匹配
        if len(candidate_pos_list) > 0:
            candidate_patterns = [[pattern.replace(extend, candidate_word), regex_flag, candidate_word] for
                                  pattern, regex_flag, extend in original_regexes for candidate_word in candidate_words]
            # print(len(candidate_patterns))
            match_flag = False
            for candidate_pattern, regex_flag, candidate_word in candidate_patterns:
                if candidate_pattern not in new_pattern_match_count:
                    new_pattern_match_count[candidate_pattern] = 0
                    new_pattern_info[candidate_pattern] = [regex_flag, candidate_word]
                    new_pattern_match_strings[candidate_pattern] = []
                match = re.compile(candidate_pattern).match(sentence)
                if match:
                    match_flag = True
                    new_pattern_match_count[candidate_pattern] += 1
                    m_string = match.groupdict()["method"]
                    match_words = nlp.word_tokenize(m_string)
                    try:
                        match_pos = [pos_dict[word] for word in match_words]
                        # get_new_pattern(match_pos, sentence_words, pos_sentence)
                        filter_results = item_filter(match_words, match_pos)
                        new_pattern_match_strings[candidate_pattern].append(filter_results)
                    except(Exception):
                        print(m_string)
                        print(match_words)
                        print(pos_sentence)

            if match_flag:
                extracted_sentence_pool.append([sentence, pos_sentence, sentence_words, pos_dict])
                unextracted_sentence_pool.remove([sentence, pos_sentence, sentence_words, pos_dict])
    return new_pattern_match_count, new_pattern_match_strings, new_pattern_info, sentence_with_pos_extracted_pos


# 过滤新得到的pattern
def filter_new_patterns(unextract_sentence_number, percent, extend_regexes, new_pattern_info, new_pattern_match_count):
    # unextract_sentence_number 是指迭代前未抽取句子的数量
    # 新pattern需要达到一定的抽取比例
    threshold = int(unextract_sentence_number / percent)
    new_patterns = [[k, new_pattern_info[k][0], new_pattern_info[k][1]] for k, v in new_pattern_match_count.items() if
                    v > threshold]
    extend_regexes.extend(new_patterns)
    return extend_regexes, new_patterns


def filter_new_extracted_pos_list(new_pattern_match_strings, percent):
    new_extracted_pos_count = collections.Counter([" ".join(single_result[1]) for pattern_result in \
        new_pattern_match_strings.values() for sentence_result in pattern_result for single_result in sentence_result \
                                                   if len(single_result[1]) > 2])
    sorted_new_extracted_count = sorted(new_extracted_pos_count, key=lambda x: x[1], reverse=True)
    new_pos_list = sorted_new_extracted_count[:int(len(sorted_new_extracted_count) / percent)]
    # print(new_pos_list[:10])
    return new_pos_list


if __name__ == '__main__':
    # open data file
    DATA_PATH = r'D:\Codes\Wos_IE\result\content_dic.json'
    fp = open(DATA_PATH, "r", encoding="utf-8")
    data = dict(json.load(fp))
    # get data
    sentences_list = data["sentenize_abstracts"]
    pos_cut_abstracts = data["pos_cut_abstracts"]
    # get regexes, the regexes could be extended
    original_regexes = list(MethodPatterns.values())
    extend_regexes = []
    method_extractor = MethodExtractor(MethodPatterns.values())

    # 第一次处理
    init_extracted_sentence_list, init_unextracted_sentence_list, flag_0, flag_1 = \
        init_extract(method_extractor, sentences_list, pos_cut_abstracts)
    # 对词性序列pattern排序
    init_extracted_pos_list = sort_init_extracted_pos_list(flag_0, flag_1)
    # 开始迭代
    unextracted_sentence_list = init_unextracted_sentence_list
    extracted_sentence_list = init_extracted_sentence_list
    new_extracted_pos_list = init_extracted_pos_list
    all_words = []
    for it in range(10):
        unextract_sentence_number = len(unextracted_sentence_list)

        new_pattern_match_count, new_pattern_match_strings, new_pattern_info, sentence_with_pos_words_pos = \
            iterate(unextracted_sentence_list, new_extracted_pos_list, extracted_sentence_list, original_regexes)
        # 过滤 得到的新pattern（同类型）
        extend_regexes, new_patterns = filter_new_patterns(unextract_sentence_number, 500, extend_regexes)
        # 
        new_extracted_pos_list = filter_new_extracted_pos_list(new_pattern_match_strings, 1)
        # 获取新类型的pattern
        new_type_patterns = get_patterns(sentence_with_pos_words_pos)
        # 从抽取结果中取出学术名词
        new_extracted_words = get_words(new_pattern_match_strings)
        all_words.extend(new_extracted_words)
    all_ = dict(all_words)
    print(len(all_))
    for k, v in all_.items():
        print(k)
        print(v)