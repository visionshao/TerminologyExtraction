def rule_extraction(pos_sentence):
    result_list = []
    temp_result = []
    for i, (word, pos) in enumerate(pos_sentence):
        if pos[0] == "N":
            if len(temp_result) == 0:
                temp_result.append(word)
            else:
                if pos_sentence[i-1] == "N":
                    temp_result.append(word)
                if pos_sentence[i+1] !="N":
                    temp_result.append(word)
                    result_list.append(temp_result)
                    temp_result = []
    return result_list


def clean(pos_sentence):
    result_list = []
    print(pos_sentence)
    for i, (word, pos) in enumerate(pos_sentence):
        if pos[0] != "N" and pos[0] != "V":
            result_list.append("----")
        else:
            result_list.append(word)
    result_list = " ".join(result_list).split("----")
    result_list = [item.strip().split() for item in result_list if item.strip() != "" and len(item.strip().split()) > 1]
    return result_list