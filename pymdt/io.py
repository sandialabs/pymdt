import os

import MDT
import pymdt
import pymdt.utils

from enum import Enum

import System
import Common.Logging
from Common.Serialization import SerializerUtils as SUF
from Common.Serialization import ImporterUtils as IUF
from System import Exception as SYSEX

class ImportFormats(Enum):
    """A class used to organize the import file formats that can be used to read
       files from other applications.
    """
   
    Windmill = MDT.WindmillTextImporter.TXT_FORMAT
    r""" The text format exported from a Windmill model. (\*.txt)
    """

    ReNCAT = MDT.ReNCATResultsImporter.JSON_FORMAT
    r""" The JSON format exported from a ReNCAT model. (\*.json)
    """

    OpenDSS = MDT.OpenDSSImporter.DSS_FORMAT
    r""" The OpenDSS file format. (\*.dss)
    """
    
    PandaPower = MDT.PandaPowerImporter.JSON_FORMAT
    r""" The Panda Power JSON file format. (\*.json)
    """

    MDTProject = MDT.MDTProjectImporterExporter.PROJ_FORMAT
    r""" The project files created by the MDT that include any external data
    packaged in. (\*.mpf)
    """


class details:
    
    @staticmethod
    def _askYesNoQuestion(args):
        msg = ""

        for e in args.Messages:
            msg = e.Message
            break

        yeses = ["y", "yes", "yup", "yas"]
        nos = ["n", "no", "nope", "nar"]

        while True:
            try:
                resp = input(msg + "(Y or N):")
                respcf = resp.casefold()

                if respcf not in yeses and respcf not in nos:
                    raise ValueError(resp)
                
                choice = respcf in yeses

                break
            except ValueError:
                print("Invalid input.  Please enter Y or N.")

        if choice:
            return Common.GUI.Util.GraphicalMessageManager.OperationResult.YES
        else:
            return Common.GUI.Util.GraphicalMessageManager.OperationResult.NO
    
    @staticmethod
    def _chooseReNCATSolution(args) -> str:
        print(args.Message)
        i = 0
        for e in args.Messages:
            print(str(i) +": " + e.Message)
            i += 1

        while True:
            try:
                choice = int(
                    input("\nEnter the number associated with your choice: ")
                    )

                if (choice < 0) or (choice >= args.Messages.Count):
                    raise ValueError
                    
                break
            except ValueError:
                print(
                    "Invalid input.  Please enter an integer from the list " +
                    "provided."
                    )

        i = 0
        for e in args.Messages:
            if i == choice:
               return e.Message
            i += 1

        return None
    
    @staticmethod
    def _chooseReNCATGeneratorTypes(args):
        print("Select a fuel type for each of the following generators " +
              "(1=Diesel, 2=Natural Gas, 3=Propane, 4=Solar, 5=Wind, 6=Hydro):")

        ret = System.Collections.Generic.Dictionary[System.String, System.String]()

        for le in args.Messages:
            
            choice = 2

            while True:
                try:
                    choice = int(input(le.Tag + " / " + le.Message + ": "))

                    if (choice < 1) or (choice > 6):
                        raise ValueError
                    
                    break
                except ValueError:
                    print(
                        "Invalid input.  Please enter an integer from the list " +
                        "provided (1-6)."
                        )

            ret.Add(
                le.Tag + "/" + le.Message,
                ["Diesel", "Natural Gas", "Propane", "Solar", "Wind", "Hydro"][choice-1]
                )

        return ret

    @staticmethod
    def _askAboutReNCATMissions(args):        
        return details._askYesNoQuestion(args)

    @staticmethod
    def _askAboutInstallSwitchMessages(args):
        return details._askYesNoQuestion(args)

    @staticmethod
    def _onNeedUserInput(sender, args):
        if args.Message == MDT.ReNCATResultsImporter.INPUT_MSG:
            args.Answer = details._chooseReNCATSolution(args)
        elif args.Message == MDT.ReNCATResultsImporter.GEN_TYPE_MSG:
            args.Answer = details._chooseReNCATGeneratorTypes(args)
        elif args.Message == MDT.ReNCATResultsImporter.READ_MISSION_MSG:
            args.Response = details._askAboutReNCATMissions(args)
        elif args.Message == MDT.OpenDSSImporter.INSTALL_SWITCH_MSG or \
            args.Message == MDT.PandaPowerImporter.INSTALL_SWITCH_MSG:
            args.Response = details._askAboutInstallSwitchMessages(args)

    class _DefaultUserInputHandler:

        def __init__(self):
            self._defAnswer = None
            self._defResponse = None

        def _onDefaultedUserInput(self, sender, args):

            if(self._defAnswer is not None):
                args.Answer = self._defAnswer.get(args.Message, None)

            if(self._defResponse is not None):
                args.Response = self._defResponse.get(
                    args.Message,
                    Common.GUI.Util.GraphicalMessageManager.OperationResult.NO
                    )

