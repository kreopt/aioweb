import os,sys
vanila_dir="/usr/share/aioweb/generators"
def ask(question, answers=["y", "n"]):
    while True:
        print(question + " [" + ",".join(answers) + "]" )
        rc = sys.stdin.readline().strip().lower()
        if rc in answers: return rc
        else:
            print("You bastard gimme a correct answer")

    pass
def get_template(subpath):
    path=os.path.abspath(subpath)
    if os.path.exists( path ): return path 
    path=os.path.join(vanila_dir, subpath)
    if os.path.exists( path ): return path 
    return None
