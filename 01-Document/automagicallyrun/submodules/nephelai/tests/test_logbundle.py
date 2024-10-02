import unittest
import sys
import os
import io
import _io
sys.path.insert(0,os.path.abspath('../'))

from nephelai.bundle import Logbundle
from nephelai.exceptions import NephelaiBaseException, NephelaiValidateException, NephelaiParseException
from nephelai.exceptions import NephelaiUnavailException, NephelaiVersionException, NephelaiDisabledException


class TestLogBundleInit(unittest.TestCase):

    def test_validate_failure(self):
        not_a_bundle = './asfasdfasdfasdfasda.py'  # This is a non-existant file
        with self.assertRaises(NephelaiValidateException):
            x = Logbundle(path=not_a_bundle)


    def test_validate_success(self):
        valid_bundle = './'  # This is a directory - i hope?
        self.assertIsInstance(Logbundle(path=valid_bundle),Logbundle)


class TestLogBundleMethods(unittest.TestCase):
    """
    I would like to cover:
    __str__
    get_file_content
    get_file
    _open_file
    get_file_lines_iter
    _mask_compressed_filename
    get_rel_dir_content

    """

    def setUp(self):
        self.test_instance = Logbundle(os.path.abspath('./'))  # Lets use the test directory as our log bundle.

    def test_str(self):
        self.assertTrue(str(self.test_instance).startswith('Unknown bundle at '))

    def test_get_file_content(self):
        self.assertTrue(self.test_instance.EXPANDFILENAMES)
        self.assertEqual('abcdefgh\n',
                         self.test_instance.get_file_content('target_file.txt'))  # This should get expanded to target_file.txt.gz

    def test_get_file(self):
        with self.test_instance.get_file('target_file.txt') as f:
            self.assertIsInstance(f, _io.TextIOWrapper)

    def test__open_file(self):
        with self.test_instance._open_file('target_file.txt') as f:
            self.assertIsInstance(f, _io.TextIOWrapper)
        with self.assertRaises(IOError):
            self.test_instance._open_file('non-existant')

    def test_get_file_lines_iter(self):
        self.assertEqual('abcdefgh\n', next(self.test_instance.get_file_lines_iter('target_file.txt')))

    def test_mask_compressed_filename(self):
        """
        This should hide filenames in FILEXTNS property
        """
        test_string = "abcdefg"
        for xtn in self.test_instance.FILEXTNS:
            self.assertEqual(test_string, self.test_instance._mask_compressed_filename(test_string + xtn))

        # Need to check it doesn't mess with xtn in the middle
        self.assertNotEqual(test_string, self.test_instance._mask_compressed_filename('abc.gzdefg'))

    def test_get_rel_dir_content(self):
        self.assertTrue('target_file.txt' in self.test_instance.get_rel_dir_content('./'))
        self.assertIsInstance(self.test_instance.get_rel_dir_content('./'),list)
