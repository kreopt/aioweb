import sys
import os

brief="test a model"
aliases=['m']
def usage(argv0):
    print("Usage: {} test model MODEL_NAME|--list|--help".format(argv0))
    sys.exit(1)

alias=['m']
def execute(argv, argv0, engine):
    if not argv or '--help' in argv:
        usage(argv0)

    os.environ["AIOWEB_ENV"] = "test"
    environment = os.getenv("AIOWEB_ENV", "development")
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    import lib
    from aioweb import settings
    
    tests_dir = lib.dirs(settings, format=["tests_models"], check=True)
    if not tests_dir:
      print("No model found!")
      sys.exit(0)

    if '--list' in argv:
      [print(m[:-3]) for m in os.listdir(tests_dir) if m.endswith(".py") and not m.startswith("__")]
      
      sys.exit(0)
    test_file = os.path.join(tests_dir, lib.names(argv[0]+".py", format=["model"]) )
    if not os.path.exists(test_file):
      print("No such file: " + test_file)
      sys.exit(1)
      
    os.system("python3 " + test_file)
