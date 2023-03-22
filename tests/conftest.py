import os


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    print("pytest_configure")

    if os.path.isfile("test.db"):
        print("AAA")

        raise Exception("test.db already exists.")

    os.environ["env"] = "test"
    os.system('alembic upgrade head')
    


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    print("B")
    

def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    print("C")
    

def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
    print("pytest_unconfigure")
    os.remove("test.db") 
