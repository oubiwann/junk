project(mything)

set(mything_SRC
    ${CMAKE_CURRENT_BINARY_DIR}/mything/mything_module_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/mything/mything_wrapper.cpp
)

set(mything_INCLUDE_DIRECTORIES
    ${SHIBOKEN_INCLUDE_DIR}
    ${PYTHON_INCLUDE_PATH}
    ${PYSIDE_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}/QtCore
    ${QT_INCLUDE_DIR}
    ${QT_QTCORE_INCLUDE_DIR}
    ${LIBFOO_DIR}
)

set(mything_LINK_LIBRARIES
    ${QT_QTCORE_LIBRARY}
    ${SHIBOKEN_PYTHON_LIBRARIES}
    ${SHIBOKEN_LIBRARY}
    ${PYSIDE_LIBRARY}
    ${LIBFOO_DIR}/libfoo.so
)

include_directories(mything ${mything_INCLUDE_DIRECTORIES})
add_library(mything MODULE ${mything_SRC})
set_property(TARGET mything PROPERTY PREFIX "")
target_link_libraries(mything ${mything_LINK_LIBRARIES})

add_custom_command(OUTPUT ${mything_SRC}
                    COMMAND ${GENERATOR}
                    --generatorSet=shiboken --enable-parent-ctor-heuristic --enable-pyside-extensions --enable-return-value-heuristic
                    ${CMAKE_SOURCE_DIR}/mything/global.h
                    --include-paths=${QT_INCLUDE_DIR}:${LIBFOO_DIR}
                    --typesystem-paths=${typesystem_path}:${PYSIDE_TYPESYSTEMS}
                    --output-directory=${CMAKE_CURRENT_BINARY_DIR}
                    ${CMAKE_CURRENT_SOURCE_DIR}/typesystem_mything.xml
                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                    COMMENT "Running generator for libmything..."
                   )
