def simple_nested_gen():
    yield "apple"
    for i in xrange(1,10):
        yield i
    yield "banana"
    yield "cranberry"

if __name__ == "__main__":
    for result in simple_nested_gen():
        print result
