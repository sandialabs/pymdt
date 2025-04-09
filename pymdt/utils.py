import numbers

import MDT
import System
import Common

from enum import Enum

import pymdt.distributions

class time_units(Enum):
    """ An enumeration of the possible time units for various inputs.  These are
    commonly used for data sets for example.
    """

    milliseconds = Common.Time.TimeAccumulation.Units.Milliseconds
    """ Indicates that a given time value is given in milliseconds.
    """

    seconds = Common.Time.TimeAccumulation.Units.Seconds
    """ Indicates that a given time value is given in seconds.
    """

    minutes = Common.Time.TimeAccumulation.Units.Minutes
    """ Indicates that a given time value is given in minutes.
    """

    hours = Common.Time.TimeAccumulation.Units.Hours
    """ Indicates that a given time value is given in hours.
    """

    days = Common.Time.TimeAccumulation.Units.Days
    """ Indicates that a given time value is given in days.
    """

    weeks = Common.Time.TimeAccumulation.Units.Weeks
    """ Indicates that a given time value is given in weeks.
    """

    months = Common.Time.TimeAccumulation.Units.Months
    """ Indicates that a given time value is given in months.
    """

    years = Common.Time.TimeAccumulation.Units.Years
    """ Indicates that a given time value is given in years.
    """

class find_fail_behavior(Enum):
    """ An enumeration of the possible responses to a failed attempt to find
    something in a list using the FindEntityByName function.
    """

    ignore = 0
    """ Indicates that the find function should just return None.
    """

    throw = 1
    """ Indicates that the find function should throw an exception.  See the
    docs for the FindEntityByName function for details of what the exception
    message will say.
    """

class text_alignment(Enum):
    """ An enumeration of the possible text alignment settings.  These are used
    for example by the node groups to place their text.
    """

    top_left = MDT.NodeGroup.TextAlignEnum.TopLeft
    """ Indicates that the text should be aligned to the top left of its parent.
    """

    top_center = MDT.NodeGroup.TextAlignEnum.TopCenter
    """ Indicates that the text should be aligned to the top center of its
    parent.
    """

    top_right = MDT.NodeGroup.TextAlignEnum.TopRight
    """ Indicates that the text should be aligned to the top right of its
    parent.
    """

    middle_left = MDT.NodeGroup.TextAlignEnum.MiddleLeft
    """ Indicates that the text should be aligned to the middle left of its
    parent.  This typically means centered vertically and aligned left
    horizontally.
    """

    middle_center = MDT.NodeGroup.TextAlignEnum.MiddleCenter
    """ Indicates that the text should be aligned to the middle center of its
    parent.  This typically means centered vertically and horizontally.
    """

    middle_right = MDT.NodeGroup.TextAlignEnum.MiddleRight
    """ Indicates that the text should be aligned to the middle right of its
    parent.  This typically means centered vertically and aligned right
    horizontally.
    """

    bottom_left = MDT.NodeGroup.TextAlignEnum.BottomLeft
    """ Indicates that the text should be aligned to the bottom left of its
    parent.
    """

    bottom_center = MDT.NodeGroup.TextAlignEnum.BottomCenter
    """ Indicates that the text should be aligned to the bottom center of its
    parent.
    """

    bottom_right = MDT.NodeGroup.TextAlignEnum.BottomRight
    """ Indicates that the text should be aligned to the bottom right of its
    parent.
    """

  
