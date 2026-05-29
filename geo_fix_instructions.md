# إصلاح خطأ `4_Geo_Geophysics.py` — ValueError: The truth value of a DataFrame is ambiguous

## السبب
```python
# ❌ خطأ — عندما _raw.get("res") يُرجع DataFrame، Python يحاول تقييمه كـ bool
RES = _raw.get("res") or _demo_res()
```
Pandas يرفض تقييم DataFrame كـ True/False مباشرة.

---

## الإصلاح — استبدل كل سطر يستخدم `or` مع DataFrames

### الشكل العام للإصلاح:
```python
# ✅ صحيح — دالة مساعدة آمنة
def _or_demo(val, demo_fn):
    """إرجع val إذا كان DataFrame غير فارغ، وإلا إرجع demo_fn()."""
    if isinstance(val, pd.DataFrame):
        return val if not val.empty else demo_fn()
    return demo_fn() if val is None else val
```

### تطبيقه في `4_Geo_Geophysics.py`:

ابحث عن الأسطر التالية (حوالي السطر 162):
```python
# ❌ قبل الإصلاح
RES   = _raw.get("res")   or _demo_res()
WELLS = _raw.get("wells") or _demo_wells()
PROD  = _raw.get("prod")  or _demo_prod()
```

استبدلها بـ:
```python
# ✅ بعد الإصلاح — أضف الدالة المساعدة أولاً في أعلى الملف بعد الـ imports
def _or_demo(val, demo_fn):
    if isinstance(val, pd.DataFrame):
        return val if not val.empty else demo_fn()
    return demo_fn() if val is None else val

# ثم استخدمها:
RES   = _or_demo(_raw.get("res"),   _demo_res)
WELLS = _or_demo(_raw.get("wells"), _demo_wells)
PROD  = _or_demo(_raw.get("prod"),  _demo_prod)
```

> **ملاحظة:** مرر اسم الدالة بدون أقواس `_demo_res` وليس `_demo_res()`
> حتى لا تُستدعى إلا عند الحاجة.

---

## إذا كان النمط مختلفاً قليلاً
أي سطر يشبه:
```python
X = some_dict.get("key") or some_function()
```
حيث النتيجة قد تكون DataFrame، استبدله بـ:
```python
_tmp = some_dict.get("key")
X = _tmp if (isinstance(_tmp, pd.DataFrame) and not _tmp.empty) else some_function()
```
