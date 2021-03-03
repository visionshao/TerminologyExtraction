import re

class ParseResult:
    def __init__(self, er, value):
        self.er = er
        self.value = value


class MethodParser:

    def __init__(self, filt_dict):
        self.filt_dict = filt_dict

    def parse(self, er):
        string = er.matched_string
        string = " ".join(string.strip().split(" "))
        results = []
        # 抽取文本是宾语
        if er.flag == 0:
            string = er.matched_string
            # print(0, er.matched_string)
            # pass
        else:
            # 是否存在并列结构
            if "and" in string and "," in string:
                values = string.replace(":", ",").replace(";", ",").strip(",").split(",")
                # values = [value for value in values if not self.is_start(value)]
                for value in values:
                    # 除去无关内容
                    if not self.is_start(value):
                        # split_chunk_list = [value for value in value.split(" ") if value != ""]
                        # pos_list = [er.pos_dict[word] for word in split_chunk_list]
                        print(value)
                        # 除去成句内容
                        # 除去从句
                        if "that" in value or "which" in value:
                            if "that" in value:
                                flag = "that"
                            else:
                                flag = "which"
                            results.append(value[:value.find(flag)])
                            continue

                        if "and" in value:
                            parts = value.split("and")
                            if len(parts) == 2:
                                if "method" in parts[0] or "approach" in parts[0]:
                                    results += [parts[0], parts[1]]
                            else:
                                results += parts
                        else:
                            results.append(value)

                print(results)

                # print(values)
            else:
                # print(value)
                pass
            # pass

    def is_start(self, part):
        flag_words = ["To", "In the", "For this purpose", "Secondly", "In this", "In", "Then", "Second", "first",
                      "Specially", "Finally", "it is", "in order to", "Unlike", "in this", "Aiming at"]
        for flag in flag_words:
            if flag in part:
                return True
        return False