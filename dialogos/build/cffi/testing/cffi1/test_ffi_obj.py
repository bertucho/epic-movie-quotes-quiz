import py, sys
import _cffi_backend as _cffi1_backend


def test_ffi_new():
    ffi = _cffi1_backend.FFI()
    p = ffi.new("int *")
    p[0] = -42
    assert p[0] == -42

def test_ffi_subclass():
    class FOO(_cffi1_backend.FFI):
        def __init__(self, x):
            self.x = x
    foo = FOO(42)
    assert foo.x == 42
    p = foo.new("int *")
    assert p[0] == 0

def test_ffi_no_argument():
    py.test.raises(TypeError, _cffi1_backend.FFI, 42)

def test_ffi_cache_type():
    ffi = _cffi1_backend.FFI()
    t1 = ffi.typeof("int **")
    t2 = ffi.typeof("int *")
    assert t2.item is t1.item.item
    assert t2 is t1.item
    assert ffi.typeof("int[][10]") is ffi.typeof("int[][10]")
    assert ffi.typeof("int(*)()") is ffi.typeof("int(*)()")

def test_ffi_cache_type_globally():
    ffi1 = _cffi1_backend.FFI()
    ffi2 = _cffi1_backend.FFI()
    t1 = ffi1.typeof("int *")
    t2 = ffi2.typeof("int *")
    assert t1 is t2

def test_ffi_invalid():
    ffi = _cffi1_backend.FFI()
    # array of 10 times an "int[]" is invalid
    py.test.raises(ValueError, ffi.typeof, "int[10][]")

def test_ffi_docstrings():
    # check that all methods of the FFI class have a docstring.
    check_type = type(_cffi1_backend.FFI.new)
    for methname in dir(_cffi1_backend.FFI):
        if not methname.startswith('_'):
            method = getattr(_cffi1_backend.FFI, methname)
            if isinstance(method, check_type):
                assert method.__doc__, "method FFI.%s() has no docstring" % (
                    methname,)

def test_ffi_NULL():
    NULL = _cffi1_backend.FFI.NULL
    assert _cffi1_backend.FFI().typeof(NULL).cname == "void *"

def test_ffi_no_attr():
    ffi = _cffi1_backend.FFI()
    py.test.raises(AttributeError, "ffi.no_such_name")
    py.test.raises(AttributeError, "ffi.no_such_name = 42")
    py.test.raises(AttributeError, "del ffi.no_such_name")

def test_ffi_string():
    ffi = _cffi1_backend.FFI()
    p = ffi.new("char[]", init=b"foobar\x00baz")
    assert ffi.string(p) == b"foobar"
    assert ffi.string(cdata=p, maxlen=3) == b"foo"

def test_ffi_errno():
    # xxx not really checking errno, just checking that we can read/write it
    ffi = _cffi1_backend.FFI()
    ffi.errno = 42
    assert ffi.errno == 42

def test_ffi_alignof():
    ffi = _cffi1_backend.FFI()
    assert ffi.alignof("int") == 4
    assert ffi.alignof("int[]") == 4
    assert ffi.alignof("int[41]") == 4
    assert ffi.alignof("short[41]") == 2
    assert ffi.alignof(ffi.new("int[41]")) == 4
    assert ffi.alignof(ffi.new("int[]", 41)) == 4

def test_ffi_sizeof():
    ffi = _cffi1_backend.FFI()
    assert ffi.sizeof("int") == 4
    py.test.raises(ffi.error, ffi.sizeof, "int[]")
    assert ffi.sizeof("int[41]") == 41 * 4
    assert ffi.sizeof(ffi.new("int[41]")) == 41 * 4
    assert ffi.sizeof(ffi.new("int[]", 41)) == 41 * 4

def test_ffi_callback():
    ffi = _cffi1_backend.FFI()
    assert ffi.callback("int(int)", lambda x: x + 42)(10) == 52
    assert ffi.callback("int(*)(int)", lambda x: x + 42)(10) == 52
    assert ffi.callback("int(int)", lambda x: x + "", -66)(10) == -66
    assert ffi.callback("int(int)", lambda x: x + "", error=-66)(10) == -66

def test_ffi_callback_decorator():
    ffi = _cffi1_backend.FFI()
    assert ffi.callback(ffi.typeof("int(*)(int)"))(lambda x: x + 42)(10) == 52
    deco = ffi.callback("int(int)", error=-66)
    assert deco(lambda x: x + "")(10) == -66
    assert deco(lambda x: x + 42)(10) == 52