def ImportInputFile(file_name, format=None, errLog: Common.Logging.Log=None, **kwargs) -> Common.Logging.Log:
    r""" Imports the file with the supplied name and loads MDT inputs from it.
    
    It is possible that multiple file types can be associated with the same file
    extension.  For example, several applications store their inputs in JSON
    files with a .json extension.  To disambiguate, you can provide an instance
    of one of the constants in the ImportFormats class as the format argument.
    
    There are a few file types that the MDT is able to import.  Examples include:
        * MDT Project Files (\*.mpf)
        * OpenDSS Files (\*.dss)
        * Panda Power JSON Files (\*.json)
        * ReNCAT JSON Files (\*.json)
        * Windmill Export Files (\*.txt)
    
    Parameters
    ----------
    file_name: str
        The name of the file from which to read the inputs.  The extension of
        the provided name will determine the importer used unless a valid format
        argument is provided.
    format
        An optional identifier of the file format intended.  If provided, this
        will take precedence over the extension of the file name.  This should
        be one of the members of the ImportFormats class defined in this module.
        If more than one format uses the same extension, .json for example, then
        this argument is highly recommended.
    errLog: Common.Logging.Log
        An optional log into which to merge any messages resulting from the 
        import operation.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        invert_bus_coords: bool
            Whether or not to invert the coordinates read in for busses for the
            purposes of display.  This prevents the common issue of having a
            display that is mirrored about the y axis from what is expected.
            The default is True.
        default_response:
            If provided, then the user will not be asked for input by the
            importer and in any place that the response result is needed, this
            map will be used to provide the answer.  The response to a given
            question is one of the members of
            Common.GUI.Util.GraphicalMessageManager.OperationResult.  This map
            must use the questions as keys and the operation result as values.
            The keys are strings and can be obtained from the specific
            importers.
          
            This is an advanced feature that can in some cases,
            require inside knowledge of the MDT object model.  Contact the
            developers for help if needed.

            Providing either this or the default_answer will prevent the
            asking of any questions of the user by the importer so provide both
            if needed.
        default_answer:
            If provided, then the user will not be asked for input by the
            importer and in any place that the answer result is needed, this
            map will be used to provide the answer.  The answer is any object
            that satisfied the request of the specific importer.    This map
            must use the questions as keys and the operation result as values.
            
            This is an advanced feature that can in some cases,
            require inside knowledge of the MDT object model.  Contact the
            developers for help if needed.

            Providing either this or the default_response will prevent the
            asking of any questions of the user by the importer so provide both
            if needed.
    
    Returns
    -------
    Common.Logging.Log:
        A log of any and all messages produced during the import operation and
        any that may have been in the provided errLog argument.  If the provided
        errLog was None, the return will be a newly created log with only those
        messages created during the import.
    """
    ext = os.path.splitext(file_name)[-1]
    
    if hasattr(format, "value"): format = format.value
    fileFmt = format or IUF.FindFileFormat(SUF.INPUT_TYPE_TAG, ext)
    serializer = IUF.GetImporter(SUF.INPUT_TYPE_TAG, fileFmt)
    if pymdt.MDT_VERSION > System.Version(1, 4, 2699, 0):
        invert = kwargs.get("invert_bus_coords", True)
        serializer.InvertBusCoordinatesForDisplay = invert

    slog = Common.Logging.Log()
    hdnlr = getattr(serializer, "OnNeedUserInput")
    
    if "default_response" in kwargs or  "default_answer" in kwargs:
        h = details._DefaultUserInputHandler()
        h._defAnswer = kwargs.get("default_answer", None)
        h._defResponse = kwargs.get("default_response", None)
        hdnlr += h._onDefaultedUserInput
    else:
        hdnlr += details._onNeedUserInput

    try:
        slog = serializer.Import(file_name)
    except SYSEX as e:
        slog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except BaseException as e:
        slog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except:
        slog.AddEntry(
            Common.Logging.LogCategories.Error,
            "Caught an unknown exception while trying to import from file " + \
            file_name
            )
    if errLog is not None: errLog.Merge(slog)
    return slog

