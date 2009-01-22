def addSequenceEditTagOptions(optionManager):
    
    optionManager.add_option('-R','--rename-tag',
                             action="append", 
                             dest='renameTags',
                             metavar="<OLD_NAME:NEW_NAME>",
                             type="string",
                             default=[],
                             help="change tag name from OLD_NAME to NEW_NAME")

    optionManager.add_option('-D','--delete-tag',
                             action="append", 
                             dest='deleteTags',
                             metavar="<TAG_NAME>",
                             type="string",
                             default=[],
                             help="delete tag TAG_NAME")

    optionManager.add_option('-S','--set-tag',
                             action="append", 
                             dest='setTags',
                             metavar="<TAG_NAME:PYTHON_EXPRESSION>",
                             type="string",
                             default=[],
                             help="Add a new tag named TAG_NAME with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('-I','--set-identifier',
                             action="store", 
                             dest='setIdentifier',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence identifier with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('-T','--set-definition',
                             action="store", 
                             dest='setDefinition',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence definition with "
                                  "a value computed from PYTHON_EXPRESSION")
    
    optionManager.add_option('-O','--only-valid-python',
                             action="store_true", 
                             dest='onlyValid',
                             default=False,
                             help="only valid python expressions are allowed")
    
  


def sequenceTaggerGenerator(options):
    toDelete = options.deleteTags[:]
    toRename = [x.split(':',1) for x in options.renameTags if len(x.split(':',1))==2]
    toSet    = [x.split(':',1) for x in options.setTags if len(x.split(':',1))==2]
    newId    = options.setIdentifier
    newDef   = options.setDefinition
    
    def sequenceTagger(seq):
        for i in toDelete:
            if i in seq:
                del seq[i]
        for o,n in toRename:
            if o in seq:
                seq[n]=seq[o]
                del seq[o]
        for i,v in toSet:
            try:
                val = eval(v,{'sequence':seq},seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = v
            seq[i]=val
        if newId is not None:
            try:
                val = eval(newId,{'sequence':seq},seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newId
            seq.id=val
        if newDef is not None:
            try:
                val = eval(newDef,{'sequence':seq},seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newDef
            seq.definition=val
        return seq
    
    return sequenceTagger