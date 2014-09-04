# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.2
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_osgFX', [dirname(__file__)])
        except ImportError:
            import _osgFX
            return _osgFX
        if fp is not None:
            try:
                _mod = imp.load_module('_osgFX', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _osgFX = swig_import_helper()
    del swig_import_helper
else:
    import _osgFX
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


try:
    import weakref
    weakref_proxy = weakref.proxy
except:
    weakref_proxy = lambda x: x


class SwigPyIterator(_object):
    """Proxy of C++ swig::SwigPyIterator class"""
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SwigPyIterator, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SwigPyIterator, name)
    def __init__(self, *args, **kwargs): raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _osgFX.delete_SwigPyIterator
    __del__ = lambda self : None;
    def value(self):
        """value(SwigPyIterator self) -> PyObject *"""
        return _osgFX.SwigPyIterator_value(self)

    def incr(self, n=1):
        """
        incr(SwigPyIterator self, size_t n=1) -> SwigPyIterator
        incr(SwigPyIterator self) -> SwigPyIterator
        """
        return _osgFX.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        """
        decr(SwigPyIterator self, size_t n=1) -> SwigPyIterator
        decr(SwigPyIterator self) -> SwigPyIterator
        """
        return _osgFX.SwigPyIterator_decr(self, n)

    def distance(self, *args):
        """distance(SwigPyIterator self, SwigPyIterator x) -> ptrdiff_t"""
        return _osgFX.SwigPyIterator_distance(self, *args)

    def equal(self, *args):
        """equal(SwigPyIterator self, SwigPyIterator x) -> bool"""
        return _osgFX.SwigPyIterator_equal(self, *args)

    def copy(self):
        """copy(SwigPyIterator self) -> SwigPyIterator"""
        return _osgFX.SwigPyIterator_copy(self)

    def next(self):
        """next(SwigPyIterator self) -> PyObject *"""
        return _osgFX.SwigPyIterator_next(self)

    def __next__(self):
        """__next__(SwigPyIterator self) -> PyObject *"""
        return _osgFX.SwigPyIterator___next__(self)

    def previous(self):
        """previous(SwigPyIterator self) -> PyObject *"""
        return _osgFX.SwigPyIterator_previous(self)

    def advance(self, *args):
        """advance(SwigPyIterator self, ptrdiff_t n) -> SwigPyIterator"""
        return _osgFX.SwigPyIterator_advance(self, *args)

    def __eq__(self, *args):
        """__eq__(SwigPyIterator self, SwigPyIterator x) -> bool"""
        return _osgFX.SwigPyIterator___eq__(self, *args)

    def __ne__(self, *args):
        """__ne__(SwigPyIterator self, SwigPyIterator x) -> bool"""
        return _osgFX.SwigPyIterator___ne__(self, *args)

    def __iadd__(self, *args):
        """__iadd__(SwigPyIterator self, ptrdiff_t n) -> SwigPyIterator"""
        return _osgFX.SwigPyIterator___iadd__(self, *args)

    def __isub__(self, *args):
        """__isub__(SwigPyIterator self, ptrdiff_t n) -> SwigPyIterator"""
        return _osgFX.SwigPyIterator___isub__(self, *args)

    def __add__(self, *args):
        """__add__(SwigPyIterator self, ptrdiff_t n) -> SwigPyIterator"""
        return _osgFX.SwigPyIterator___add__(self, *args)

    def __sub__(self, *args):
        """
        __sub__(SwigPyIterator self, ptrdiff_t n) -> SwigPyIterator
        __sub__(SwigPyIterator self, SwigPyIterator x) -> ptrdiff_t
        """
        return _osgFX.SwigPyIterator___sub__(self, *args)

    def __iter__(self): return self
SwigPyIterator_swigregister = _osgFX.SwigPyIterator_swigregister
SwigPyIterator_swigregister(SwigPyIterator)