def ReadInputFile(file_name, errLog: Common.Logging.Log=None, **kwargs) -> Common.Logging.Log:
    """ Reads the file with the supplied name and loads MDT inputs from it.
        
    Parameters
    ----------
    file_name: str
        The name of the file from which to read the inputs.  The provided name
        should have a ".mbf" extension.
    errLog: Common.Logging.Log
        An optional log into which to merge any messages resulting from the load
        operation.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        make_backup: bool
            Whether or not to write a backup file if the loaded file is from an
            older version of the MDT.  The default is False.
    
    Returns
    -------
    Common.Logging.Log:
        A log of any and all messages produced during the load operation and any
        that may have been in the provided errLog argument.  If the provided
        errLog was None, the return will be a newly created log with only those
        messages created during the load.
    """
    ext = os.path.splitext(file_name)[-1]
    fileFmt = SUF.FindFileFormat(SUF.SAVE_INPUT_TYPE_TAG, ext)
    serializer = SUF.GetSerializer(SUF.SAVE_INPUT_TYPE_TAG, fileFmt, file_name)
    serializer.MakeBackups = kwargs.get("make_backup", False)
    if errLog is None: errLog = Common.Logging.Log()
    
    try:
        return serializer.Load(
            SUF.INPUT_TYPE_TAG, MDT.Driver.INSTANCE, errLog
            )
    except SYSEX as e:
        errLog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except BaseException as e:
        errLog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except:
        errLog.AddEntry(
            Common.Logging.LogCategories.Error,
            "Caught an unknown exception while trying to read from file " + \
            file_name
            )
    return errLog

def WriteInputFile(file_name, errLog: Common.Logging.Log=None) -> Common.Logging.Log:
    """ Writes the current MDT inputs to a file with the supplied name.
        
    Parameters
    ----------
    file_name: str
        The name of the file into which to write the inputs.  The provided name
        should have a ".mbf" extension.
    errLog: Common.Logging.Log
        An optional log into which to merge any messages resulting from the save
        operation.
    
    Returns
    -------
    Common.Logging.Log:
        A log of any and all messages produced during the save operation.  No
        matter whether an errLog is provided as a parameter to the method, the
        returned log will only contain those messages produced during the save
        operation.
    """
    ext = os.path.splitext(file_name)[-1]
    fileFmt = SUF.FindFileFormat(SUF.SAVE_INPUT_TYPE_TAG, ext)
    serializer = SUF.GetSerializer(SUF.SAVE_INPUT_TYPE_TAG, fileFmt, file_name)
    slog = Common.Logging.Log()
    
    try:
        slog = serializer.Save(
            SUF.INPUT_TYPE_TAG, MDT.Driver.INSTANCE, pymdt.MDT_VERSION
            )
    except SYSEX as e:
        slog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except BaseException as e:
        slog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except:
        slog.AddEntry(
            Common.Logging.LogCategories.Error,
            "Caught an unknown exception while trying to write to file " + \
            file_name
            )
        
    if errLog is not None: errLog.Merge(slog)
    return slog

def WriteOutputFile(file_name: str, sri, errLog: Common.Logging.Log=None) -> Common.Logging.Log:
    """ Writes an MDT results file for the provided solver run info object to
    a file with the supplied name.
        
    Parameters
    ----------
    file_name: str
        The name of the file into which to write the results.  The provided name
        have a ".mof" extension.
    sri
        The result set or sets to be written to the file.  This can be a
        collection of MDT.SolverRunInfo or just a single instance thereof.
    errLog: Common.Logging.Log
        An optional log into which to merge any messages resulting from the save
        operation.
    
    Returns
    -------
    Common.Logging.Log:
        A log of any and all messages produced during the save operation.  No
        matter whether an errLog is provided as a parameter to the method, the
        returned log will only contain those messages produced during the save
        operation.
    """
    slog = Common.Logging.Log()
    
    try:
        ext = os.path.splitext(file_name)[-1]
        fileFmt = SUF.FindFileFormat(SUF.SAVE_OUTPUT_TYPE_TAG, ext)
        serializer = SUF.GetSerializer(SUF.SAVE_OUTPUT_TYPE_TAG, fileFmt, file_name)
        drv = MDT.Driver.INSTANCE
        drv.OutputDataToSave.Clear()
        rvm = MDT.ResultViewManager()
        if not pymdt.utils.details._is_collection(sri): sri = [sri]
        for r in sri: rvm.get_SolverRunInfos().Add(r)
        drv.get_ResultViewManagers().Add(rvm)
        drv.get_OutputDataToSave().Add(rvm)
        slog = serializer.Save(SUF.OUTPUT_TYPE_TAG, drv, pymdt.MDT_VERSION)
        drv.get_ResultViewManagers().Remove(rvm)
        drv.OutputDataToSave.Clear()
    except SYSEX as e:
        slog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except BaseException as e:
        slog.AddEntry(Common.Logging.LogCategories.Error, str(e))
    except:
        slog.AddEntry(
            Common.Logging.LogCategories.Error,
            "Caught an unknown exception while trying to write to file " + \
            file_name
            )

    if errLog is not None: errLog.Merge(slog)
    return slog

