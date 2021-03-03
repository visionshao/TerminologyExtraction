import collections
from information_extraction_main_system.function_box import *
from information_extraction_main_system.pattern.Method_Regex import *
from information_extraction_main_system.extractors.BaseMethodExtractor_new import *


class IESystem:

    def __init__(self, init_patterns: dict, ):

        # 新类型的新pattern（非规范化）
        self.new_type_patterns = list()
        # 旧类型的新pattern（规范化）
        self.new_patterns = list()
        # 得到的术语的词性序列
        self.target_pos = []
        # 系统状态
        self.state = dict()
        # dict，初始模板
        self.init_patterns = init_patterns
        # 初始抽取器
        self.method_extractor = MethodExtractor(init_patterns.values())
        # 规范后的pattern
        self.new_formed_patterns = list()

    def form_patterns(self):
        patterns = []
        for pattern, pattern_pos in self.new_type_patterns:
            temp_pattern = []
            for i, token in enumerate(pattern):
                if token != "<ITEM_PADDING>" and token != "<PADDING>" and token not in ["(", ")"]:
                    # 防止句式中的原生正则字符干扰
                    temp_pattern.append(token.replace("(", "").replace(")", "").replace("*", "").replace("[", "").replace("]", ""))
                if token == "<ITEM_PADDING>":
                    if i == len(pattern)-1 or pattern[i+1] != "<ITEM_PADDING>":
                        temp_pattern.append("(.+?)")
                if token == "<PADDING>":
                    if i == len(pattern)-1 or pattern[i+1] != "<PADDING>":
                        temp_pattern.append(".+?")
            temp_pattern = " ".join(temp_pattern)
            # print(temp_pattern)
            # print(pattern_pos)
            patterns.append(temp_pattern)
        self.new_formed_patterns = list(set([p[0] for p in self.new_patterns] + patterns))
        print(len(self.new_formed_patterns))

    def extract_entity(self, sentence_pos_dict, sentence, pos_sentence=None):

        extract_result = []
        if pos_sentence == None:
            # sentence 是字符串
            for pattern in self.new_formed_patterns:
                temp_regex = re.compile(pattern)
                match = temp_regex.match(sentence)
                if match:
                    # print("**********************************************")
                    # print(sentence)
                    # print(pattern)
                    for index in range(len(match.groups())):
                        m_string = match.groups()[index]
                        m_split = nlp.word_tokenize(m_string)
                        m_pos = [sentence_pos_dict[w] for w in m_split]
                        results = item_filter(m_split, m_pos)
                        # print(results)
                        extract_result += results
        else:
            # pos_sentence, sentence 是list，
            temp_list = []
            item_list = []
            copy_sentence = copy.copy(sentence)
            copy_sentence_pos = copy.copy(pos_sentence)
            for item_pos_list in self.target_pos:
                for idx, word, pos in zip(range(len(pos_sentence)), copy_sentence, copy_sentence_pos):
                    # print("length_temp_list: ", len(temp_list))
                    # print("length_item_pos_list: ", len(item_pos_list))
                    # 如果句子当前词性token和目标词性序列第一个token相同，且这是当前group的第一个token
                    if pos == item_pos_list[0] and len(temp_list) == 0:
                        temp_list.append(idx)
                        item_list.append(word)
                    # 如果词性相同，且词性token在句子中对应的id是要抽取的group的最新的id+1（保证连续性）
                    elif pos == item_pos_list[len(temp_list)] and idx == temp_list[-1] + 1:
                        temp_list.append(idx)
                        item_list.append(word)
                        # 如果从句子中抽取的当前group的长度和要匹配的词性序列长度相同，则匹配完毕
                        # 或者是当前句子已被匹配完，但是target pos sequence未被匹配完，也选择中断
                        if len(temp_list) == len(item_pos_list) or idx == (len(pos_sentence) -1):
                            extract_result.append(item_list)
                            temp_list = []
                            item_list = []
                    else:
                        temp_list = []
                        item_list = []
            # print(pos_sentence)
            # print(sentence)
            # print(extract_result)
            # print("------------------------------------")
        return extract_result

    def cool_start(self, data):
        # get data
        sentences_list = data["sentenize_abstracts"]
        pos_cut_abstracts = data["pos_cut_abstracts"]
        # get regexes, the regexes could be extended
        original_regexes = list(self.init_patterns.values())
        extend_regexes = []
        method_extractor = MethodExtractor(MethodPatterns.values())

        # 第一次处理
        init_extracted_sentence_list, init_unextracted_sentence_list, flag_0, flag_1 = \
            init_extract(method_extractor, sentences_list, pos_cut_abstracts)
        # 对词性序列pattern排序
        init_extracted_pos_list = sort_init_extracted_pos_list(flag_0, flag_1)
        # 开始迭代
        unextracted_sentence_list = copy.copy(init_unextracted_sentence_list)
        extracted_sentence_list = copy.copy(init_extracted_sentence_list)
        new_extracted_pos_list = copy.copy(init_extracted_pos_list)
        self.target_pos.extend(new_extracted_pos_list)
        for it in range(5):
            unextract_sentence_number = len(unextracted_sentence_list)

            new_pattern_match_count, new_pattern_match_strings, new_pattern_info, sentence_with_pos_words_pos = \
                iterate(unextracted_sentence_list, new_extracted_pos_list, extracted_sentence_list, original_regexes)
            # 过滤 得到的新pattern（同类型）
            extend_regexes, new_patterns = filter_new_patterns(unextract_sentence_number, 500, extend_regexes,
                                                               new_pattern_info, new_pattern_match_count)
            #
            new_extracted_pos_list = filter_new_extracted_pos_list(new_pattern_match_strings, 1)
            # 获取新类型的pattern
            new_type_patterns = get_patterns(sentence_with_pos_words_pos)
            # 从抽取结果中取出学术名词
            new_extracted_words = get_words(new_pattern_match_strings)

            # self.new_type_patterns.extend(new_type_patterns)
            self.new_patterns.extend(new_patterns)
            self.target_pos.extend(new_extracted_pos_list)

        self.target_pos = sorted(collections.Counter(self.target_pos).items(), key=lambda x: x[1], reverse=True)
        self.target_pos = [item[0].split() for item in self.target_pos if item[1] > 2]

        for sentence, pos_sentence, sentence_words, pos_dict in tqdm.tqdm(unextracted_sentence_list + extracted_sentence_list):
            for pos_item in self.target_pos:
                new_pattern, new_pattern_pos = system_get_pattern(pos_item, sentence_words, pos_sentence)
                self.new_type_patterns.append((new_pattern, new_pattern_pos))