import osg
class Technique(osg.Referenced):
    """Proxy of C++ osgFX::Technique class"""
    __swig_setmethods__ = {}
    for _s in [osg.Referenced]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Technique, name, value)
    __swig_getmethods__ = {}
    for _s in [osg.Referenced]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, Technique, name)
    def __init__(self, *args, **kwargs): raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    def techniqueName(self):
        """techniqueName(Technique self) -> char const *"""
        return _osgFX.Technique_techniqueName(self)

    def techniqueDescription(self):
        """techniqueDescription(Technique self) -> char const *"""
        return _osgFX.Technique_techniqueDescription(self)

    def getRequiredExtensions(self, *args):
        """getRequiredExtensions(Technique self, std::vector< std::string,std::allocator< std::string > > & arg2)"""
        return _osgFX.Technique_getRequiredExtensions(self, *args)

    def validate(self, *args):
        """validate(Technique self, State arg2) -> bool"""
        return _osgFX.Technique_validate(self, *args)

    def getNumPasses(self):
        """getNumPasses(Technique self) -> int"""
        return _osgFX.Technique_getNumPasses(self)

    def getPassStateSet(self, *args):
        """
        getPassStateSet(Technique self, int i) -> StateSet
        getPassStateSet(Technique self, int i) -> StateSet
        """
        return _osgFX.Technique_getPassStateSet(self, *args)

    def traverse(self, *args):
        """traverse(Technique self, NodeVisitor nv, Effect fx)"""
        return _osgFX.Technique_traverse(self, *args)

Technique_swigregister = _osgFX.Technique_swigregister
Technique_swigregister(Technique)

class Effect(osg.Group):
    """Proxy of C++ osgFX::Effect class"""
    __swig_setmethods__ = {}
    for _s in [osg.Group]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Effect, name, value)
    __swig_getmethods__ = {}
    for _s in [osg.Group]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, Effect, name)
    def __init__(self, *args, **kwargs): raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    def isSameKindAs(self, *args):
        """isSameKindAs(Effect self, Object obj) -> bool"""
        return _osgFX.Effect_isSameKindAs(self, *args)

    def libraryName(self):
        """libraryName(Effect self) -> char const *"""
        return _osgFX.Effect_libraryName(self)

    def className(self):
        """className(Effect self) -> char const *"""
        return _osgFX.Effect_className(self)

    def effectName(self):
        """effectName(Effect self) -> char const *"""
        return _osgFX.Effect_effectName(self)

    def effectDescription(self):
        """effectDescription(Effect self) -> char const *"""
        return _osgFX.Effect_effectDescription(self)

    def effectAuthor(self):
        """effectAuthor(Effect self) -> char const *"""
        return _osgFX.Effect_effectAuthor(self)

    def getEnabled(self):
        """getEnabled(Effect self) -> bool"""
        return _osgFX.Effect_getEnabled(self)

    def setEnabled(self, *args):
        """setEnabled(Effect self, bool v)"""
        return _osgFX.Effect_setEnabled(self, *args)

    def setUpDemo(self):
        """setUpDemo(Effect self)"""
        return _osgFX.Effect_setUpDemo(self)

    def getNumTechniques(self):
        """getNumTechniques(Effect self) -> int"""
        return _osgFX.Effect_getNumTechniques(self)

    def getTechnique(self, *args):
        """
        getTechnique(Effect self, int i) -> Technique
        getTechnique(Effect self, int i) -> Technique
        """
        return _osgFX.Effect_getTechnique(self, *args)

    def getSelectedTechnique(self):
        """getSelectedTechnique(Effect self) -> int"""
        return _osgFX.Effect_getSelectedTechnique(self)

    AUTO_DETECT = _osgFX.Effect_AUTO_DETECT
    def selectTechnique(self, *args):
        """
        selectTechnique(Effect self, int i=AUTO_DETECT)
        selectTechnique(Effect self)
        """
        return _osgFX.Effect_selectTechnique(self, *args)

    def traverse(self, *args):
        """traverse(Effect self, NodeVisitor nv)"""
        return _osgFX.Effect_traverse(self, *args)

    def inherited_traverse(self, *args):
        """inherited_traverse(Effect self, NodeVisitor nv)"""
        return _osgFX.Effect_inherited_traverse(self, *args)

