import unittest
from virtual_fs import VirtualFileSystem
from unittest.mock import patch, MagicMock


class VirtualFileSystemTest(unittest.TestCase):

    def setUp(self):
        # Создаем мок для zipfile
        self.zipfile_mock = MagicMock()
        self.zipfile_mock.namelist.return_value = [
            'file1.txt', 'file2.txt', 'dir1/', 'dir1/file3.txt', 'dir2/', 'dir2/file4.txt'
        ]
        patcher = patch('zipfile.ZipFile', return_value=self.zipfile_mock)
        self.addCleanup(patcher.stop)
        patcher.start()

        # Создаем виртуальную файловую систему
        self.vfs = VirtualFileSystem('mock_archive.zip')

    # Тесты для команды ls
    def test_ls_with_files(self):
        output = self.vfs.list_directory()
        self.assertEqual(output, ['dir1', 'dir2', 'file1.txt', 'file2.txt'])

    def test_ls_empty_directory(self):
        # Тестируем пустую директорию (если удалить все файлы)
        self.vfs.deleted_items.update(['file1.txt', 'file2.txt', 'dir1', 'dir2'])
        output = self.vfs.list_directory()
        self.assertEqual(output, [])

    def test_ls_with_deleted_items(self):
        # Тестируем ls, когда некоторые файлы были удалены
        self.vfs.deleted_items.add('file1.txt')
        output = self.vfs.list_directory()
        self.assertEqual(output, ['dir1', 'dir2', 'file2.txt'])

    # Тесты для команды cd
    def test_cd_valid(self):
        # Успешный переход в существующий каталог
        self.assertTrue(self.vfs.change_directory('dir1'))
        self.assertEqual(self.vfs.get_current_path(), '/dir1')

    def test_cd_invalid(self):
        # Переход в несуществующий каталог
        self.assertFalse(self.vfs.change_directory('invalid_dir'))
        self.assertEqual(self.vfs.get_current_path(), '')

    def test_cd_to_root(self):
        self.vfs.change_directory('dir1')
        self.vfs.change_directory('/')
        self.assertEqual(self.vfs.get_current_path(), '')

    # Тесты для команды pwd
    def test_pwd_root_directory(self):
        self.assertEqual(self.vfs.get_current_path(), '')

    def test_pwd_after_cd(self):
        self.vfs.change_directory('dir1')
        self.assertEqual(self.vfs.get_current_path(), '/dir1')

    def test_pwd_nested_directory(self):
        self.vfs.change_directory('/dir1')
        self.assertEqual(self.vfs.get_current_path(), '/dir1')

    # Тесты для команды tree
    def test_tree_single_level(self):
        self.vfs.change_directory('dir1')
        tree_output = self.vfs.get_tree()
        expected_output = '└── file3.txt\n'
        self.assertEqual(tree_output, expected_output)


    # Тесты для команды rmdir
    def test_rmdir_valid(self):
        # Успешное удаление пустой директории
        self.vfs.deleted_items.add('dir1/file3.txt')  # Чтобы удалить каталог, он должен быть пуст
        success, message = self.vfs.remove_directory('dir1')
        self.assertTrue(success)
        self.assertEqual(message, '')

    def test_rmdir_directory_not_empty(self):
        # Неуспешное удаление непустой директории
        success, message = self.vfs.remove_directory('dir1')
        self.assertFalse(success)
        self.assertEqual(message, 'Directory not empty')

    def test_rmdir_directory_does_not_exist(self):
        # Попытка удаления несуществующей директории
        success, message = self.vfs.remove_directory('invalid_dir')
        self.assertFalse(success)
        self.assertEqual(message, 'No such directory')

    # Дополнительные тесты для работы с файлами
    def test_file_exists(self):
        # Проверка, что файл существует
        self.assertTrue(self.vfs.file_exists('file1.txt'))

    def test_file_does_not_exist(self):
        # Проверка, что файл не существует (или был удален)
        self.vfs.deleted_items.add('file1.txt')
        self.assertFalse(self.vfs.file_exists('file1.txt'))

    def test_read_file(self):
        # Чтение содержимого файла
        self.zipfile_mock.open.return_value.read.return_value = "1231231312"
        content = self.vfs.read_file('file1.txt')

    def test_read_deleted_file(self):
        # Попытка чтения удаленного файла
        self.vfs.deleted_items.add('file1.txt')
        content = self.vfs.read_file('file1.txt')
        self.assertEqual(content, 'cat: file1.txt: No such file')


if __name__ == '__main__':
    unittest.main()
