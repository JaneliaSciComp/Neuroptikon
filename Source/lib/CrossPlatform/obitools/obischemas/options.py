def addConnectionOptions(optionManager):
    
    optionManager.add_option('-d','--dbname',
                             action="store", dest="dbname",
                             metavar="<DB NAME>",
                             type="string",
                             help="OBISchema database name containing"
                                  "taxonomical data")

    optionManager.add_option('-H','--host',
                             action="store", dest="dbhost",
                             metavar="<DB HOST>",
                             type="string",
                             help="host hosting OBISchema database")

    optionManager.add_option('-U','--user',
                             action="store", dest="dbuser",
                             metavar="<DB USER>",
                             type="string",
                             help="user for OBISchema database connection")

    optionManager.add_option('-W','--password',
                             action="store", dest="dbpassword",
                             metavar="<DB PASSWORD>",
                             type="string",
                             help="password for OBISchema database connection")

    optionManager.add_option('-A','--autocommit',
                             action="store_true",dest="autocommit",
                             default=False,
                             help="add commit action after each query")