import xml.etree.ElementTree as ET
from datetime import datetime

class ActionLogger:
    def __init__(self, log_path, user):
        self.log_path = log_path
        self.user = user
        self.root = ET.Element('session')

    def log_action(self, action):
        entry = ET.SubElement(self.root, 'action')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(entry, 'user').text = self.user
        ET.SubElement(entry, 'time').text = timestamp
        ET.SubElement(entry, 'command').text = action

    def close(self):
        tree = ET.ElementTree(self.root)
        tree.write(self.log_path, encoding='utf-8', xml_declaration=True)
