#!/usr/bin/env python
"""
Example script for the OBO parser that takes an OBO ontology file
and converts it into Cytoscape's ontology format.

Cytoscape's ontology format is used by the BiNGO Cytoscape plugin
for custom ontologies, so this script is handy if you have an
OBO ontology that you want to use in BiNGO.
"""

import optparse
import sys

import gene_ontology.obo as obo

class ConverterApplication(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("-c", "--curator", dest="curator",
                help="the content of the curator header field",
                default="GO")
        self.parser.add_option("-t", "--type", dest="type",
                help="the content of the type header field",
                default="process")

    def run(self):
        self.options, self.args = self.parser.parse_args()

        if not self.args:
            self.args = ["-"]

        for arg in self.args:
            if arg == "-":
                self.process_file(sys.stdin)
            else:
                f = open(arg)
                self.process_file(f)
                f.close()

    def process_file(self, f):
        parser = obo.Parser(f)
        out = sys.stdout
        print >>out, "(curator=%s)(type=%s)" % \
            (self.options.curator, self.options.type)
        for stanza in parser:
            if stanza.name != "Term": continue
            id = stanza.tags["id"][0].value
            if stanza.tags.get("name", []):
                name = stanza.tags["name"][0].value
            else:
                name = id
            out.write("%s = %s" % (self.process_id(id), name))
            out.write(self.format_isa(stanza.tags.get("is_a", [])))
            out.write(self.format_partof(stanza.tags.get("relationship", [])))
            out.write("\n")

    def format_isa(self, parents):
        if not parents: return ""
        ids = [self.process_id(str(parent)) for parent in parents]
        return " [isa: %s ]" % (" ".join(ids))

    def format_partof(self, rels):
        rels = [rel.value[8:] for rel in rels \
                if rel.value.startswith("part_of ")]
        if not rels: return ""
        ids = [self.process_id(rel) for rel in rels]
        return " [partof: %s ]" % (" ".join(ids))

    def process_id(self, id):
        if id.startswith("GO:"): return id[3:]
        return id


if __name__ == "__main__":
    sys.exit(ConverterApplication().run())