class details:
            
    currentLog: Common.Logging.Log

    @staticmethod
    def _log_merge_handler(sender, args):
        if details.currentLog is not None:
            details.currentLog.Merge(args.Log)
            
    @staticmethod
    def _extract_guid(identified, **kwargs):
        # can be missing all together, a string, or a System.Guid.  If missing,
        # do nothing. The default that already exists in the identified object
        # can be kept.
        guid = kwargs.get("guid")
        if guid:
            if type(guid) is str:
                guid = System.Guid(guid)
            identified.ResetUID(guid)
        
    @staticmethod
    def _execute_loggable_action(
        obj, cancelEvtName, l, **kwargs
        ) -> Common.Logging.Log:
        
        errLog = kwargs.get("err_log", pymdt.GlobalErrorLog)
        hdnlr = getattr(obj, cancelEvtName)
        
        hdnlr += details._log_merge_handler
        details.currentLog = errLog
        try:
            l()
        finally:
            details.currentLog = None
            hdnlr -= details._log_merge_handler
        return errLog
    
    @staticmethod
    def _execute_3_arg_add_with_undo(
        into, cancelEvtName, collectionGetterName, a1, a2, a3, **kwargs
        ) -> Common.Logging.Log:
        
        lst = getattr(into, collectionGetterName)
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()   
        return details._execute_loggable_action(
            into, cancelEvtName, lambda: lst().Add(a1, a2, a3, undos), **kwargs
            )
    
    @staticmethod
    def _execute_3_arg_add(
        into, cancelEvtName, collectionGetterName, a1, a2, a3, **kwargs
        ) -> Common.Logging.Log:
        
        lst = getattr(into, collectionGetterName)
        return details._execute_loggable_action(
            into, cancelEvtName, lambda: lst().Add(a1, a2, a3), **kwargs
            )
    
    @staticmethod
    def _execute_2_arg_add_with_undo(
        into, cancelEvtName, collectionGetterName, a1, a2, **kwargs
        ) -> Common.Logging.Log:
        
        lst = getattr(into, collectionGetterName)        
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()  
        return details._execute_loggable_action(
            into, cancelEvtName, lambda: lst().Add(a1, a2, undos), **kwargs
            )
    
    @staticmethod
    def _execute_2_arg_add(
        into, cancelEvtName, collectionGetterName, a1, a2, **kwargs
        ) -> Common.Logging.Log:
        
        lst = getattr(into, collectionGetterName)
        return details._execute_loggable_action(
            into, cancelEvtName, lambda: lst().Add(a1, a2), **kwargs
            )
    
    @staticmethod
    def _execute_1_arg_add_with_undo(
        into, cancelEvtName, collectionGetterName, item, **kwargs
        ) -> Common.Logging.Log:
        
        lst = getattr(into, collectionGetterName)        
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()     
        return details._execute_loggable_action(
            into, cancelEvtName, lambda: lst().Add(item, undos), **kwargs
            )
    
    @staticmethod
    def _execute_1_arg_add(
        into, cancelEvtName, collectionGetterName, item, **kwargs
        ) -> Common.Logging.Log:
        
        lst = getattr(into, collectionGetterName)
        return details._execute_loggable_action(
            into, cancelEvtName, lambda: lst().Add(item), **kwargs
            )
    
    @staticmethod
    def _execute_loggable_property_set_with_undo(
        obj, propName, value, custom_cancel_evt_name=None, **kwargs
        ) -> Common.Logging.Log:
        
        prop = getattr(obj, "set_" + propName)
        
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()
        
        if custom_cancel_evt_name is None: 
            custom_cancel_evt_name = "Change" + propName + "Canceled"
            
        return details._execute_loggable_action(
            obj, str(custom_cancel_evt_name), lambda: prop(undos, value),
            **kwargs
            )
    
    @staticmethod
    def _execute_loggable_property_set(
        obj, propName, value, custom_cancel_evt_name=None, **kwargs
        ) -> Common.Logging.Log:
        
        prop = getattr(obj, "set_" + propName)
        
        if custom_cancel_evt_name is None: 
            custom_cancel_evt_name = "Change" + propName + "Canceled"
            
        return details._execute_loggable_action(
            obj, str(custom_cancel_evt_name), lambda: prop(value), **kwargs
            )
    
    @staticmethod
    def _execute_loggable_indexed_property_set_with_undo(
        obj, propName, index, value, custom_cancel_evt_name=None, **kwargs
        ) -> Common.Logging.Log:
        
        prop = getattr(obj, "set_" + propName)
        
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()
        
        if custom_cancel_evt_name is None: 
            custom_cancel_evt_name = "Change" + propName + "Canceled"
            
        return details._execute_loggable_action(
            obj, custom_cancel_evt_name, lambda: prop(index, undos, value),
            **kwargs
            )

    @staticmethod
    def _execute_loggable_indexed_property_set(
        obj, propName, index, value, custom_cancel_evt_name=None, **kwargs
        ) -> Common.Logging.Log:
        
        prop = getattr(obj, "set_" + propName)
        
        if custom_cancel_evt_name is None: 
            custom_cancel_evt_name = "Change" + propName + "Canceled"
            
        return details._execute_loggable_action(
            obj, custom_cancel_evt_name, lambda: prop(index, value), **kwargs
            )

    @staticmethod
    def _is_integer(n):
        if isinstance(n, int): return True
        if isinstance(n, float): return n.is_integer()
        return False

    @staticmethod
    def _is_iterable(item) -> bool:
        try:
            _ = iter(item)
            return True
        except:
            return False

    @staticmethod
    def _is_collection(item) -> bool:
        return (type(item) is not str) and details._is_iterable(item)
    
    @staticmethod
    def _extract_notes(entity, **kwargs):
        details._execute_loggable_property_set_with_undo(
            entity, "Notes", str(kwargs.get("notes", "")), **kwargs
            )
        
    @staticmethod    
    def _extract_failure_modes(unrel, **kwargs):
        fms = kwargs.get("failure_modes")
        if fms is None: return
        if not details._is_collection(fms): fms = [fms]
        for fm in fms:
            details._execute_1_arg_add_with_undo(
                unrel, "AddFailureModeCanceled", "get_FailureModes", fm,
                **kwargs
                ) 
            
    @staticmethod
    def _extract_distribution(
        paramName: str, **kwargs
        ) -> Common.Distributions.IDistribution:
        dist = kwargs.get(paramName)
        if isinstance(dist, numbers.Number):
            dist = pymdt.distributions.MakeFixed(float(dist))
        if isinstance(dist, MDT.CustomDistributionBase):
            allowed = kwargs.get("allow_custom_distributions", True)
            if not allowed:
                raise RuntimeError(
                    "Custom distributions cannot be used in this context." +
                    " This is typically thrown when building specifications."
                    )
            dist = MDT.CustomDistributionWrapper(dist)
        return dist

    @staticmethod
    def _extract_impedance(impedes, **kwargs):
        imp = kwargs.get("impedance")
        if imp is not None:
            resist = imp[0]
            react = imp[1]
        else:
            resist = kwargs.get("resistance", 0.0)
            react = kwargs.get("reactance", 0.0)
            
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            impedes, "Impedance", System.Numerics.Complex(resist, react),
            **kwargs
            )

    @staticmethod
    def _extract_voltage(volt_node, **kwargs):
        rv = kwargs.get("voltage")
        if rv is not None:
            real = rv[0]
            imag = rv[1]
        else:
            real = kwargs.get("real", 0.0)
            imag = kwargs.get("imaginary", 0.0)
            
        details._execute_loggable_property_set_with_undo(
            volt_node, "Voltage", System.Numerics.Complex(real, imag),
            **kwargs
            )
        
    @staticmethod
    def _extract_color(**kwargs) -> System.Drawing.Color:
        if "color" not in kwargs: return System.Drawing.Color.Empty
        c = kwargs["color"]
        if type(c) is str:
            c = System.Drawing.Color.FromName(c)
        return c
        
    @staticmethod
    def _extract_font(**kwargs) -> System.Drawing.Font:
        return kwargs.get("font", System.Drawing.SystemFonts.DefaultFont)
        
    @staticmethod
    def _extract_text_alignment(**kwargs) -> MDT.NodeGroup.TextAlignEnum:
        return kwargs.get("text_alignment", text_alignment.top_left).value
        
