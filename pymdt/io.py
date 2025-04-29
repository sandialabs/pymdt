import os

import MDT
import pymdt
import pymdt.utils

import System
import Common.Logging
from Common.Serialization import SerializerUtils as SUF
from Common.Serialization import ImporterUtils as IUF
from System import Exception as SYSEX

class ImportFormats:
    """A class used to organize the import file formats that can be used to read
       files from other applications.
    """
   
    Windmill = MDT.WindmillTextImporter.TXT_FORMAT
    """ The text format exported from a Windmill model. (\*.txt)
    """

    ReNCAT = MDT.ReNCATResultsImporter.JSON_FORMAT
    """ The JSON format exported from a ReNCAT model. (\*.json)
    """

    OpenDSS = MDT.OpenDSSImporter.DSS_FORMAT
    """ The OpenDSS file format. (\*.dss)
    """

    MDTProject = MDT.MDTProjectImporterExporter.PROJ_FORMAT
    """ The project files created by the MDT that include any external data
    packaged in. (\*.mpf)
    """
   
    
class details:
    
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
    def _onNeedUserInput(sender, args):
        if args.Message == MDT.ReNCATResultsImporter.INPUT_MSG:
            args.Answer = details._chooseReNCATSolution(args)

def ImportInputFile(file_name, format=None, errLog: Common.Logging.Log=None) -> Common.Logging.Log:
    """ Imports the file with the supplied name and loads MDT inputs from it.
    
    It is possible that multiple file types can be associated with the same file
    extension.  For example, several applications store their inputs in JSON
    files with a .json extension.  To disambiguate, you can provide an instance
    of one of the constants in the ImportFormats class as the format argument.
    
    There are a few file types that the MDT is able to import.  Examples include:
        * MDT Project Files (\*.mpf)
        * OpenDSS Files (\*.dss)
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
    errLog: Common.Logging.Log
        An optional log into which to merge any messages resulting from the 
        import operation.
    undos: Common.Undoing.IUndoPack
        An optional undo pack into which to load the undoable objects generated
        during this operation (if any).
    
    Returns
    -------
    Common.Logging.Log:
        A log of any and all messages produced during the import operation and
        any that may have been in the provided errLog argument.  If the provided
        errLog was None, the return will be a newly created log with only those
        messages created during the import.
    """
    ext = os.path.splitext(file_name)[-1]
    fileFmt = format or IUF.FindFileFormat(SUF.INPUT_TYPE_TAG, ext)
    serializer = IUF.GetImporter(SUF.INPUT_TYPE_TAG, fileFmt)
    slog = Common.Logging.Log()
    
    hdnlr = getattr(serializer, "OnNeedUserInput")        
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
    binder = MDT.PRM.CustomSerializationBinder()
    if errLog is None: errLog = Common.Logging.Log()
    
    try:
        return serializer.Load(
            SUF.INPUT_TYPE_TAG, MDT.Driver.INSTANCE, binder, errLog
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

