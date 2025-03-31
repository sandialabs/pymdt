import numbers

import MDT
import System
import Common

from enum import Enum

import pymdt.distributions

class time_units(Enum):
    milliseconds = Common.Time.TimeAccumulation.Units.Milliseconds
    seconds = Common.Time.TimeAccumulation.Units.Seconds
    minutes = Common.Time.TimeAccumulation.Units.Minutes
    hours = Common.Time.TimeAccumulation.Units.Hours
    days = Common.Time.TimeAccumulation.Units.Days
    weeks = Common.Time.TimeAccumulation.Units.Weeks
    months = Common.Time.TimeAccumulation.Units.Months
    years = Common.Time.TimeAccumulation.Units.Years

class find_fail_behavior(Enum):
    ignore = 0
    throw = 1

class text_alignment(Enum):
    top_left = MDT.NodeGroup.TextAlignEnum.TopLeft
    top_center = MDT.NodeGroup.TextAlignEnum.TopCenter
    top_right = MDT.NodeGroup.TextAlignEnum.TopRight
    middle_left = MDT.NodeGroup.TextAlignEnum.MiddleLeft
    middle_center = MDT.NodeGroup.TextAlignEnum.MiddleCenter
    middle_right = MDT.NodeGroup.TextAlignEnum.MiddleRight
    bottom_left = MDT.NodeGroup.TextAlignEnum.BottomLeft
    bottom_center = MDT.NodeGroup.TextAlignEnum.BottomCenter
    bottom_right = MDT.NodeGroup.TextAlignEnum.BottomRight
  
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
    def _extract_failure_distributions(fm: MDT.FailureMode, **kwargs):
        details._execute_loggable_property_set_with_undo(
            fm, "MTBF", details._extract_distribution("mtbf", **kwargs),
            **kwargs
            )
        
        details._execute_loggable_property_set_with_undo(
            fm, "MTTR", details._extract_distribution("mttr", **kwargs),
            **kwargs
            )
            
    @staticmethod    
    def _extract_failure_modes(unrel, **kwargs):
        fms = kwargs.get("failure_modes")
        if fms is None: return
        if not details._is_collection(fms): fms = [fms]
        for fm in fms:
            pymdt.utils.details._execute_1_arg_add_with_undo(
                unrel, "AddFailureModeCanceled", "get_FailureModes", fm,
                **kwargs
                ) 
            
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
        
    @staticmethod
    def build_failure_mode(name: str, **kwargs) -> MDT.FailureMode:
        fm = MDT.FailureMode(name)
        details._extract_guid(fm, **kwargs)
        details._extract_failure_distributions(fm, **kwargs)
        details._extract_notes(fm, **kwargs)
        return fm
 
    @staticmethod
    def build_fragility_curve(name: str, **kwargs) -> MDT.FragilityCurve:
        fc = MDT.FragilityCurve(name)
        details._extract_guid(fc, **kwargs)
        details._execute_loggable_property_set_with_undo(
            fc, "MTTR", details._extract_distribution("mttr", **kwargs),
            **kwargs
            )
        details._execute_loggable_property_set_with_undo(
            fc, "ProbabilityGenerator", 
            details._extract_distribution("probability_generator", **kwargs),
            **kwargs
            )
        details._extract_notes(fc, **kwargs)
        return fc
 
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
        
        Properties
        ----------
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
        
        Properties
        ----------
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

def MakeFailureMode(u: MDT.IUnreliable, name: str, **kwargs) -> MDT.FailureMode:
    """ This helper function creates a new failure mode, extracts any
        provided properties, loads it into its owner (u), and returns it.
        
    Parameters
    ----------
    u: MDT.IUnreliable
        The unreliable entity for which this failure mode is being built.  This
        argument can be None and if no owner is provided or the owner provided
        is None, then the returned mode will not be added to any owner.  It
        should thus be added to an owner at some later time.
    name: str
        The name to be given to the new failure mode.  Names of failure modes
        within an unreliable entity must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        Properties
        ----------
        mtbf: Common.Distributions.IDistribution
            The probability distribution describing the mean time between
            failures for this failure mode.  This could also be a float in which
            case a fixed distribution will be used.
        mttr: Common.Distributions.IDistribution
            The probability distribution describing the mean time to repair for
            this failure mode.  This could also be a float in which case a fixed
            distribution will be used.
        owner:
            An optional parameter to serve as the owner of the new failure mode.
            This is typically used if one does not want the failure mode added
            to the unreliable asset as part of this call in which case None is
            specified as the owner.  If no owner is provided, then the supplied
            unreliable (u) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes:
            Any notes to assign to the resulting failure mode.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
            
    Returns
    -------
    MDT.FailureMode:
        The newly created and loaded failure mode.
    """
    fm = details.build_failure_mode(name, **kwargs)
    owner = pymdt.core.details._extract_owner(u, **kwargs)
    if owner is not None:
        details._execute_1_arg_add_with_undo(
            owner, "AddFailureModeCanceled", "get_FailureModes", fm, **kwargs
            )
    return fm
    
def MakeFragilityCurve(
    f: MDT.IFragile, name: str, haz: MDT.Hazard, **kwargs
    ) -> MDT.FragilityCurve:
    """ This helper function creates a new fragility curve, extracts any
        provided properties, loads it into its owner (f) mapped to the supplied
        hazard, and returns it.
        
    Parameters
    ----------
    f: MDT.IFragile
        The fragile entity for which this fragility curve is being built. This
        parameter can be None and if so, and if no explicit non-None owner is
        provided, the fragility curve will be built and returned but no mapping
        to haz will take place.  At some later time, the newly created fragility
        curve should be added to an asset mapped to a hazard.
    name: str
        The name to be given to the new fragility curve.  Names of fragility
        curves within an unreliable entity must be unique.
    haz: MDT.Hazard
        The hazard to which this fragility curve applies in the given fragile
        entity.  If the parameter f is None, or if an explicit owner=None is
        provided, this parameter can also be None. Otherwise, it cannot.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        Properties
        ----------
        mttr: Common.Distributions.IDistribution
            The probability distribution describing the mean time to repair for
            this fragility curve.  This could also be a float in which case a
            fixed distribution will be used.
        probability_generator: Common.Distributions.IDistribution
            The distribution that determines the likelihood of failure in terms
            of the hazard intensity units for this fragility.
        owner:
            An optional parameter to serve as the owner of the new fragility
            curve. This is typically used if one does not want the fragility
            curve added to the fragile asset as part of this call in which case
            None is specified as the owner.  If no owner is provided, then the
            supplied fragile asset (f) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes:
            Any notes to assign to the resulting fragility curve.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
            
    Returns
    -------
    MDT.FragilityCurve:
        The newly created and loaded fragility curve.
    """
    fc = details.build_fragility_curve(name, **kwargs)
    owner = pymdt.core.details._extract_owner(f, **kwargs)
    if owner is not None:
        details._execute_2_arg_add_with_undo(
            owner, "AddFragilityCurveCanceled", "get_FragilityCurves", haz, fc,
            **kwargs
            )
    return fc

def ExecutePropertySet(
    obj, propName, value, custom_cancel_evt_name=None, **kwargs
    ) -> Common.Logging.Log:

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