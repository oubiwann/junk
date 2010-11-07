#include<Python.h>
#include "mything.h"


PyMethodDef methods[] = {
    {NULL, NULL},
};

struct _IntConstantPair {
    char *constant_name;
    int constant_value;
};

typedef struct _IntConstantPair IntConstantPair;

static IntConstantPair _constants[] = {
    {"THING_ONE", THING_ONE},
    {"THING_TWO", THING_TWO},
    {(char*)NULL, 0}
};

PyMODINIT_FUNC
initmything(void)
{
    PyObject *module, *dict, *tmp_obj;
    module = Py_InitModule("mything", methods);
    dict = PyModule_GetDict(module);

    /* Set integer constants */
    int i;
    for (i = 0; _constants[i].constant_name != 0; i++) {
        tmp_obj = Py_BuildValue("i", _constants[i].constant_value);
        PyDict_SetItemString(dict, _constants[i].constant_name, tmp_obj);
        Py_DECREF(tmp_obj);
    }
}
