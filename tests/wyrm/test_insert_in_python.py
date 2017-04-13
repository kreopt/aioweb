import unittest
import os, sys, shutil
sys.path.append( os.path.abspath(os.path.join(os.path.dirname(__file__), '../../wyrm' ) ) )
import lib


class insert_in_python(unittest.TestCase):

    def setUp(s):
        s.files_dir = os.path.abspath( os.path.join(os.path.dirname(__file__), 'files' ) )
        s.file_path = os.path.join( s.files_dir, "test.py")
        if os.path.exists(s.file_path): os.unlink( s.file_path )
        shutil.copy2( os.path.join( s.files_dir, "insert_in_python.py"), s.file_path )

    def test_insert_code_after_brief(s):
        lib.insert_in_python(s.file_path, ["AcidTest", "def up"], ["for i in [1,1,2,3]:", "  print(i)" ])
        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r1.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )

    def test_insert_code_in_beginning_of_block(s):
        lib.insert_in_python(s.file_path, ["AcidTest", "def up", "with"], ["for i in [1,1,2,3]:", "  print(i)" ])

        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r2.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )

    def test_empty_line(s):
        lib.insert_in_python(s.file_path, ["AcidTest"], ["def drop(self):", "    for i in [1,1,2,3]:", "        print(i)", "" ])

        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r3.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )

    def test_remove_pass_word(s):
        lib.insert_in_python(s.file_path, ["AcidTest", "def down", "with"], ["for i in [1,1,2,3]:", "  print(i)" ])

        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r4.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )

    def test_insert_import_after_import(s):
        lib.insert_in_python(s.file_path, ["import"], ["from auzli import lsd" ])
        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r5.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )
    def test_end_of_block_insertion(s):
        lib.insert_in_python(s.file_path, ["AcidTest", "def up", "with"], ["for i in [1,1,2,3]:", "  print(i)" ], True)

        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r6.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )

    def test_end_of_block_insertion_and_pass_word(s):
        lib.insert_in_python(s.file_path, ["AcidTest", "def down", "with"], ["for i in [1,1,2,3]:", "  print(i)" ], True)

        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r7.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )

    def test_zend_of_block_insertion2(s):
        lib.insert_in_python(s.file_path, ["AcidTest", "def up", "with"], ["for i in [1,1,2,3]:", "  print(i)" ], True)
        lib.insert_in_python(s.file_path, ["AcidTest", "def up", "with"], ["self.string('weight')" ], True)

        f=open(s.file_path)
        res= f.read()
        f.close()
        f=open( os.path.join( s.files_dir, "insert_in_python_r8.py") )
        ok=f.read()
        f.close()
        s.assertTrue( res == ok )




if __name__ == '__main__':
    unittest.main()
    
