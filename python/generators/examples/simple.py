def simple_gen():
    yield "apple"
    yield "banana"
    yield "cranberry"

if __name__ == "__main__":
    for result in simple_gen():
        print result
