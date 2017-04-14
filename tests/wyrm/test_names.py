import unittest
import os, sys, shutil
sys.path.append( os.path.abspath(os.path.join(os.path.dirname(__file__), '../../wyrm' ) ) )
import lib


class names(unittest.TestCase):
    def test_without_format(s):
        word = "super_users"
        ok = {"model": "super_user", "table": "super_users", "class": "SuperUser"}
        for word in ["super_users", "super_user", "SuperUsers", "SuperUser", "Super_Users"]:
            s.assertTrue(lib.names(word) == ok)
    def test_with_format(s):
        word = "super_users"
        s.assertTrue(lib.names(word, ["class", "model"]) == ["SuperUser", "super_user"])
    def test_with_one_format(s):
        word = "super_users"
        s.assertTrue(lib.names(word, ["model"]) == "super_user")

if __name__ == '__main__':
    unittest.main()


