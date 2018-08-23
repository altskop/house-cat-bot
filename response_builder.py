import re
import random


class ResponseBuilder:
    def __init__(self, config):
        self.config = config
        self.dictionary = self.read_templates("dictionary.locale")
        self.message_templates = self.read_templates("messages.locale")

    def get_response(self, key):
        return self.build_response(random.choice(self.message_templates.get(key)))

    def build_response(self, string):
        pattern = re.compile("%[A-Z]+")
        # here we will substitute every %WORD occurrence from string with actual choices from dictionary or responses
        for (word) in re.findall(pattern, string):
            string = string.replace(word, random.choice(self.dictionary.get(word[1:])))
            # print(word)

        # Capitalize first letter
        string = string[0].upper() + string[1:]
        return string

    def truncate_mentions(self, msg):

        mention_pattern = re.compile("(<@!*\d+>\s*)")
        new_text = msg
        new_text = re.sub(mention_pattern, '', new_text)
        new_text = self.cleanup_spaces(new_text)
        return new_text

    def msg_fits_template(self, key, msg):

        any_pattern = re.compile("[a-zA-z]")

        for template in self.message_templates.get(key):
            remain = msg
            template_word_list = re.sub("[^\S]", " ", template).split()
            for (word) in template_word_list:
                if word[:1] == "%":
                    for (dict_word) in self.dictionary.get(word[1:]):
                        word_pattern = re.compile("^\W*("+dict_word+")")
                        if word_pattern.match(remain):
                            #print("Found occurence of "+word+" in \""+remain+"\"")
                            remain = re.sub(word_pattern, '', remain)
                            remain = self.cleanup_spaces(remain)
                            #print("new string "+remain)
                    if not any_pattern.search(remain):
                        return True
                else:
                    word_pattern = re.compile("^\W*(" + word + ")")
                    if word_pattern.match(remain):
                        #print("Found occurence of " + word + " in \"" + remain + "\"")
                        remain = re.sub(word_pattern, '', remain)
                        remain = self.cleanup_spaces(remain)
                        #print("new string " + remain)
                if not any_pattern.search(remain):
                    return True
        return False

    def cleanup_spaces(self, string):
        if string[-1:] == " ":
            string = string [:-1]
        return ' '.join(string.split())

    def read_templates(self, filename):
        responses = {}
        tag_pattern = re.compile("\[[A-Z-?]+\]")
        with open("locale/" + filename, "r") as file:
            lines = [line.rstrip('\n') for line in file]
            current_tag = ""
            current_list = []
            for line in lines:
                if len(line) > 0:
                    if tag_pattern.match(line):
                        '''NEW TAG found'''
                        current_tag = line[1:-1]
                    else:
                        current_list.append(line)
                else:
                    '''Empty line found. Used as a separator between modules. Save the list to dictionary'''
                    current_list.sort(key=len, reverse=True)
                    responses[current_tag] = current_list
                    current_tag = ""
                    current_list = []

            if current_tag != "":
                current_list.sort(key=len, reverse=True)
                responses[current_tag] = current_list

        # print("DEBUG: "+filename+" contents")
        # print(responses)
        return responses
