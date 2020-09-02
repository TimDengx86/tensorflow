# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""# tf.experimental.numpy: NumPy API on TensorFlow.

This module provides a subset of NumPy API, built on top of TensorFlow
operations. APIs are based on and have been tested with NumPy 1.16 version.

The set of supported APIs may be expanded over time. Also future releases may
change the baseline version of NumPy API being supported. A list of some
systematic differences with NumPy are listed later in the "Differences with
NumPy" section.

## Getting Started

Please also see [TensorFlow NumPy Guide](
https://www.tensorflow.org/guide/tf_numpy).

In the code snippets below, we will assume that `tf.experimental.numpy` is
imported as `tnp` and NumPy is imported as `np`

```python
print(tnp.ones([2,1]) + tnp.ones([1, 2]))
```

## Types

The module provides an `ndarray` class which wraps an immutable `tf.Tensor`.
Additional functions are provided which accept array-like objects. Here
array-like objects includes `ndarrays` as defined by this module, as well as
`tf.Tensor`, in addition to types accepted by NumPy.

A subset of NumPy dtypes are supported. Type promotion follows NumPy
semantics.

```python
print(tnp.ones([1, 2], dtype=tnp.int16) + tnp.ones([2, 1], dtype=tnp.uint8))
```

## Array Interface

The `ndarray` class implements the `__array__` interface. This should allow
these objects to be passed into contexts that expect a NumPy or array-like
object (e.g. matplotlib).

```python
np.sum(tnp.ones([1, 2]) + np.ones([2, 1]))
```


## TF Interoperability

The TF-NumPy API calls can be interleaved with TensorFlow calls
without incurring Tensor data copies. This is true even if the `ndarray` or
`tf.Tensor` is placed on a non-CPU device.

In general, the expected behavior should be on par with that of code involving
`tf.Tensor` and running stateless TensorFlow functions on them.

```python
tnp.sum(tnp.ones([1, 2]) + tf.ones([2, 1]))
```

Note that the `__array_priority__` is currently chosen to be lower than
`tf.Tensor`. Hence the `+` operator above returns a `tf.Tensor`.

Additional examples of interopability include:

*  using `with tf.GradientTape()` scope to compute gradients through the
  TF-NumPy API calls.
*  using `tf.distribution.Strategy` scope for distributed execution
*  using `tf.vectorized_map()` for speeding up code using auto-vectorization



## Device Support

Given that `ndarray` and functions wrap TensorFlow constructs, the code will
have GPU and TPU support on par with TensorFlow. Device placement can be
controlled by using `with tf.device` scopes. Note that these devices could
be local or remote.

```python
with tf.device("GPU:0"):
  x = tnp.ones([1, 2])
print(tf.convert_to_tensor(x).device)
```

## Graph and Eager Modes

Eager mode execution should typically match NumPy semantics of executing
op-by-op. However the same code can be executed in graph mode, by putting it
inside a `tf.function`. The function body can contain NumPy code, and the inputs
can be `ndarray` as well.

```python
@tf.function
def f(x, y):
  return tnp.sum(x + y)

f(tnp.ones([1, 2]), tf.ones([2, 1]))
```
Python control flow based on `ndarray` values will be translated by
[autograph](https://www.tensorflow.org/code/tensorflow/python/autograph/g3doc/reference/index.md)
into `tf.cond` and `tf.while_loop` constructs. The code can be XLA compiled
for further optimizations.

However, note that graph mode execution can change behavior of certain
operations since symbolic execution may not have information that is computed
during runtime. Some differences are:

*   Shapes can be incomplete or unknown in graph mode. This means that
    `ndarray.shape`, `ndarray.size` and `ndarray.ndim` can return `ndarray`
    objects instead of returning integer (or tuple of integer) values.
*   `__len__`, `__iter__` and `__index__` properties of `ndarray`
    may similarly not be supported in graph mode. Code using these
    may need to change to explicit shape operations or control flow
    constructs.
*   Also note the [autograph limitations](
https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/autograph/g3doc/reference/limitations.md).


## Mutation and Variables

`ndarrays` currently wrap immutable `tf.Tensor`. Hence mutation
operations like slice assigns are not supported. This may change in the future.
Note however that one can directly construct a `tf.Variable` and use that with
the TF-NumPy APIs.

```python
tf_var = tf.Variable(2.0)
tf_var.assign_add(tnp.square(tf_var))
```

## Differences with NumPy

Here is a non-exhaustive list of differences:

*   Not all dtypes are currently supported. e.g. `np.float96`, `np.float128`.
    `np.object`, `np.str`, `np.recarray` types are not supported.
*   `ndarray` storage is in C order only. Fortran order, views, `stride_tricks`
    are not supported.
*   Only a subset of functions and modules are supported. This set will be
    expanded over time. For supported functions, some arguments or argument
    values may not be supported. This differences are generally provide in the
    function comments. Full `ufunc` support is also not provided.
*   Buffer mutation is currently not supported. `ndarrays` wrap immutable
    tensors. This means that output buffer arguments (e..g `out` in ufuncs) are
    not supported
*   NumPy C API is not supported. NumPy's Cython and Swig integration are not
    supported.
"""
# TODO(wangpeng): Append `np_export`ed symbols to the comments above.

# pylint: disable=g-direct-tensorflow-import

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.ops.array_ops import newaxis
from tensorflow.python.ops.numpy_ops import np_random as random
from tensorflow.python.ops.numpy_ops import np_utils
# pylint: disable=wildcard-import
from tensorflow.python.ops.numpy_ops.np_array_ops import *
from tensorflow.python.ops.numpy_ops.np_arrays import ndarray
from tensorflow.python.ops.numpy_ops.np_dtypes import *
from tensorflow.python.ops.numpy_ops.np_math_ops import *
# pylint: enable=wildcard-import
from tensorflow.python.ops.numpy_ops.np_utils import finfo
from tensorflow.python.ops.numpy_ops.np_utils import promote_types
from tensorflow.python.ops.numpy_ops.np_utils import result_type


# pylint: disable=redefined-builtin,undefined-variable
@np_utils.np_doc("max", link=np_utils.AliasOf("maximum"))
def max(a, axis=None, keepdims=None):
  return amax(a, axis=axis, keepdims=keepdims)


@np_utils.np_doc("min", link=np_utils.AliasOf("minimum"))
def min(a, axis=None, keepdims=None):
  return amin(a, axis=axis, keepdims=keepdims)


@np_utils.np_doc("round", link=np_utils.AliasOf("around"))
def round(a, decimals=0):
  return around(a, decimals=decimals)
# pylint: enable=redefined-builtin,undefined-variable
