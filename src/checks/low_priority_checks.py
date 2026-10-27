from checks.checks import Checks

class LowPriorityChecks(Checks):
    """ Defines the Low-Priority checks to be run. 
        These checks serve as information regarding metadata, that is not 
        application critical, in a way that is assumed it does not break the
        application itself.
    """
    def __init__(self, current_ver, new_ver):
        super().__init__(current_ver, new_ver)
        self.feedback = list()

    def set_feedback(self, new_version=None, status=None, added_uuids = None):
        """
            :param new_version : version number found in the new .plist (first result of compare_version_number)
            :param status : "same" or "lower" (second result of compare_version_number)

            Builds the feedback messages for the Low-Priority checks, based on the detected_* flags.
        """
        if status == "same":
            self.feedback.append(f"In new file, version {new_version} is the same as the current live version")
        elif status == "lower":
            self.feedback.append(f"In new file, version {new_version} is lower than the current live version")
        elif status == "missing":
            self.feedback.append("No 'version' key found in one of the .plist files")
        
        if added_uuids:
            for uuid in added_uuids:
                self.feedback.append(f"UUID added in new version: '{uuid}'")


    def get_feedback(self):
        """ Returns feedback related to Low-Priority checks """
        return self.feedback
    
    def validate_key_diff(self):
        """
        Validates whether any UUID keys from the current version were dropped or added in the new version.
        """
        xpath_expr = "/plist/dict/key[.='localisations']/following-sibling::dict[1]/key/text()"
        
        current_keys = set(self.find_required_elements_xpath(self.current_ver, xpath_expr))
        new_keys = set(self.find_required_elements_xpath(self.new_ver, xpath_expr))
        
        added_keys = new_keys - current_keys
        
        return sorted(added_keys)
        
    
    def compare_version_number(self, xquery):
        """ 
        :param xquery: xpath query for version number fetching
        
        Fetches both .plist versions, current and new. 
        Filter out the dots (".") and compares the numbers,
        to find out if they are the same or if the new .plist is lower.
        """
        curr = self.find_required_elements_xpath(self.current_ver, xquery)
        new = self.find_required_elements_xpath(self.new_ver, xquery)

        if not curr or not new:
            return None, "missing"

        curr_t = tuple(int(n) for n in curr[0].split("."))
        new_t = tuple(int(n) for n in new[0].split("."))

        if new_t == curr_t:
            return new[0], "same"
        if new_t < curr_t:
            return new[0], "lower"
        return new[0], None
