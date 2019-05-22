import re
from collections import Counter


from data_preprocess import sci_term_replacer, lemmatizer, stop_words_set

class PhraseExtractor:
    '''
    Takes in the list of dictionaries of a format:
    [{orcid:str, n_papers:int, data:str}].
    Returns list of dictionaries with phrases and frequencies of their appearance of a format:
    {'ORCID':orcid, 'TOPICS':[{'key':phrase, 'value':frequency}]}

    Empty documents returned as empty dictionaries.
    Order is preserved.
    '''
    def __init__(self, docs:list):
        self.docs = docs
        self.rgx_trim = re.compile('^\s+|[(),]+|\s+$')  # from fun get_key_phrases  #trims heading and trailing spaces, brackets and comas
        self.unwanted_chars = {'_': ' ', r'\ba ': '', '\.': ''}  # from fun replace_unwanted_chars

    def result(self) -> list:
        output = []
        for doc in self.docs:
            sw, ph = self.process_data(doc['data'])
            if ph != []:
                #piped everyting to make things faster
                result = self.replace_unwanted_chars(self.remove_single_vals(self.get_key_phrases(doc['n_papers'], search_words = sw, phrases = ph)))
                result = [{'key': key, 'value': val} for key, val in result.items()] #transform to form suitable for mongodb
            else:
                result = []
            output.append({'ORCID':doc['orcid'], 'TOPICS':result})

        return output


    def process_data(self, doc:str) -> (list,list):
        if doc == '':
            return [],[]
        else:
            #processing data part 1
            data_str = doc.lower() #bring to lowercase
            data_str = sci_term_replacer(data_str) #repalce some terms and characters
            phrases = data_str.split(';') #split string into list of phrases
            phrases = [self.rgx_trim.sub('',i) for i in phrases] #trim all the tokens using compiled regexp
            phrases = [i for i in phrases if i != ''] #delete empty elements of the list
            result_phrases = []
            result_search_words = []
            #processing part 2
            for ph in phrases:
                split_ph = ph.split(' ') #split phrases into list of words
                split_ph = [lemmatizer.lemmatize(i) for i in split_ph if self.not_digit(i)]# trim words to the base dictionary forms
                phrases_li = split_ph.copy()
                search_word = [i for i in split_ph if i not in stop_words_set]# remove stop words from tokens
                if search_word != None:
                    result_search_words.extend(search_word)
                    phrases_str = ' '.join(phrases_li) #join list of words back into phrases
                    if len(phrases_str) > 50: #if length of phrase is more than 50 chracters, split it into separate words
                        result_phrases.extend(phrases_str.split(' '))
                    else:
                        result_phrases.append(phrases_str)
                else:
                    return [],[]
            return result_search_words, result_phrases


    def get_key_phrases(self, n_papers:int, search_words:list, phrases:list) -> dict:
        if n_papers == 0 or search_words == []:
            return {}

        topic_number = (n_papers*2)//10

        if topic_number < 10:
            topic_number = 10

        sw_counted = Counter(search_words) #count frequency of appearance of search words
        sw_top = sw_counted.most_common(topic_number) #pick top search words

        ph_counted = Counter(phrases) #count frequency of appearance of phrases
        #ph_top = ph_counted.most_common(topic_number)

        output = {}
        for w in sw_top:
            search_word = w[0]
            #check if pharse contains search word
            #if yes add value of ph_counted to matches
            matches = {key:val for key,val in ph_counted.items() if search_word in key}
            sum_matches = sum(matches.values()) #sum of frequencies of matched pharses
            
            #for each mathced phrase check if it contributes >= 10% to the sum of matches
            output_before = len(output)
            for element in matches:
                if (matches[element]/sum_matches) >= 0.1:
                    output[element] = matches[element]
            output_after = len(output)

            if output_after == output_before:
                output[w[0]] = w[1]


        result_dict = {}
        for w in sorted(output, key = output.get, reverse = True):
            result_dict[w] = output[w]


        return result_dict

    def replace_unwanted_chars(self, data:dict) -> dict:
        input_data = data
        for ch, subs in self.unwanted_chars.items(): #unwanted_chars specified in the __init__
            input_data = {re.sub(ch,subs,key):val for key,val in input_data.items()}
        return input_data


    def remove_single_vals(self, data:dict) -> dict: #remove single words from dict if they are also found in other phrases
        input_data = data
        input_data = {key:val for key,val in input_data.items() if len(key) > 1} #remove single letters
        single_word_dict = {}
        
        for i in input_data: #get single words
            matched = re.search('^\w+$',i)
            if matched != None:
                single_word_dict[matched.group()] = 0

        for phrase in input_data:#match single words to other words
            for word in single_word_dict:
                if word in phrase:
                    single_word_dict[word] += 1 #increment number of matches for each successful match

        single_word_dict = {key:val for key,val in single_word_dict.items() if val > 1}
        input_data = {key:val for key, val in input_data.items() if key not in single_word_dict}

        return input_data

    def not_digit(self, string:str) -> bool:
        return not string.replace('.','',1).isdigit()