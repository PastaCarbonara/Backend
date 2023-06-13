# pylint: skip-file

def func(**kwargs):
    print(kwargs)
    x = {kwargs}
    print(x)

func(x="lol", y="chicken ")