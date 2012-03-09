#include <Python.h>
int bar();


static PyObject *f1_bar (PyObject *self, PyObject *args)
{
  int ret;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  ret = bar ();
  return Py_BuildValue ("i", ret);
  
}

static PyMethodDef f1Methods[] =
{
  {"bar", f1_bar, METH_VARARGS,
   "Execute bar()"},
  {NULL, NULL, 0 , NULL}
};

PyMODINIT_FUNC initf1(void)
{
  (void) Py_InitModule("f1", f1Methods);
}

