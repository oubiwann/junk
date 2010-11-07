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

void initmything()
{
    PyObject *module, *dict;
    module = Py_InitModule("mything", methods);
    dict = PyModule_GetDict(module);

    /* Set integer constants */
    int i;
    int tmp_obj;
    for (i = 0; _constants[i].constant_name != 0; i++) {
        tmp_obj = PyInt_FromLong(_constants[i].constant_value);
        PyDict_SetItemString(dict, _constants[i].constant_name, tmp_obj);
        Py_DECREF(tmp_obj);
    }
}
