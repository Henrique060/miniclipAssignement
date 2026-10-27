import re
from collections import Counter
from checks.checks import Checks

class HeavyPriorityChecks(Checks):
    """
        Defines the Heavy-Priority checks to be run.
        These checks are mission-critical. The application is NOT to be deployed if one
        of these checks are triggered.
    """
    def __init__(self, current_ver, new_ver):
        super().__init__(current_ver, new_ver)
        self.feedback = list()

    def get_uuid_key_counter(self, doc_vers):
        """
        :param doc_vers : .plist document to check
        :return uuid_key_counter : the number of uuid keys

        Gets the UUID <key> number for each group of localisations.
        """
        uuid_keys = self.find_required_elements_xpath(doc_vers, 
                                                "/plist/dict/key[.='localisations']/following-sibling::dict[1]/key/text()")
        
        uuid_key_counter = 0
        for k in uuid_keys:
            uuid_key_counter += 1
        return uuid_key_counter
    

    def get_keys(self, doc_vers):
        """ 
         :param doc_vers : .plist document to check
         :return : a list of all key-tag objects

         Through an xpath query, fetches all key-tag objects.
           """
        return doc_vers.xpath("//key[following-sibling::*[1][self::string]][not(.='version')]")
    

    def set_feedback(self, mismatched=None, missing_pairs=None, erratic_entries=None):
        """ Fetches feedback and turns the results into readable lines. """
        for uuid, lang in missing_pairs or []:
            self.feedback.append(f"[{lang}] Empty translation in {uuid}")

        for entry in erratic_entries or []:
            lang = entry["key"]
            problem = entry.get("problem") or f"Malformed token '{entry['Token to be fixed']}'"
            lines = [f"[{lang}] {problem} in {entry['uuid']}",
                    f"    Text  : \"{entry['text']}\""]
            if "en_text" in entry:
                lines.append(f"    en-US : \"{entry['en_text']}\"")
            self.feedback.append("\n".join(lines))

        for lang, count, expected in mismatched or []:
            self.feedback.append(f"[{lang}] Count mismatch: found {count} entries, expected {expected}")

    def get_feedback(self):
        """ Returns feedback related to Low-Priority checks """
        return self.feedback
    

    def validate_key_loc_number(self, doc_vers, uuid_key_nr):
        """
        :param doc_vers : .plist document to check
        :param uuid_key_nr : number of key tags

        Validates the number of key-tags against the number of localisations per key-tag. 
        """
        lang_keys = self.find_required_elements_xpath(doc_vers, "//key[following-sibling::*[1][self::string]][not(.='version')]/text()")
        dict_to_count = dict(Counter(lang_keys))

        mismatched = list()
        for lang, count in dict_to_count.items():
            if count != uuid_key_nr:
                mismatched.append((lang, count, uuid_key_nr))

        return mismatched
    
    def validate_empty_string_loc(self):
        """
        Validates if any of the localisations is missing its text (empty translations).
        """
        missing_pairs = list()
        for key in self.get_keys(self.new_ver):
            val_elem = key.getnext()
            text = val_elem.text if val_elem is not None else None
            if not text or not text.strip():
                uuid = key.getparent().getprevious().text
                missing_pairs.append((uuid, key.text))
        return missing_pairs
        


    def get_list_key_strings(self, doc_vers):
        """
            :param doc_vers : .plist document to check
            :return list_key_strings: returns a list of strings for each localisation key

            Helper function that concatenates all strings into a list, for every localisation key there is.
        """
        list_of_keys = self.get_keys(doc_vers)
        list_key_strings = list()
        for key in list_of_keys:
            val_elem = key.getnext()
            val_text = val_elem.text if val_elem is not None else None
            list_key_strings.append((key.text, val_text))
        return list_key_strings
        
    
    def validate_erratic_placeholder(self):
        """
            Validates if there are any missing or erratic placeholders in the string.
            An erratic placeholder is defined as a placeholder that is missing the secondary symbol (eg., '%' alone).

            \nGets the list of placeholders and runs a detection against the present substrings. If not found the placeholder,
            flags it, alongside the string itself.
        """

        erratic_entries = list()

        valid_placeholder_pattern = re.compile(
            r"%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?(?:l{0,2}[diuxXfcs@]|%)"
        )
        erratic_placeholder_pattern = re.compile( #this regex will be used to find ONLY the %x symbols (placeholders)
            r"%(?![0-9$+\-#.]*l{0,2}[diuxXfcs@]|%)" #check % alone or followed by another % ("%%")
        )

        #Get the UUID nodes for each localisation key-tag
        uuid_dict_nodes = self.find_required_elements_xpath(self.new_ver, "/plist/dict/key[.='localisations']/following-sibling::dict[1]/dict")

        for dict_node in uuid_dict_nodes: #runs through all nodes in the dict of nodes
            uuid_key_node = dict_node.getprevious()
            uuid = uuid_key_node.text if uuid_key_node is not None else "Unknown UUID"

            lang_nodes = dict_node.xpath("./key")
            translations = {}
            for k in lang_nodes:
                val_node = k.getnext()
                translations[k.text] = val_node.text if val_node is not None else ""
            
            en_key = next((k for k in translations if k.startswith("en")), None) #default "None" for debugging purposes in the feedback
            en_text = translations.get(en_key, "") if en_key else ""

            en_tokens = Counter(valid_placeholder_pattern.findall(en_text))

            for key, text in translations.items():
                if not text: #if the string is empty, have to flag issue
                    continue

                broken_tokens = erratic_placeholder_pattern.findall(text) 
                for token in broken_tokens:
                    erratic_entries.append({"uuid" : uuid,
                                            "key" : key,
                                            "text": text,
                                            "en_text": en_text,
                                            "Token to be fixed": token})
                
                #now to compare against the english baseline 
                if en_key and key != en_key:
                    curr_tokens = Counter(valid_placeholder_pattern.findall(text))
                    missing_from_lang = en_tokens - curr_tokens
                    extra_in_lang = curr_tokens - en_tokens
                    if missing_from_lang or extra_in_lang:
                        problems = list()
                        if missing_from_lang:
                            problems.append(f"missing {list(missing_from_lang.elements())}")
                        if extra_in_lang:
                            problems.append(f"extra {list(extra_in_lang.elements())}")
                        erratic_entries.append({"uuid": uuid,
                                                "key": key,
                                                "text": text,
                                                "en_text": en_text,
                                                "problem": "Placeholder mismatch: " + ", ".join(problems)})
        return erratic_entries
