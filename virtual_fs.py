import os
import zipfile


class VirtualFileSystem:
    def __init__(self, archive_path):
        try:
            self.archive = zipfile.ZipFile(archive_path, 'r')
        except Exception as e:
            print(f"Error loading zip archive: {e}")
            self.archive = None

        self.current_path = '/'
        self.deleted_items = set()

    def list_directory(self):
        if not self.archive:
            return []

        # Ensure the path is consistent: no leading slash, and ends with '/'
        path = self.current_path.lstrip('/').rstrip('/')
        if path:
            path += '/'

        files = set()
        print(f"Deleted items: {self.deleted_items}")
        for file in self.archive.namelist():
            if file.startswith(path):
                rel_path = file[len(path):].strip('/')
                if '/' not in rel_path and rel_path:
                    # Construct full item path without leading/trailing slashes
                    full_item_path = os.path.join(path, rel_path).replace('\\', '/').rstrip('/')
                    print(f"Full item path: '{full_item_path}'")
                    if full_item_path not in self.deleted_items:
                        files.add(rel_path)

        return sorted(files)

    def change_directory(self, path):
        if path == '.':
            return True
        if path == '/':
            self.current_path = '/'
            return True

        # Normalize the new path and ensure consistency
        new_path = os.path.normpath(os.path.join(self.current_path, path))
        new_path = new_path.replace('\\', '/').rstrip('/').lstrip('/')
        if new_path:
            new_path += '/'

        if self.directory_exists(new_path.rstrip('/')):
            self.current_path = '/' + new_path  # For display purposes
            return True
        else:
            return False

    def get_current_path(self):
        return self.current_path.rstrip('/')

    def directory_exists(self, path):
        # Ensure the path is consistent
        path = path.rstrip('/').lstrip('/')
        print(f"Checking directory exists for path: '{path}'")
        if path in self.deleted_items:
            return False
        for file in self.archive.namelist():
            if file.startswith(path + '/'):
                return True
        return False

    def file_exists(self, path):
        path = path.lstrip('/').rstrip('/')
        if path in self.deleted_items:
            return False
        if path in self.archive.namelist():
            return True
        return False

    def read_file(self, file_name):
        full_path = os.path.normpath(os.path.join(self.current_path, file_name)).replace('\\', '/').lstrip('/').rstrip('/')
        if full_path in self.deleted_items:
            return f"cat: {file_name}: No such file"

        if full_path in self.archive.namelist():
            with self.archive.open(full_path) as file:
                content = file.read().decode('utf-8')
                return content
        else:
            return f"cat: {file_name}: No such file"

    def remove_directory(self, path):
        full_path = os.path.normpath(os.path.join(self.current_path, path))
        full_path = full_path.replace('\\', '/').rstrip('/').lstrip('/')

        if not self.directory_exists(full_path):
            return False, "No such directory"

        # Check if the directory is empty
        contents = [f for f in self.archive.namelist() if f.startswith(full_path + '/') and f != full_path + '/']
        contents = [f for f in contents if f not in self.deleted_items]

        if contents:
            return False, "Directory not empty"

        # Simulate deletion by adding to deleted_items
        self.deleted_items.add(full_path)
        return True, ""

    def remove_file(self, path):
        full_path = os.path.normpath(os.path.join(self.current_path, path))
        full_path = full_path.replace('\\', '/').rstrip('/').lstrip('/')

        if not self.file_exists(full_path):
            return False, "No such file"

        # Simulate deletion by adding to deleted_items
        self.deleted_items.add(full_path)
        return True, ""

    def get_tree(self, path=None, prefix=''):
        if path is None:
            path = self.current_path
        path = path.rstrip('/').lstrip('/')
        tree = ''
        items = self.list_directory()

        for index, item in enumerate(items):
            connector = '└── ' if index == len(items) - 1 else '├── '
            tree += prefix + connector + item + '\n'
            sub_path = os.path.join(path, item).replace('\\', '/').rstrip('/').lstrip('/')

            if self.directory_exists(sub_path):
                extension = '    ' if index == len(items) - 1 else '│   '
                tree += self.get_tree('/' + sub_path, prefix + extension)

        return tree
