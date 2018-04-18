"""
Simple annotation that mimics java's @override annotation. Used both for documentation and
checking purposes. Will throw an AssertionError when the method marked with the annotation does not
override correctly its corresponding superclass method.
"""

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
