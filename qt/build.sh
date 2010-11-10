cd python
# Generate binding code
generatorrunner \
    --generatorSet=shiboken \
    mything/pyside_global.h \
    --include-paths=../src/ \
    --typesystem-paths=/usr/share/PySide/typesystems/:./mything/ \
    --output-directory=. \
    mything/typesystem_mything.xml
# Build the bindings
mkdir build
cd build
cmake ../
make
# Run the unit tests
ctest
