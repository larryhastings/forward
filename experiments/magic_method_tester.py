class MyPreparedDict(dict):
    def __repr__(self):
        super_repr = dict.__repr__(self)
        return f"<MyPreparedDict {super_repr}>"
    def __del__(self):
        # thank goodness for reference counting, and immediate __del__ calling!
        print("oh woe is me!  MyPreparedDict.__del__ was called here!")

class MetaClass_Base(type):
    def __init_subclass__(cls, **kwargs):
        print(f"step 0: metaclass_base.__init_subclass__\n  {cls=}\n  {kwargs=}\n")
        return None

class MetaClass(MetaClass_Base, pepsi="and milk"):
    def __prepare__(name, bases, **kwargs):
        print(f"step 1: metaclass __prepare__\n  {name=}\n  {bases=}\n  {kwargs=}\n")
        return MyPreparedDict()

    def __new__(mcls, name, bases, namespace, **kwargs):
        print(f"step 2: metaclass __new__\n  {mcls=}\n  {name=}\n  {bases=}\n  {namespace=}\n  {kwargs=}\n")
        return super().__new__(mcls, name, bases, namespace, **kwargs)

    def __init__(mcls, name, bases, namespace, **kwargs):
        print(f"step 5: metaclass __init__\n  {mcls=}\n  {name=}\n  {bases=}\n  {namespace=}\n  {kwargs=}\n")
        return super().__init__(name, bases, namespace, **kwargs)

class BaseClass_A:
    def __init_subclass__(cls, **kwargs):
        print(f"step 3: first baseclass.__init_subclass__\n  {cls=}\n  {kwargs=}\n")
        return super().__init_subclass__(**kwargs)

class BaseClass_B:
    def __init_subclass__(cls, **kwargs):
        print(f"step 4: second baseclass.__init_subclass__\n  {cls=}\n  {kwargs=}\n")
        return None

print("next up: class Foo\n")

class Foo(BaseClass_A, BaseClass_B, metaclass=MetaClass, rocket="booster"):
    print("class Foo class body executed here.\n")
    a = 3

print("we just finished defining class Foo.\n")

print(f"{type(Foo.__dict__)=}")
print(f"{Foo.__dict__=}")
print(f"{Foo.__mro__=}")