def FindEntityByName(all_ents, name: str, **kwargs):
    """ Searches through a collection to find an item with the given name.
    
    In the case of the MDT interface, the name is indicated by the value of
    the StringID property of an entry in all_ents.
    
    Parameters
    ----------
    all_ents:
        Something that can be iterated to search for an item with the supplied
        name.  Then entities in this list must have a property named StringID
        that is used as the name getter.
    name: str
        The name to search for.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        find_context:
            A descriptor of the find operation that is happening, typically a
            description of the list being searched.  This is used if no matching
            item is found to give a more meaningful error message.  If not
            supplied, the context is an empty string.
        case_sensitive:
            An indicator of whether the search should be case sensitive or not.
            if not provided, the default is True for a case sensitive search.
        find_fail_behavior: find_fail_behavior
            A member of the find_fail_behavior enumeration indicating what to do
            if the search is unsuccessful.  The default is to ignore and return
            None.  Optionally, if this argument is find_fail_behavior.throw, an
            exception is thrown with a message meant to give information about
            the failed search.
            
    Returns
    -------
    Found Item:
        The item that was found or None if no matching item is found.
    """
    fb = kwargs.get("find_fail_behavior", find_fail_behavior.ignore)
    context = kwargs.get("find_context", "")
    casesen = kwargs.get("case_sensitive", True)
    if casesen:
        ret = next((s for s in all_ents if (s.StringID == name)), None)
    else:
        ret = next(
            (s for s in all_ents if (s.StringID.casefold() == name.casefold())),
            None
            )
    if ret is None and fb == find_fail_behavior.throw:
        msg = "Unable to find entity with name " + name
        if context: msg += " in " + str(context)
        raise Exception(msg)
    return ret

