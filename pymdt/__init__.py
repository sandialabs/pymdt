import os
import sys
import subprocess
import clr
import System

from enum import Enum

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

class interface_enum(Enum):
    
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        PyMDT = MDT.Driver.InterfaceEnum.PyMDT

        COMMAND_LINE = MDT.Driver.InterfaceEnum.COMMAND_LINE

        PRIMARY_GUI = MDT.Driver.InterfaceEnum.PRIMARY_GUI
    else:
        PyMDT = 0

        COMMAND_LINE = 1

        PRIMARY_GUI = 2

class DriverProxy:
    
    @staticmethod
    @property
    def INSTANCE():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return None
        else:
            return MDT.Driver.INSTANCE
        
    @staticmethod
    @property
    def LoadTiers():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.LoadTiers
        else:
            return []
        
    @staticmethod
    @property
    def PRMSettings():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.PRMSettings
        else:
            return None
             
    @staticmethod
    @property
    def LineSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.LineSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def DieselGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.DieselGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def NaturalGasGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.NaturalGasGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def PropaneGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.PropaneGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def DieselTankSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.DieselTankSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def PropaneTankSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.PropaneTankSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def SolarGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.SolarGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def WindGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.WindGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def HydroGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.HydroGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def BatteryGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.BatteryGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def InverterGeneratorSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.InverterGeneratorSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def UninterruptiblePowerSupplySpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.UninterruptiblePowerSupplySpecifications
        else:
            return []
        
    @staticmethod
    @property
    def TransformerSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.TransformerSpecifications
        else:
            return []
        
    @staticmethod
    @property
    def SwitchSpecifications():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.SwitchSpecifications
        else:
            return []
        
    @staticmethod
    def MakeLoadDataDirectory():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.MakeLoadDataDirectory()
        else:
            return ""
        
    @staticmethod
    def MakeThermalLoadDataDirectory():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.MakeThermalLoadDataDirectory()
        else:
            return ""
        
    @staticmethod
    def MakeSolarDataDirectory():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.MakeSolarDataDirectory()
        else:
            return ""
        
    @staticmethod
    def MakeWindDataDirectory():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.MakeWindDataDirectory()
        else:
            return ""

    @staticmethod
    def MakeHydroDataDirectory():
        if "__PYMDT_DOC_BUILD__" not in os.environ:
            return MDT.Driver.INSTANCE.MakeHydroDataDirectory()
        else:
            return ""


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
    _ = DriverProxy.INSTANCE
    
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        MDT.Driver.INSTANCE.Interface = interface_enum.PyMDT
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
