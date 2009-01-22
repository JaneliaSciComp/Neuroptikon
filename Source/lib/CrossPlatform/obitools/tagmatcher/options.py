def addTagMatcherErrorOptions(optionManager):
    optionManager.add_option('-E','--emax',
                             action='store',
                             metavar="<##>",
                             type="int",dest="emax",
                             default=None,
                             help="keep match with no more than emax errors")

    optionManager.add_option('-e','--emin',
                             action='store',
                             metavar="<##>",
                             type="int",dest="emin",
                             default=0,
                             help="keep match with at least emin errors")
