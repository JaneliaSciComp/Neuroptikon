#!/usr/bin/env python
"""
A higher level Gene Ontology representation in Python

=======
License
=======

Copyright (c) 2009 Tamas Nepusz <tamas@cs.rhul.ac.uk>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

__author__  = "Tamas Nepusz"
__email__   = "tamas@cs.rhul.ac.uk"
__copyright__ = "Copyright (c) 2009, Tamas Nepusz"
__license__ = "MIT"
__version__ = "0.1"

__all__ = ["Annotation", "AnnotationFile", "Tree", "Term"]

from collections import deque


class Annotation(object):
    """Class representing a GO annotation (possibly parsed from an
    annotation file).
    
    The class has the following attributes (corresponding to the
    columns of a GO annotation file):
        
    - ``db``: refers to the database from which the identifier
      in the next column (``db_object_id``) is drawn
    - ``db_object_id``: a unique identifier in ``db`` for the
      item being annotated.
    - ``db_object_symbol``: a unique and valid symbol to which
      ``db_object_id`` is matched. Usually a symbol that means
      something to a biologist.
    - ``qualifiers``: a list of flags that modify the interpretation
      of the annotation (e.g., ``NOT``). Note that this is always
      a list, even when no qualifier exists.
    - ``go_id``: the GO identifier for the term attributed to
      ``db_object_id``.
    - ``db_references``: a list of unique identifiers for a single
      source cited as an authority for the attribution of the
      ``go_id`` to the ``db_object_id``. May be a literature or
      a database record.
    - ``evidence_code``: the GO evidence code
    - ``with``: required for some evidence codes. Holds an additional
      identifier for certain evidence codes.
    - ``aspect``: one of ``P`` (biological process), ``F``
      (molecular function) or ``C`` (cellular compartment).
    - ``db_object_name``: name of gene or gene product
    - ``db_object_synonyms``: a gene symbol or some other human-readable text
    - ``db_object_type``: what kind of thing is being annotated.
      This is either gene (``SO:0000704``), transcript (``SO:0000673``),
      protein (``SO:0000358``), ``protein_structure`` or ``complex``.
    - ``taxons``: taxonomic identifiers (at most two, at least 1). This is
      always a list
    - ``date``: date on which the annotation was made
    - ``assigned_by``: the database which made the annotation.
    """

    __slots__ = ["db", "db_object_id", "db_object_symbol", \
            "qualifiers", "go_id", "db_references", \
            "evidence_code", "with", "aspect", \
            "db_object_name", "db_object_synonyms", \
            "db_object_type", "taxons", "date", \
            "assigned_by"]

    def __init__(self, *args, **kwds):
        """Constructs an annotation. Use keyword arguments to specify the values
        of the different attributes. If you use positional arguments, the order
        of the arguments must be the same as they are in the GO annotation file.
        No syntax checking is done on the values entered, but attributes with a
        maximum cardinality more than one are converted to lists automatically.
        (If you specify a string with vertical bar separators as they are in the
        input file, the string will be splitted appropriately)."""
        if len(args) == 1 and not kwds:
            args = args[0].strip().split("\t")
        for (name, value) in zip(self.__slots__, args):
            setattr(self, name, value)
        for name, value in kwds.iteritems():
            setattr(self, name, kwds[value])
        for name in self.__slots__:
            if not hasattr(self, name):
                setattr(self, name, "")
        self._polish_attributes()

    def _polish_attributes(self):
        """Ensures that the atributes are of the right type"""
        self._ensure_list("qualifiers")
        self._ensure_list("db_references")
        self._ensure_list("with")
        self._ensure_list("db_object_synonyms")
        self._ensure_list("taxons")

    def _ensure_list(self, attr):
        """Ensures that a given attribute is a list and not a string"""
        value = getattr(self, attr)
        if not isinstance(value, list):
            if value == "":
                setattr(self, attr, [])
            else:
                setattr(self, attr, value.split("|"))

    def __repr__(self):
        params = ",".join("%s=%r" % (name, getattr(self, name)) \
                for name in self.__slots__)
        return "%s(%s)" % (self.__class__.__name__, params)


class AnnotationFile(object):
    """A parser class that processes GO annotation files"""

    def __init__(self, fp):
        """Creates an annotation file parser that reads the given file-like
        object. You can also specify filenames. If the filename ends in ``.gz``,
        the file is assumed to contain gzipped data and it will be unzipped
        on the fly. Example:

          >>> import gene_ontology as go
          >>> parser = go.AnnotationFile("gene_association.sgd.gz")

        To read the annotations in the file, you must iterate over the parser
        as if it were a list. The iterator yields `Annotation` objects.
        """
        if isinstance(fp, (str, unicode)):
            if fp[-3:] == ".gz":
                from gzip import GzipFile
                self.fp = GzipFile(fp)
            else:
                self.fp = file(fp)
        else:
            self.fp = fp
        self.lineno = 0

    def annotations(self):
        """Iterates over the annotations in this annotation file,
        yielding an `Annotation` object for each annotation."""
        for line in self.fp:
            self.lineno += 1
            if not line or line[0] == '!':
                # This is a comment line
                continue
            try:
                yield Annotation(line)
            except TypeError, ex:
                raise ParseError("cannot parse annotation", self.lineno)

    def __iter__(self): return self.annotations()


class Tree(object):
    """Class representing a GO tree

    A GO tree contains many GO terms represented by `Term`
    objects.
    """

    def __init__(self):
        """Constructs an empty GO tree."""
        self.terms = {}
        self.aliases= {}

    def add(self, term):
        """Adds a `Term` to this GO tree"""
        self.terms[term.id] = term

    def add_alias(self, canonical, alias):
        """Adds an alias to the given canonical term in the GO tree"""
        self.aliases[alias] = canonical

    def lookup(self, id):
        """Looks up a `Term` in this tree by ID. Also cares about alternative
        IDs"""
        try:
            return self.terms[id]
        except KeyError:
            return self.terms[self.aliases[id]]

    def _ensure_term(self, term_or_id):
        """Given a `Term` or a GO term ID, returns an object
        that is surely a `Term`"""
        if isinstance(term_or_id, Term): return term_or_id
        return self.lookup(term_or_id)

    def parents(self, term_or_id):
        """Returns the parents of a `Term` in this tree.
        `term_or_id` can be a GO term ID or a `Term`.
        The result is a list of `Term` instances."""
        term = self._ensure_term(term_or_id)
        parent_ids = term.tags.get("is_a", [])
        return [self.lookup(id.value) for id in parent_ids]

    def paths_to_root(self, *args):
        terms = [self._ensure_term(term_or_id) for term_or_id in args]
        queue = deque([(term, [term]) for term in terms])
        while queue:
            first, path = queue.popleft()
            parents = self.parents(first)
            if not parents: yield path
            for parent in self.parents(first):
                queue.append((parent, path + [parent]))

    def to_igraph(self, rel="is_a"):
        """Returns an igraph graph representing this GO tree"""
        import igraph
        g = igraph.Graph(n=len(self.terms), directed=True)
        g.vs["id"] = self.terms.keys()
        g.vs["name"] = [term.name for term in self.terms.values()]

        term_id_to_idx = dict(zip(self.terms.keys(),
            range(len(self.terms))))
        el = []
        for id, term in self.terms.iteritems():
            v1 = term_id_to_idx[id]
            for parent_id in term.tags.get(rel, []):
                v2 = term_id_to_idx.get(parent_id.value, None)
                if v2 is None: continue
                el.append((v1, v2))

        g.add_edges(el)
        return g

    @classmethod
    def from_obo(klass, fp):
        """Constructs a GO tree from an OBO file. `fp` is a file pointer
        to the OBO file we want to use"""
        import gene_ontology.obo as obo
        parser = obo.Parser(fp)
        tree = klass()
        for stanza in parser:
            term = Term.from_stanza(stanza)
            tree.add(term)
            for alt_id in stanza.tags.get("alt_id", []):
                tree.add_alias(term.id, alt_id.value)
        return tree


    def __len__(self):
        return len(self.terms)


class Term(object):
    """Class representing a single GO term"""

    __slots__ = ["id", "name", "tags"]

    def __init__(self, id, name="", tags=None):
        """Constructs a GO term"""
        self.id = str(id)
        self.name = str(name)
        if tags:
            self.tags = dict(tags)
        else:
            self.tags = {}

    def __repr__(self):
        """String representation of a GO term"""
        return "%s(%r, %r, %r)" % (self.__class__.__name__,
                self.id, self.name, self.tags)

    def __str__(self):
        """Returns just the ID of the GO term"""
        return self.id

    @classmethod
    def from_stanza(klass, stanza):
        """Constructs a GO term from a stanza coming from an
        OBO file. `stanza` must be an instance of `gene_ontology.obo.Stanza`.
        """
        id = stanza.tags["id"][0]
        name = stanza.tags.get("name", [id])[0]
        return klass(id, name, stanza.tags)

def test():
    from time import time
    from gzip import GzipFile

    start = time()
    tree = Tree.from_obo(file("gene_ontology.obo"))
    end = time()

    print len(tree), "terms in GO tree parsed in %.2f seconds" % (end-start)
    for path in tree.paths_to_root("GO:0009651"):
        print " -> ".join(node.name for node in path)

    start = time()
    ann_file = AnnotationFile(GzipFile("gene_association.sgd.gz"))
    l = sum(1 for _ in ann_file)
    end = time()
    print l, "annotations for yeast parsed in %.2f seconds" % (end-start)


if __name__ == "__main__":
    import sys
    sys.exit(test())
