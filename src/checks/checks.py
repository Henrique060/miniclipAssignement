class Checks:
    def __init__(self, current_ver, new_ver):
        self.current_ver = current_ver
        self.new_ver = new_ver

    def find_required_elements_xpath(self, doc_vers, xpath_query):
        return doc_vers.xpath(xpath_query)
    

     