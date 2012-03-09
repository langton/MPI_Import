#include <Python.h>
int bar();


static PyObject *f2_bar (PyObject *self, PyObject *args)
{
  int ret;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  ret = bar ();
  return Py_BuildValue ("i", ret);
  
}

static PyMethodDef f2Methods[] =
{
  {"bar", f2_bar, METH_VARARGS,
   "Execute bar()"},
  {NULL, NULL, 0 , NULL}
};

PyMODINIT_FUNC initf2(void)
{
  (void) Py_InitModule("f2", f2Methods);
}

