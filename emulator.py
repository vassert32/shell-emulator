import argparse
import tkinter as tk
from virtual_fs import VirtualFileSystem
from command_processor import CommandProcessor
from action_logger import ActionLogger


class ShellEmulator(tk.Tk):
    def __init__(self, user, host, fs_archive, log_path, script_path=None):
        super().__init__()
        self.title("Shell Emulator")
        self.geometry("512x512")

        self.user = user
        self.host = host
        self.fs_archive = fs_archive
        self.log_path = log_path
        self.script_path = script_path

        self.vfs = VirtualFileSystem(fs_archive)
        self.logger = ActionLogger(log_path, user)
        self.command_processor = CommandProcessor(self.vfs, self.logger)

        self.create_widgets()
        self.run_startup_script()

        # Bind the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.logger.close()
        self.destroy()

    def create_widgets(self):
        self.text_area = tk.Text(self, wrap='word', undo=True)
        self.text_area.pack(fill='both', expand=True)

        # Инициализируем позицию ввода
        self.display_prompt()

        # Привязываем события
        self.text_area.bind('<Return>', self.on_enter)
        self.text_area.bind('<Key>', self.on_keypress)
        self.text_area.bind('<BackSpace>', self.on_backspace)

    def display_prompt(self):
        current_dir = self.vfs.get_current_path()
        self.prompt = f"{self.user}@{self.host} {current_dir}$ "
        self.text_area.insert('end', self.prompt)
        self.text_area.mark_set("input_start", "insert")
        self.text_area.mark_gravity("input_start", "left")
        self.text_area.see('end')

    def on_keypress(self, event):
        if self.text_area.compare('insert', '<', "input_start"):
            self.text_area.mark_set("insert", "end")
            return "break"
        else:
            return None

    def on_backspace(self, event):
        if self.text_area.compare('insert', '<=', "input_start"):
            return "break"
        else:
            return None

    def on_enter(self, event):
        command_line = self.get_command()
        self.text_area.insert('end', '\n')  # Перенос на новую строку

        self.count_del = 0
        self.count_inc = 0

        if command_line.strip() != '':
            self.logger.log_action(command_line.strip())
            output = self.command_processor.process_command(command_line.strip())
            if output:
                self.text_area.insert('end', output + '\n')
        else:
            pass

        if command_line.strip() == 'exit':
            self.logger.close()
            self.destroy()
            return 'break'

        # Обновляем приглашение с текущим путем
        self.display_prompt()

        return 'break'

    def get_command(self):
        try:
            input_start_index = self.text_area.index("input_start")
        except tk.TclError:
            print("Mark 'input_start' not found.")
            return ''

        end_index = self.text_area.index('end-1c')
        print(f"input_start_index: {input_start_index}, end_index: {end_index}")

        if self.text_area.compare(input_start_index, '<', end_index):
            command = self.text_area.get(input_start_index, end_index).strip()
            if command:
                print(f"Command entered: {command}")
                return command
            else:
                print("Empty command")
                return ''
        else:
            print("No input after prompt.")
            return ''

    def run_startup_script(self):
        if self.script_path:
            try:
                with open(self.script_path, 'r') as script_file:
                    commands = script_file.readlines()
                    for command in commands:
                        command = command.strip()
                        if command:
                            self.text_area.insert('end', command + '\n')
                            self.logger.log_action(command)
                            output = self.command_processor.process_command(command)
                            if output:
                                self.text_area.insert('end', output + '\n')
                            if command == 'exit':
                                self.logger.close()
                                self.destroy()
                                return
                    self.display_prompt()
            except FileNotFoundError:
                self.text_area.insert('end', f"Startup script not found: {self.script_path}\n")
                self.display_prompt()
        else:
            self.display_prompt()


def main():
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('--user', required=True, help='User name for prompt')
    parser.add_argument('--host', required=True, help='Host name for prompt')
    parser.add_argument('--fs', required=True, help='Path to virtual filesystem zip archive')
    parser.add_argument('--log', required=True, help='Path to log file')
    parser.add_argument('--script', help='Path to startup script')

    args = parser.parse_args()

    app = ShellEmulator(
        user=args.user,
        host=args.host,
        fs_archive=args.fs,
        log_path=args.log,
        script_path=args.script
    )
    app.mainloop()


if __name__ == '__main__':
    main()