Effect_swigregister = _osgFX.Effect_swigregister
Effect_swigregister(Effect)

class AnisotropicLighting(Effect):
    """Proxy of C++ osgFX::AnisotropicLighting class"""
    __swig_setmethods__ = {}
    for _s in [Effect]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, AnisotropicLighting, name, value)
    __swig_getmethods__ = {}
    for _s in [Effect]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, AnisotropicLighting, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::AnisotropicLighting self) -> AnisotropicLighting
        __init__(osgFX::AnisotropicLighting self, AnisotropicLighting copy, CopyOp copyop=SHALLOW_COPY) -> AnisotropicLighting
        __init__(osgFX::AnisotropicLighting self, AnisotropicLighting copy) -> AnisotropicLighting
        """
        this = _osgFX.new_AnisotropicLighting(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(AnisotropicLighting self) -> Object"""
        return _osgFX.AnisotropicLighting_cloneType(self)

    def clone(self, *args):
        """clone(AnisotropicLighting self, CopyOp copyop) -> Object"""
        return _osgFX.AnisotropicLighting_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(AnisotropicLighting self, Object obj) -> bool"""
        return _osgFX.AnisotropicLighting_isSameKindAs(self, *args)

    def className(self):
        """className(AnisotropicLighting self) -> char const *"""
        return _osgFX.AnisotropicLighting_className(self)

    def libraryName(self):
        """libraryName(AnisotropicLighting self) -> char const *"""
        return _osgFX.AnisotropicLighting_libraryName(self)

    def accept(self, *args):
        """accept(AnisotropicLighting self, NodeVisitor nv)"""
        return _osgFX.AnisotropicLighting_accept(self, *args)

    def effectName(self):
        """effectName(AnisotropicLighting self) -> char const *"""
        return _osgFX.AnisotropicLighting_effectName(self)

    def effectDescription(self):
        """effectDescription(AnisotropicLighting self) -> char const *"""
        return _osgFX.AnisotropicLighting_effectDescription(self)

    def effectAuthor(self):
        """effectAuthor(AnisotropicLighting self) -> char const *"""
        return _osgFX.AnisotropicLighting_effectAuthor(self)

    def getLightingMap(self, *args):
        """
        getLightingMap(AnisotropicLighting self) -> Image
        getLightingMap(AnisotropicLighting self) -> Image
        """
        return _osgFX.AnisotropicLighting_getLightingMap(self, *args)

    def setLightingMap(self, *args):
        """setLightingMap(AnisotropicLighting self, Image image)"""
        return _osgFX.AnisotropicLighting_setLightingMap(self, *args)

    def getLightNumber(self):
        """getLightNumber(AnisotropicLighting self) -> int"""
        return _osgFX.AnisotropicLighting_getLightNumber(self)

    def setLightNumber(self, *args):
        """setLightNumber(AnisotropicLighting self, int n)"""
        return _osgFX.AnisotropicLighting_setLightNumber(self, *args)

AnisotropicLighting_swigregister = _osgFX.AnisotropicLighting_swigregister
AnisotropicLighting_swigregister(AnisotropicLighting)

class BumpMapping(Effect):
    """Proxy of C++ osgFX::BumpMapping class"""
    __swig_setmethods__ = {}
    for _s in [Effect]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, BumpMapping, name, value)
    __swig_getmethods__ = {}
    for _s in [Effect]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, BumpMapping, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::BumpMapping self) -> BumpMapping
        __init__(osgFX::BumpMapping self, BumpMapping copy, CopyOp copyop=SHALLOW_COPY) -> BumpMapping
        __init__(osgFX::BumpMapping self, BumpMapping copy) -> BumpMapping
        """
        this = _osgFX.new_BumpMapping(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(BumpMapping self) -> Object"""
        return _osgFX.BumpMapping_cloneType(self)

    def clone(self, *args):
        """clone(BumpMapping self, CopyOp copyop) -> Object"""
        return _osgFX.BumpMapping_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(BumpMapping self, Object obj) -> bool"""
        return _osgFX.BumpMapping_isSameKindAs(self, *args)

    def className(self):
        """className(BumpMapping self) -> char const *"""
        return _osgFX.BumpMapping_className(self)

    def libraryName(self):
        """libraryName(BumpMapping self) -> char const *"""
        return _osgFX.BumpMapping_libraryName(self)

    def accept(self, *args):
        """accept(BumpMapping self, NodeVisitor nv)"""
        return _osgFX.BumpMapping_accept(self, *args)

    def effectName(self):
        """effectName(BumpMapping self) -> char const *"""
        return _osgFX.BumpMapping_effectName(self)

    def effectDescription(self):
        """effectDescription(BumpMapping self) -> char const *"""
        return _osgFX.BumpMapping_effectDescription(self)

    def effectAuthor(self):
        """effectAuthor(BumpMapping self) -> char const *"""
        return _osgFX.BumpMapping_effectAuthor(self)

    def getLightNumber(self):
        """getLightNumber(BumpMapping self) -> int"""
        return _osgFX.BumpMapping_getLightNumber(self)

    def setLightNumber(self, *args):
        """setLightNumber(BumpMapping self, int n)"""
        return _osgFX.BumpMapping_setLightNumber(self, *args)

    def getDiffuseTextureUnit(self):
        """getDiffuseTextureUnit(BumpMapping self) -> int"""
        return _osgFX.BumpMapping_getDiffuseTextureUnit(self)

    def setDiffuseTextureUnit(self, *args):
        """setDiffuseTextureUnit(BumpMapping self, int n)"""
        return _osgFX.BumpMapping_setDiffuseTextureUnit(self, *args)

    def getNormalMapTextureUnit(self):
        """getNormalMapTextureUnit(BumpMapping self) -> int"""
        return _osgFX.BumpMapping_getNormalMapTextureUnit(self)

    def setNormalMapTextureUnit(self, *args):
        """setNormalMapTextureUnit(BumpMapping self, int n)"""
        return _osgFX.BumpMapping_setNormalMapTextureUnit(self, *args)

    def getOverrideDiffuseTexture(self, *args):
        """
        getOverrideDiffuseTexture(BumpMapping self) -> Texture2D
        getOverrideDiffuseTexture(BumpMapping self) -> Texture2D
        """
        return _osgFX.BumpMapping_getOverrideDiffuseTexture(self, *args)

    def setOverrideDiffuseTexture(self, *args):
        """setOverrideDiffuseTexture(BumpMapping self, Texture2D texture)"""
        return _osgFX.BumpMapping_setOverrideDiffuseTexture(self, *args)

    def getOverrideNormalMapTexture(self, *args):
        """
        getOverrideNormalMapTexture(BumpMapping self) -> Texture2D
        getOverrideNormalMapTexture(BumpMapping self) -> Texture2D
        """
        return _osgFX.BumpMapping_getOverrideNormalMapTexture(self, *args)

    def setOverrideNormalMapTexture(self, *args):
        """setOverrideNormalMapTexture(BumpMapping self, Texture2D texture)"""
        return _osgFX.BumpMapping_setOverrideNormalMapTexture(self, *args)

    def prepareGeometry(self, *args):
        """prepareGeometry(BumpMapping self, Geometry geo)"""
        return _osgFX.BumpMapping_prepareGeometry(self, *args)

    def prepareNode(self, *args):
        """prepareNode(BumpMapping self, Node node)"""
        return _osgFX.BumpMapping_prepareNode(self, *args)

    def prepareChildren(self):
        """prepareChildren(BumpMapping self)"""
        return _osgFX.BumpMapping_prepareChildren(self)

    def setUpDemo(self):
        """setUpDemo(BumpMapping self)"""
        return _osgFX.BumpMapping_setUpDemo(self)

BumpMapping_swigregister = _osgFX.BumpMapping_swigregister
BumpMapping_swigregister(BumpMapping)

class Cartoon(Effect):
    """Proxy of C++ osgFX::Cartoon class"""
    __swig_setmethods__ = {}
    for _s in [Effect]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Cartoon, name, value)
    __swig_getmethods__ = {}
    for _s in [Effect]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, Cartoon, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::Cartoon self) -> Cartoon
        __init__(osgFX::Cartoon self, Cartoon copy, CopyOp copyop=SHALLOW_COPY) -> Cartoon
        __init__(osgFX::Cartoon self, Cartoon copy) -> Cartoon
        """
        this = _osgFX.new_Cartoon(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(Cartoon self) -> Object"""
        return _osgFX.Cartoon_cloneType(self)

    def clone(self, *args):
        """clone(Cartoon self, CopyOp copyop) -> Object"""
        return _osgFX.Cartoon_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(Cartoon self, Object obj) -> bool"""
        return _osgFX.Cartoon_isSameKindAs(self, *args)

    def className(self):
        """className(Cartoon self) -> char const *"""
        return _osgFX.Cartoon_className(self)

    def libraryName(self):
        """libraryName(Cartoon self) -> char const *"""
        return _osgFX.Cartoon_libraryName(self)

    def accept(self, *args):
        """accept(Cartoon self, NodeVisitor nv)"""
        return _osgFX.Cartoon_accept(self, *args)

    def effectName(self):
        """effectName(Cartoon self) -> char const *"""
        return _osgFX.Cartoon_effectName(self)

    def effectDescription(self):
        """effectDescription(Cartoon self) -> char const *"""
        return _osgFX.Cartoon_effectDescription(self)

    def effectAuthor(self):
        """effectAuthor(Cartoon self) -> char const *"""
        return _osgFX.Cartoon_effectAuthor(self)

    def getOutlineColor(self):
        """getOutlineColor(Cartoon self) -> Vec4f"""
        return _osgFX.Cartoon_getOutlineColor(self)

    def setOutlineColor(self, *args):
        """setOutlineColor(Cartoon self, Vec4f color)"""
        return _osgFX.Cartoon_setOutlineColor(self, *args)

    def getOutlineLineWidth(self):
        """getOutlineLineWidth(Cartoon self) -> float"""
        return _osgFX.Cartoon_getOutlineLineWidth(self)

    def setOutlineLineWidth(self, *args):
        """setOutlineLineWidth(Cartoon self, float w)"""
        return _osgFX.Cartoon_setOutlineLineWidth(self, *args)

    def getLightNumber(self):
        """getLightNumber(Cartoon self) -> int"""
        return _osgFX.Cartoon_getLightNumber(self)

    def setLightNumber(self, *args):
        """setLightNumber(Cartoon self, int n)"""
        return _osgFX.Cartoon_setLightNumber(self, *args)

Cartoon_swigregister = _osgFX.Cartoon_swigregister
Cartoon_swigregister(Cartoon)

class MultiTextureControl(osg.Group):
    """Proxy of C++ osgFX::MultiTextureControl class"""
    __swig_setmethods__ = {}
    for _s in [osg.Group]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, MultiTextureControl, name, value)
    __swig_getmethods__ = {}
    for _s in [osg.Group]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, MultiTextureControl, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::MultiTextureControl self) -> MultiTextureControl
        __init__(osgFX::MultiTextureControl self, MultiTextureControl copy, CopyOp copyop=SHALLOW_COPY) -> MultiTextureControl
        __init__(osgFX::MultiTextureControl self, MultiTextureControl copy) -> MultiTextureControl
        """
        this = _osgFX.new_MultiTextureControl(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(MultiTextureControl self) -> Object"""
        return _osgFX.MultiTextureControl_cloneType(self)

    def clone(self, *args):
        """clone(MultiTextureControl self, CopyOp copyop) -> Object"""
        return _osgFX.MultiTextureControl_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(MultiTextureControl self, Object obj) -> bool"""
        return _osgFX.MultiTextureControl_isSameKindAs(self, *args)

    def className(self):
        """className(MultiTextureControl self) -> char const *"""
        return _osgFX.MultiTextureControl_className(self)

    def libraryName(self):
        """libraryName(MultiTextureControl self) -> char const *"""
        return _osgFX.MultiTextureControl_libraryName(self)

    def accept(self, *args):
        """accept(MultiTextureControl self, NodeVisitor nv)"""
        return _osgFX.MultiTextureControl_accept(self, *args)

    def setTextureWeight(self, *args):
        """setTextureWeight(MultiTextureControl self, unsigned int unit, float weight)"""
        return _osgFX.MultiTextureControl_setTextureWeight(self, *args)

    def getTextureWeight(self, *args):
        """getTextureWeight(MultiTextureControl self, unsigned int unit) -> float"""
        return _osgFX.MultiTextureControl_getTextureWeight(self, *args)

    def getNumTextureWeights(self):
        """getNumTextureWeights(MultiTextureControl self) -> unsigned int"""
        return _osgFX.MultiTextureControl_getNumTextureWeights(self)

MultiTextureControl_swigregister = _osgFX.MultiTextureControl_swigregister
MultiTextureControl_swigregister(MultiTextureControl)

class Registry(osg.Referenced):
    """Proxy of C++ osgFX::Registry class"""
    __swig_setmethods__ = {}
    for _s in [osg.Referenced]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Registry, name, value)
    __swig_getmethods__ = {}
    for _s in [osg.Referenced]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, Registry, name)
    def __init__(self, *args, **kwargs): raise AttributeError("No constructor defined")
    __repr__ = _swig_repr
    def instance():
        """instance() -> Registry"""
        return _osgFX.Registry_instance()

    if _newclass:instance = staticmethod(instance)
    __swig_getmethods__["instance"] = lambda x: instance
    def registerEffect(self, *args):
        """registerEffect(Registry self, Effect effect)"""
        return _osgFX.Registry_registerEffect(self, *args)

    def removeEffect(self, *args):
        """removeEffect(Registry self, Effect effect)"""
        return _osgFX.Registry_removeEffect(self, *args)

    def getEffectMap(self):
        """getEffectMap(Registry self) -> osgFX::Registry::EffectMap const &"""
        return _osgFX.Registry_getEffectMap(self)

