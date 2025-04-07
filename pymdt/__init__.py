import os
import sys
import subprocess
import clr
import System

MDT_VERSION = System.Version(1, 4, 2520, 0)
MDT_BIN_DIR=None
MDT_DATA_DIR=None
MDT_SPEC_DB_DIR=None

for px in sys.argv:
    argInfo = px.split("=")
    key = argInfo[0].strip() if (len(argInfo) > 1) else ""
    value = argInfo[1].strip() if (len(argInfo) > 1) else ""
    
    if key == "MDT_VERSION":
        MDT_VERSION = System.Version.Parse(value)
    elif key == "MDT_BIN_DIR":
        MDT_BIN_DIR = value
    elif key == "MDT_DATA_DIR":
        MDT_DATA_DIR = value

if "__PYMDT_DOC_BUILD__" in os.environ:
    MDT_BIN_DIR = os.environ["__PYMDT_DOC_BUILD_DIR__"]
        
if MDT_BIN_DIR is None:
    MDT_BIN_DIR = os.path.join(
        "C:\\", "Program Files", "Sandia National Laboratories",
        "Microgrid Design Toolkit v" + MDT_VERSION.ToString()
        )

# If building docs, then make sure the SpecDB directory is set.  Otherwise,
# leave it at whatever it is.  Even None.  If None, the MDT will try and find
# it in the default location.
if MDT_SPEC_DB_DIR is None and "__PYMDT_DOC_BUILD__" in os.environ:    
    MDT_SPEC_DB_DIR = os.environ["__PYMDT_DOC_BUILD_DIR__"]
    
if "__PYMDT_DOC_BUILD__" not in os.environ and MDT_DATA_DIR is None:
    MDT_DATA_DIR = os.path.join(
        "C:\\", "ProgramData", "Sandia National Laboratories",
        "Microgrid Design Toolkit"
        )
    
if not os.path.exists(MDT_BIN_DIR):
    raise FileNotFoundError(
        "MDT binary directory not found.  Value is: " + MDT_BIN_DIR
        )

if "__PYMDT_DOC_BUILD__" not in os.environ:
    if not os.path.exists(MDT_DATA_DIR):
        raise FileNotFoundError(
            "MDT data directory not found.  Value is: " + MDT_DATA_DIR
            )
   
sys.path.append(MDT_BIN_DIR)

clr.AddReference(r"MDT-AC")
clr.AddReference(r"MDT-PRM-x64")

if "__PYMDT_DOC_BUILD__" not in os.environ:
    MDT_DATA_VER_DIR = os.path.join(MDT_DATA_DIR, MDT_VERSION.ToString())

import MDT
import Common

# This log is the default log used by a pymdt app when another log has not
# been provided to methods that make input changes that may be rejected.  It
# is recommended that this log be viewed frequently during the input phase
# and that it also be reviewed before solving.
GlobalErrorLog = Common.Logging.Log()

def _InvokeFilePath():
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return os.path.join(MDT_DATA_VER_DIR, "been.invoked")

def _IsFirstAppRun():
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return not os.path.exists(_InvokeFilePath())
    else:
        return False

if "__PYMDT_DOC_BUILD__" not in os.environ and _IsFirstAppRun():
    if not os.path.exists(MDT_DATA_VER_DIR): os.makedirs(MDT_DATA_VER_DIR)
    # using the MDT GUI manager for ease. Python users would probably prefer
    # not to have MDT GUI components popping up so may in the future create some
    # other non-GUI facility for this.  Not worth the work for now.
    subprocess.run([os.path.join(MDT_BIN_DIR, "MDT-DB-Manager.exe")])
    # Create the "been.invoked" file.  It has nothing in it.
    with open(_InvokeFilePath(), 'a') as fp: pass    
    
try:
    print("Looking for specDB in " + MDT_SPEC_DB_DIR if MDT_SPEC_DB_DIR else " the default loc.")
    MDT.UtilFuncs.InitializeDB(MDT_SPEC_DB_DIR)
    
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        print("DB Initialized")
        _ = MDT.Driver.INSTANCE
        print("Get the Driver Instance")
        MDT.Driver.INSTANCE.Interface = MDT.Driver.InterfaceEnum.PyMDT
        print("Set the interface type to PyMDT")
        MDT.Driver.LogEntryRegistry.AddTabooTag("W0025")
except System.Exception as e:
    raise Exception(
        "Caught a system exception while trying to initialize the MDT " + \
        "Specifications Database and/or Driver reading " + str(e) + "."
        )
except BaseException as e:
    print("Exception, DBG=" + MDT.UtilFuncs.DBG)
    raise Exception(
        "Caught a python exception while trying to initialize the MDT " + \
        "Specifications Database and/or Driver reading " + str(e) + "."
        )
except:
    raise Exception(
        "Caught an unknown exception while trying to initialize the MDT " + \
        "Specifications Database and/or Driver."
        )
