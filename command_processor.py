class CommandProcessor:
    def __init__(self, vfs, logger):
        self.vfs = vfs
        self.logger = logger

    def process_command(self, command):
        args = command.strip().split()
        if not args:
            return ''
        cmd = args[0]

        print(f"Executing command: {cmd}")  # Отладка
        if cmd == 'ls':
            return self.ls()
        elif cmd == 'cd':
            return self.cd(args[1] if len(args) > 1 else '/')
        elif cmd == 'pwd':
            return self.pwd()
        elif cmd == 'tree':
            return self.tree()
        elif cmd == 'cat':
            return self.cat(args[1] if len(args) > 1 else '')
        elif cmd == 'rmdir':
            return self.rmdir(args[1] if len(args) > 1 else '')
        elif cmd == 'exit':
            return ''
        else:
            return f"{cmd}: command not found"

    def ls(self):
        files = self.vfs.list_directory()
        print(f"Files in directory: {files}")  # Отладка
        return '\n'.join(files)

    def cd(self, path):
        if self.vfs.change_directory(path):
            return ''
        else:
            return f"cd: {path}: No such file or directory"

    def pwd(self):
        return self.vfs.get_current_path()

    def tree(self):
        tree_str = self.vfs.get_tree()
        print(f"Directory tree:\n{tree_str}")  # Отладка
        return tree_str.strip()

    def cat(self, file_name):
        if file_name:
            content = self.vfs.read_file(file_name)
            return content
        else:
            return "cat: missing file name"

    def rmdir(self, path):
        if not path:
            return "rmdir: missing operand"
        success, message = self.vfs.remove_directory(path)
        if success:
            return ''
        else:
            return f"rmdir: failed to remove '{path}': {message}"