Registry_swigregister = _osgFX.Registry_swigregister
Registry_swigregister(Registry)

def Registry_instance():
  """Registry_instance() -> Registry"""
  return _osgFX.Registry_instance()

class Scribe(Effect):
    """Proxy of C++ osgFX::Scribe class"""
    __swig_setmethods__ = {}
    for _s in [Effect]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Scribe, name, value)
    __swig_getmethods__ = {}
    for _s in [Effect]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, Scribe, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::Scribe self) -> Scribe
        __init__(osgFX::Scribe self, Scribe copy, CopyOp copyop=SHALLOW_COPY) -> Scribe
        __init__(osgFX::Scribe self, Scribe copy) -> Scribe
        """
        this = _osgFX.new_Scribe(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(Scribe self) -> Object"""
        return _osgFX.Scribe_cloneType(self)

    def clone(self, *args):
        """clone(Scribe self, CopyOp copyop) -> Object"""
        return _osgFX.Scribe_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(Scribe self, Object obj) -> bool"""
        return _osgFX.Scribe_isSameKindAs(self, *args)

    def className(self):
        """className(Scribe self) -> char const *"""
        return _osgFX.Scribe_className(self)

    def libraryName(self):
        """libraryName(Scribe self) -> char const *"""
        return _osgFX.Scribe_libraryName(self)

    def accept(self, *args):
        """accept(Scribe self, NodeVisitor nv)"""
        return _osgFX.Scribe_accept(self, *args)

    def effectName(self):
        """effectName(Scribe self) -> char const *"""
        return _osgFX.Scribe_effectName(self)

    def effectDescription(self):
        """effectDescription(Scribe self) -> char const *"""
        return _osgFX.Scribe_effectDescription(self)

    def effectAuthor(self):
        """effectAuthor(Scribe self) -> char const *"""
        return _osgFX.Scribe_effectAuthor(self)

    def getWireframeColor(self):
        """getWireframeColor(Scribe self) -> Vec4f"""
        return _osgFX.Scribe_getWireframeColor(self)

    def setWireframeColor(self, *args):
        """setWireframeColor(Scribe self, Vec4f color)"""
        return _osgFX.Scribe_setWireframeColor(self, *args)

    def getWireframeLineWidth(self):
        """getWireframeLineWidth(Scribe self) -> float"""
        return _osgFX.Scribe_getWireframeLineWidth(self)

    def setWireframeLineWidth(self, *args):
        """setWireframeLineWidth(Scribe self, float w)"""
        return _osgFX.Scribe_setWireframeLineWidth(self, *args)

Scribe_swigregister = _osgFX.Scribe_swigregister
Scribe_swigregister(Scribe)

class SpecularHighlights(Effect):
    """Proxy of C++ osgFX::SpecularHighlights class"""
    __swig_setmethods__ = {}
    for _s in [Effect]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, SpecularHighlights, name, value)
    __swig_getmethods__ = {}
    for _s in [Effect]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, SpecularHighlights, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::SpecularHighlights self) -> SpecularHighlights
        __init__(osgFX::SpecularHighlights self, SpecularHighlights copy, CopyOp copyop=SHALLOW_COPY) -> SpecularHighlights
        __init__(osgFX::SpecularHighlights self, SpecularHighlights copy) -> SpecularHighlights
        """
        this = _osgFX.new_SpecularHighlights(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(SpecularHighlights self) -> Object"""
        return _osgFX.SpecularHighlights_cloneType(self)

    def clone(self, *args):
        """clone(SpecularHighlights self, CopyOp copyop) -> Object"""
        return _osgFX.SpecularHighlights_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(SpecularHighlights self, Object obj) -> bool"""
        return _osgFX.SpecularHighlights_isSameKindAs(self, *args)

    def className(self):
        """className(SpecularHighlights self) -> char const *"""
        return _osgFX.SpecularHighlights_className(self)

    def libraryName(self):
        """libraryName(SpecularHighlights self) -> char const *"""
        return _osgFX.SpecularHighlights_libraryName(self)

    def accept(self, *args):
        """accept(SpecularHighlights self, NodeVisitor nv)"""
        return _osgFX.SpecularHighlights_accept(self, *args)

    def effectName(self):
        """effectName(SpecularHighlights self) -> char const *"""
        return _osgFX.SpecularHighlights_effectName(self)

    def effectDescription(self):
        """effectDescription(SpecularHighlights self) -> char const *"""
        return _osgFX.SpecularHighlights_effectDescription(self)

    def effectAuthor(self):
        """effectAuthor(SpecularHighlights self) -> char const *"""
        return _osgFX.SpecularHighlights_effectAuthor(self)

    def getLightNumber(self):
        """getLightNumber(SpecularHighlights self) -> int"""
        return _osgFX.SpecularHighlights_getLightNumber(self)

    def setLightNumber(self, *args):
        """setLightNumber(SpecularHighlights self, int n)"""
        return _osgFX.SpecularHighlights_setLightNumber(self, *args)

    def getTextureUnit(self):
        """getTextureUnit(SpecularHighlights self) -> int"""
        return _osgFX.SpecularHighlights_getTextureUnit(self)

    def setTextureUnit(self, *args):
        """setTextureUnit(SpecularHighlights self, int n)"""
        return _osgFX.SpecularHighlights_setTextureUnit(self, *args)

    def getSpecularColor(self):
        """getSpecularColor(SpecularHighlights self) -> Vec4f"""
        return _osgFX.SpecularHighlights_getSpecularColor(self)

    def setSpecularColor(self, *args):
        """setSpecularColor(SpecularHighlights self, Vec4f color)"""
        return _osgFX.SpecularHighlights_setSpecularColor(self, *args)

    def getSpecularExponent(self):
        """getSpecularExponent(SpecularHighlights self) -> float"""
        return _osgFX.SpecularHighlights_getSpecularExponent(self)

    def setSpecularExponent(self, *args):
        """setSpecularExponent(SpecularHighlights self, float e)"""
        return _osgFX.SpecularHighlights_setSpecularExponent(self, *args)

SpecularHighlights_swigregister = _osgFX.SpecularHighlights_swigregister
SpecularHighlights_swigregister(SpecularHighlights)

class Validator(osg.StateAttribute):
    """Proxy of C++ osgFX::Validator class"""
    __swig_setmethods__ = {}
    for _s in [osg.StateAttribute]: __swig_setmethods__.update(getattr(_s,'__swig_setmethods__',{}))
    __setattr__ = lambda self, name, value: _swig_setattr(self, Validator, name, value)
    __swig_getmethods__ = {}
    for _s in [osg.StateAttribute]: __swig_getmethods__.update(getattr(_s,'__swig_getmethods__',{}))
    __getattr__ = lambda self, name: _swig_getattr(self, Validator, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(osgFX::Validator self) -> Validator
        __init__(osgFX::Validator self, Effect effect) -> Validator
        __init__(osgFX::Validator self, Validator copy, CopyOp copyop=SHALLOW_COPY) -> Validator
        __init__(osgFX::Validator self, Validator copy) -> Validator
        """
        this = _osgFX.new_Validator(*args)
        try: self.this.append(this)
        except: self.this = this
    def cloneType(self):
        """cloneType(Validator self) -> Object"""
        return _osgFX.Validator_cloneType(self)

    def clone(self, *args):
        """clone(Validator self, CopyOp copyop) -> Object"""
        return _osgFX.Validator_clone(self, *args)

    def isSameKindAs(self, *args):
        """isSameKindAs(Validator self, Object obj) -> bool"""
        return _osgFX.Validator_isSameKindAs(self, *args)

    def libraryName(self):
        """libraryName(Validator self) -> char const *"""
        return _osgFX.Validator_libraryName(self)

    def className(self):
        """className(Validator self) -> char const *"""
        return _osgFX.Validator_className(self)

    def getType(self):
        """getType(Validator self) -> osg::StateAttribute::Type"""
        return _osgFX.Validator_getType(self)

    def apply(self, *args):
        """apply(Validator self, State state)"""
        return _osgFX.Validator_apply(self, *args)

    def compileGLObjects(self, *args):
        """compileGLObjects(Validator self, State state)"""
        return _osgFX.Validator_compileGLObjects(self, *args)

    def compare(self, *args):
        """compare(Validator self, StateAttribute sa) -> int"""
        return _osgFX.Validator_compare(self, *args)

    def disable(self):
        """disable(Validator self)"""
        return _osgFX.Validator_disable(self)

Validator_swigregister = _osgFX.Validator_swigregister
Validator_swigregister(Validator)

# This file is compatible with both classic and new-style classes.


