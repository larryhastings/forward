
print("Defining metaclasses, base classes, and base metaclasses.\n")

_step_no = 0

def step_no():
    global _step_no
    _step_no += 1
    return _step_no

class MyPreparedDict(dict):
    def __repr__(self):
        super_repr = dict.__repr__(self)
        return f"<MyPreparedDict {super_repr}>"
    def __del__(self):
        # thank goodness for reference counting, and immediate __del__ calling!
        print("oh woe is me!  MyPreparedDict.__del__ was called here!")

class MetaClass_Base(type):
    def __init_subclass__(cls, **kwargs):
        # We aren't actually interested in when this is run.
        # We're only printing the dunder methods called when defining class foo.
        # print(f"step {step_no()}: metaclass_base.__init_subclass__\n  {cls=}\n  {kwargs=}\n")
        return None

class MetaClass(MetaClass_Base, pepsi="and milk"):
    def __prepare__(name, bases, **kwargs):
        print(f"step {step_no()}: metaclass __prepare__\n  {name=}\n  {bases=}\n  {kwargs=}\n")
        return MyPreparedDict()

    def __new__(metaclass, name, bases, namespace, **kwargs):
        print(f"step {step_no()}: metaclass __new__\n  {metaclass=}\n  {name=}\n  {bases=}\n  {namespace=}\n  {kwargs=}\n")
        return super().__new__(metaclass, name, bases, namespace, **kwargs)

    def __init__(metaclass, name, bases, namespace, **kwargs):
        print(f"step {step_no()}: metaclass __init__\n  {metaclass=}\n  {name=}\n  {bases=}\n  {namespace=}\n  {kwargs=}\n")
        return super().__init__(name, bases, namespace, **kwargs)

class BaseClass_A:
    def __init_subclass__(cls, **kwargs):
        print(f"step {step_no()}: BaseClass_A.__init_subclass__ (first defined base class)\n  {cls=}\n  {kwargs=}\n")
        return super().__init_subclass__(**kwargs)

class BaseClass_B:
    def __init_subclass__(cls, **kwargs):
        print(f"step {step_no()}: BaseClass_B.__init_subclass__ (second defined base class)\n  {cls=}\n  {kwargs=}\n")
        return None


print("The next line is the declaration of class Foo.\n")

class Foo(BaseClass_A, BaseClass_B, metaclass=MetaClass, rocket="booster"):
    print("Now executing the class body for class Foo.\n")
    a = 3

print("Just finished class Foo.\n")

print(f"{type(Foo.__dict__)=}")
print(f"{Foo.__dict__=}")
print(f"{Foo.__mro__=}")
