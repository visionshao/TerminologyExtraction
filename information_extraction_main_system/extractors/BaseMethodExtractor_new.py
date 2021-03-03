import re


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
                    m_string = match.groups()[index]
                    s = match.start(index)
                    e = match.end(index)
                    er = ExtractResult(s, e, text, flag, m_string, pos_dict)
                    ers.append(er)
        return ers





#
#
# flag_1 = []
# flag_0 = []
# extracted_sentence_list = []
# unextracted_sentence_list = []
# for sentence_list, pos_cut_abstract in zip(sentences_list, pos_cut_abstracts):
#     for sentence, pos_sentence in zip(sentence_list, pos_cut_abstract):
#         # print(pos_sentence)
#         pos_dict = dict(pos_sentence)
#         # print(pos_dict)
#         # 抽取句子
#         rs = method_extractor.extract(sentence, pos_dict)
#         if len(rs) > 0:
#             for r in rs:
#                 strings = r.matched_string
#                 # print(strings)
#                 match_list = nlp.word_tokenize(strings)
#                 # print(match_list)
#                 # 提取去除标点后的词性标注结果
#                 temp_pos_list = [pos_dict[word] for word in match_list]
#                 # print(temp_pos_list)
#                 filter_methods = filter(match_list, temp_pos_list)
#                 # 从过滤后的方法词中选择pattern
#                 for i, filtered_m in enumerate(filter_methods):
#                     # pattern需要有一定长度
#                     # 包含字符控制的
#                     # if len(filtered_m[0]) > 2:
#                     #     start_strings = r.matched_string.strip(";").strip(",").strip(".").split(" ")[0]
#                     #     end_strings = r.matched_string.strip(";").strip(",").strip(".").split(" ")[-1]
#                     #     char_feature = " "
#                     #     if start_strings != "" and end_strings != "":
#                     #         char_feature = start_strings + "---" + end_strings
#                     #     if r.flag == 1:
#                     #         flag_1.append([" ".join(filtered_m[1]), char_feature])
#                     #     else:
#                     #         flag_0.append([" ".join(filtered_m[1]), char_feature])
#                     # 不含字符控制的
#                         if r.flag == 1:
#                             flag_1.append(" ".join(filtered_m[1]))
#                         else:
#                             flag_0.append(" ".join(filtered_m[1]))
#
#             extracted_sentence_list.append([sentence, pos_sentence])
#         else:
#             unextracted_sentence_list.append([sentence, pos_sentence])
#
# print(len(extracted_sentence_list))
# print(len(unextracted_sentence_list))
# # 包含字符控制的
# # flag_0_char_feature_count =collections.Counter([item[1] for item in flag_0])
# # flag_1_char_feature_count = collections.Counter([item[1] for item in flag_1])
# # flag_0 = [[item[0], item[1], flag_0_char_feature_count[item[1]]]for item in flag_0]
# # flag_1 = [[item[0], item[1], flag_1_char_feature_count[item[1]]]for item in flag_1]
# # flag_0 = sorted(flag_0, key=lambda x: x[2], reverse=True)
# # flag_1 = sorted(flag_1, key=lambda x: x[2], reverse=True)
# # 不含字符控制
# flag_0_count = collections.Counter(flag_0)
# flag_1_count = collections.Counter(flag_1)
# flag_0 = sorted(flag_0_count, key=lambda x: x[1], reverse=True)
# flag_1 = sorted(flag_1_count, key=lambda x: x[1], reverse=True)
# flag_0 = flag_0[:int(len(flag_0)/20)]
# flag_1 = flag_1[:int(len(flag_1)/20)]
# flags = flag_0 + flag_1
#
# print(len(flags))
# # 遍历未抽取的句子，选择新的pattern
# new_string_pool = set()
# new_pattern_match_count = dict()
# new_pattern_match_strings = dict()
# new_pattern_info = dict()
# for sentence, pos_sentence in tqdm.tqdm(unextracted_sentence_list):
#     pos_dict = dict(pos_sentence)
#     pos_string = " ".join([item[1] for item in pos_sentence])
#     sentence_words = [item[0] for item in pos_sentence]
#     candidate_words = [sentence_words[i] for i in range(len(pos_sentence)) if pos_sentence[i][1][:1] == "V"]
#     # 能够匹配的词性组合list
#     candidate_flags = [flag for flag in flags if flag in pos_string]
#     # 如果可以匹配
#     if len(candidate_flags) > 0:
#         candidate_patterns = [[pattern.replace(extend, candidate_word), regex_flag, candidate_word] for pattern, regex_flag, extend in all_regexes for candidate_word in candidate_words]
#         # print(len(candidate_patterns))
#         match_flag = False
#         for candidate_pattern, regex_flag, candidate_word in candidate_patterns:
#             if candidate_pattern not in new_pattern_match_count:
#                 new_pattern_match_count[candidate_pattern] = 0
#                 new_pattern_info[candidate_pattern] = [regex_flag, candidate_word]
#                 new_pattern_match_strings[candidate_pattern] = []
#             match = re.compile(candidate_pattern).match(sentence)
#             if match:
#                 match_flag = True
#                 new_pattern_match_count[candidate_pattern] += 1
#
#                 m_string = match.groupdict()["method"]
#
#                 match_words = nlp.word_tokenize(m_string)
#                 try:
#                     match_pos = [pos_dict[word] for word in match_words]
#                     new_pattern_match_strings[candidate_pattern] += match_pos
#                     new_string_pool.add(m_string)
#                 except(Exception):
#                     print(m_string)
#                     print(match_words)
#                     print(pos_sentence)
#
#         if match_flag:
#             extracted_sentence_list.append([sentence, pos_sentence])
#             unextracted_sentence_list.remove([sentence, pos_sentence])
#
#
# print(len(extracted_sentence_list))
# print(len(unextracted_sentence_list))
# # 质量检测
# # 保留抽取到0.5%的
# threshold = int(len(unextracted_sentence_list) / 200)
# new_patterns = [[k, new_pattern_info[k][0], new_pattern_info[k][0]] for k, v in new_pattern_match_count.items() if v > threshold]
# all_regexes.extend(new_patterns)
#
#
#
#



