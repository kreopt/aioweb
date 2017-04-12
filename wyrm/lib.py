import os, sys, re
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

def patch(file_name, search, fx):
    f= open(file_name, "r")
    lines=f.readlines() 
    f.close()
    n = 0
    for i,line in enumerate(lines):
        if search[n] in line:
            n+=1
            if len(search) == n:
                lines = fx(lines, i)
                break;
    f=open(file_name, "w")
    f.writelines(lines)
    f.close()

def indent(line):
    s=re.search(r'\S', line)
    if not s: return None
    return line[:s.span()[0]]