def test_ffi_getctype():
    ffi = _cffi1_backend.FFI()
    assert ffi.getctype("int") == "int"
    assert ffi.getctype("int", 'x') == "int x"
    assert ffi.getctype("int*") == "int *"
    assert ffi.getctype("int*", '') == "int *"
    assert ffi.getctype("int*", 'x') == "int * x"
    assert ffi.getctype("int", '*') == "int *"
    assert ffi.getctype("int", replace_with=' * x ') == "int * x"
    assert ffi.getctype(ffi.typeof("int*"), '*') == "int * *"
    assert ffi.getctype("int", '[5]') == "int[5]"
    assert ffi.getctype("int[5]", '[6]') == "int[6][5]"
    assert ffi.getctype("int[5]", '(*)') == "int(*)[5]"
    # special-case for convenience: automatically put '()' around '*'
    assert ffi.getctype("int[5]", '*') == "int(*)[5]"
    assert ffi.getctype("int[5]", '*foo') == "int(*foo)[5]"
    assert ffi.getctype("int[5]", ' ** foo ') == "int(** foo)[5]"

def test_addressof():
    ffi = _cffi1_backend.FFI()
    a = ffi.new("int[10]")
    b = ffi.addressof(a, 5)
    b[2] = -123
    assert a[7] == -123

def test_handle():
    ffi = _cffi1_backend.FFI()
    x = [2, 4, 6]
    xp = ffi.new_handle(x)
    assert ffi.typeof(xp) == ffi.typeof("void *")
    assert ffi.from_handle(xp) is x
    yp = ffi.new_handle([6, 4, 2])
    assert ffi.from_handle(yp) == [6, 4, 2]

def test_ffi_cast():
    ffi = _cffi1_backend.FFI()
    assert ffi.cast("int(*)(int)", 0) == ffi.NULL
    ffi.callback("int(int)")      # side-effect of registering this string
    py.test.raises(ffi.error, ffi.cast, "int(int)", 0)

def test_ffi_invalid_type():
    ffi = _cffi1_backend.FFI()
    e = py.test.raises(ffi.error, ffi.cast, "", 0)
    assert str(e.value) == ("identifier expected\n"
                            "\n"
                            "^")
    e = py.test.raises(ffi.error, ffi.cast, "struct struct", 0)
    assert str(e.value) == ("struct or union name expected\n"
                            "struct struct\n"
                            "       ^")
    e = py.test.raises(ffi.error, ffi.cast, "struct never_heard_of_s", 0)
    assert str(e.value) == ("undefined struct/union name\n"
                            "struct never_heard_of_s\n"
                            "       ^")
    e = py.test.raises(ffi.error, ffi.cast, "\t\n\x01\x1f~\x7f\x80\xff", 0)
    marks = "?" if sys.version_info < (3,) else "??"
    assert str(e.value) == ("identifier expected\n"
                            "  ??~?%s%s\n"
                            "  ^" % (marks, marks))
    e = py.test.raises(ffi.error, ffi.cast, "X" * 600, 0)
    assert str(e.value) == ("undefined type name")

def test_ffi_buffer():
    ffi = _cffi1_backend.FFI()
    a = ffi.new("signed char[]", [5, 6, 7])
    assert ffi.buffer(a)[:] == b'\x05\x06\x07'
    assert ffi.buffer(cdata=a, size=2)[:] == b'\x05\x06'

def test_ffi_from_buffer():
    import array
    ffi = _cffi1_backend.FFI()
    a = array.array('H', [10000, 20000, 30000])
    c = ffi.from_buffer(a)
    assert ffi.typeof(c) is ffi.typeof("char[]")
    ffi.cast("unsigned short *", c)[1] += 500
    assert list(a) == [10000, 20500, 30000]

def test_ffi_types():
    CData = _cffi1_backend.FFI.CData
    CType = _cffi1_backend.FFI.CType
    ffi = _cffi1_backend.FFI()
    assert isinstance(ffi.cast("int", 42), CData)
    assert isinstance(ffi.typeof("int"), CType)

def test_ffi_getwinerror():
    if sys.platform != "win32":
        py.test.skip("for windows")
    ffi = _cffi1_backend.FFI()
    n = (1 << 29) + 42
    code, message = ffi.getwinerror(code=n)
    assert code == n
