from checks.checks import Checks

class MidPriorityChecks(Checks):
    """
        Defines the Mid-Priority checks to be run.
        These checks serve as warnings. Although not critical, it is assumed that
        one of these passing would create UX issues (such as missing translations).
    """
    def __init__(self, current_ver, new_ver):
        super().__init__(current_ver, new_ver)
        self.feedback = list()

    def set_feedback(self, removed=None, added=None, deleted_uuids=None):
        """
            :param removed : languages removed in the new version (result of compare_unique_localisations)
            :param added : languages added in the new version (result of compare_unique_localisations)

            Builds the feedback messages for the Mid-Priority checks, based on the detected_* flags.
        """
        if removed:
            self.feedback.append(f"Missing language keys in the new version - {removed}")
            if added:
                self.feedback.append(f" ...and new language keys in the new version - {added}")
        elif added:
            self.feedback.append(f"New languages have been added in the new version (old ones intact) - {added}")
        
        if deleted_uuids:
            for uuid in deleted_uuids:
                self.feedback.append(f"UUID removed in new version: '{uuid}'")

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
        
        deleted_keys = current_keys - new_keys
        
        return sorted(deleted_keys)
    

    def compare_unique_localisations(self, xquery):
        """
            :param xquery: xpath query to find all <key> tags
            :return removed, added: items that have been both removed and added, in comparison to old .plist version

            Gets both current and new version of the .plist and fetches their keys.
            Runs comparisons in order to detect if localisations are missing in the new version, compared to the new version.
            Also detects in new localisations have been added, or, if a new one is present despite an old one being amiss.
        """
        curr_ver = set(self.find_required_elements_xpath(self.current_ver, xquery))
        new_ver = set(self.find_required_elements_xpath(self.new_ver, xquery))

        removed = sorted(curr_ver - new_ver) 
        added = sorted(new_ver - curr_ver)


        return removed, added