def MakeUsableName(all_ents, name: str, **kwargs) -> str:
    """ Creates a usable name from the supplied name that does not duplicate any
    names in the collection all_ents by adding digits to the end.
    
    In the case of the MDT interface, the name is indicated by the value of
    the StringID property of an entry in all_ents.
    
    Parameters
    ----------
    all_ents:
        Something that can be iterated to search for an item with the supplied
        name.  Then entities in this list must have a property named StringID
        that is used as the name getter.
    name: str
        The name to search for.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        start: int
            The lowest usable digit to append in the case of the need to append
            them to get a unique name.
            
    Returns
    -------
    str:
        The name that is unique to the supplied collection which may be the
        supplied name if it was already unique.
    """
    strt = kwargs.get("start", 1)
    done = False
    base = name
    while not done:
        done = True
        for ent in all_ents:
            if ent.StringID == name:
                done = False
                name = base + str(strt)
                strt += 1

    return name

def ExecutePropertySet(
    obj, propName, value, custom_cancel_evt_name=None, **kwargs
    ) -> Common.Logging.Log:
    """ A helper function for setting properties on MDT (or associated library)
    class objects.  This helps with management of messages that may occur when
    setting a property that should be processed (error messages for example).
    
    Parameters
    ----------
    obj:
        The object on which a property set should occur.
    propName: str
        The name of the property to set.
    value:
        The value to assign to the property (as in obj.propName = value).
    custom_cancel_evt_name: str
        The name of a function that should be called if the property set is
        rejected by the library.  If not provided, the default handler is used
        which will push the cancellation message into a log (either a provided
        one or the GlobalErrorLog).
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        err_log: Common.Logging.Log
            A Log object into which to capture any messages generated during
            this operation.  If not provided, messages will be added into
            the pymdt.GlobalErrorLog.
    """
    return details._execute_loggable_property_set_with_undo(
        obj, propName, value, custom_cancel_evt_name, **kwargs
        )

def PrintLog(log: Common.Logging.Log, writeTags: bool=False, maxEntries: int=-1):
    """ A simple helper function to print out the contents of a Log.
    
    Parameters
    ----------
    log: Common.Logging.Log
        The log to print using the print() function.
    writeTags: bool
        True if the tags (like E0001, W0032, etc.) should be written along with
        each entry in the log.
    maxEntries: int
        The maximum number of log entries to write.  if this value is -1 (the
        default), than all log entries are written.
    """
    print(log.ToString(writeTags, maxEntries))