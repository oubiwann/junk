#include<Python.h>
#include "mything.h"


typedef struct {
    PyObject_HEAD
    PyObject            *x_attr;        /* Attributes dictionary */
} MyThingObject;

static PyTypeObject MyThing_type;

#define MyThingObject_Check(v)      (Py_TYPE(v) == &MyThing_type)

static MyThingObject * newMyThingObject(PyObject *arg) {
    MyThingObject *self;
    self = PyObject_New(MyThingObject, &MyThing_type);
    if (self == NULL)
        return NULL;
    self->x_attr = NULL;
    return self;
}

/* MyThing methods */
static void MyThing_dealloc(MyThingObject *self) {
    Py_XDECREF(self->x_attr);
    PyObject_Del(self);
}

static PyObject * MyThing_get_thing_one(MyThingObject *self, PyObject *args) {
    int result = get_thing_one();
    return Py_BuildValue("i", result);
}

PyObject * MyThing_get_thing_two(PyObject *self) {
    int result = get_thing_two();
    return Py_BuildValue("i", result);
}

static PyMethodDef MyThing_methods[] = {
    {"get_thing_one", (PyCFunction)MyThing_get_thing_one, METH_VARARGS,
     PyDoc_STR("get_thing_one() -> 1")},
    {"get_thing_two", (PyCFunction)MyThing_get_thing_two, METH_VARARGS},
    {NULL, NULL},
};

static PyObject * MyThing_getattr(MyThingObject *self, char *name) {
    if (self->x_attr != NULL) {
        PyObject *v = PyDict_GetItemString(self->x_attr, name);
        if (v != NULL) {
            Py_INCREF(v);
            return v;
        }
    }
    return Py_FindMethod(MyThing_methods, (PyObject *)self, name);
}

static int MyThing_setattr(MyThingObject *self, char *name, PyObject *v) {
    if (self->x_attr == NULL) {
        self->x_attr = PyDict_New();
        if (self->x_attr == NULL)
            return -1;
    }
    if (v == NULL) {
        int rv = PyDict_DelItemString(self->x_attr, name);
        if (rv < 0)
            PyErr_SetString(PyExc_AttributeError,
                "delete non-existing MyThing attribute");
        return rv;
    }
    else
        return PyDict_SetItemString(self->x_attr, name, v);
}

static PyTypeObject MyThing_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "mything.MyThing",              /*tp_name*/
    sizeof(MyThingObject),          /*tp_basicsize*/
    0,                              /*tp_itemsize*/
    /* methods */
    (destructor)MyThing_dealloc,    /*tp_dealloc*/
    0,                              /*tp_print*/
    (getattrfunc)MyThing_getattr,   /*tp_getattr*/
    (setattrfunc)MyThing_setattr,   /*tp_setattr*/
    0,                              /*tp_compare*/
    0,                              /*tp_repr*/
    0,                              /*tp_as_number*/
    0,                              /*tp_as_sequence*/
    0,                              /*tp_as_mapping*/
    0,                              /*tp_hash*/
    0,                              /*tp_call*/
    0,                              /*tp_str*/
    0,                              /*tp_getattro*/
    0,                              /*tp_setattro*/
    0,                              /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,             /*tp_flags*/
    0,                              /*tp_doc*/
    0,                              /*tp_traverse*/
    0,                              /*tp_clear*/
    0,                              /*tp_richcompare*/
    0,                              /*tp_weaklistoffset*/
    0,                              /*tp_iter*/
    0,                              /*tp_iternext*/
    0,                              /*tp_methods*/
    0,                              /*tp_members*/
    0,                              /*tp_getset*/
    0,                              /*tp_base*/
    0,                              /*tp_dict*/
    0,                              /*tp_descr_get*/
    0,                              /*tp_descr_set*/
    0,                              /*tp_dictoffset*/
    0,                              /*tp_init*/
    0,                              /*tp_alloc*/
    0,                              /*tp_new*/
    0,                              /*tp_free*/
    0,                              /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

static PyTypeObject Str_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "xxmodule.Str",             /*tp_name*/
    0,                          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    /* methods */
    0,                          /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    0,                          /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0, /* see initxx */         /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};

/* ---------- */

static PyObject * null_richcompare(PyObject *self, PyObject *other, int op) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
}

static PyTypeObject Null_type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "xxmodule.Null",            /*tp_name*/
    0,                          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    /* methods */
    0,                          /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    null_richcompare,           /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    0,                          /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0, /* see initxx */         /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0, /* see initxx */         /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};


/* ---------- */

static PyObject * mything_MyThing(PyObject *self, PyObject *args) {
    MyThingObject *rv;

    if (!PyArg_ParseTuple(args, ":new"))
        return NULL;
    rv = newMyThingObject(args);
    if (rv == NULL)
        return NULL;
    return (PyObject *)rv;
}

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

static PyMethodDef mything_functions[] = {
    {"MyThing", mything_MyThing, METH_VARARGS,
        PyDoc_STR("MyThing() -> new Xx object")},
    {NULL, NULL}
};

PyMODINIT_FUNC
initmything(void) {
    PyObject *module, *dict;
    module = Py_InitModule("mything", mything_functions);
    dict = PyModule_GetDict(module);

    /* Due to cross platform compiler issues the slots must be filled
     * here. It's required for portability to Windows without requiring
     * C++. */
    Null_type.tp_base = &PyBaseObject_Type;
    Null_type.tp_new = PyType_GenericNew;
    Str_type.tp_base = &PyUnicode_Type;

    /* Finalize the type object including setting type of the new type
     * object; doing it here is required for portability, too. */
    if (PyType_Ready(&MyThing_type) < 0)
        return;

    /* Set integer constants */
    int i;
    for (i = 0; _constants[i].constant_name != 0; i++) {
        PyModule_AddIntConstant(module,
                                _constants[i].constant_name,
                                _constants[i].constant_value);
    }
}
