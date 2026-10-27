from lxml import etree

class LoadLocDocs:
    def __init__(self, current_ver_path, new_ver_path):
        self.current_ver_path = current_ver_path
        self.new_ver_path = new_ver_path

    def get_current_ver(self):
        return etree.parse(self.current_ver_path)

    def get_new_ver(self):
        return etree.parse(self.new_ver_path)