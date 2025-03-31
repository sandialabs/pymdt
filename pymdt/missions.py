import MDT
import TMO

import pymdt.utils
import pymdt.specs

class details:
    
    @staticmethod
    def build_mission_function(s: MDT.Site, name: str, **kwargs) -> MDT.MissionFunction:
        ret = MDT.MissionFunction(s, name)
        pymdt.utils.details._extract_guid(ret, **kwargs)
        pymdt.utils.details._extract_notes(ret, **kwargs)
        return ret
    
    @staticmethod
    def build_mission(s: MDT.Site, name: str, **kwargs) -> MDT.Mission:
        ret = MDT.Mission(s, name)
        pymdt.utils.details._extract_guid(ret, **kwargs)
        pymdt.utils.details._extract_notes(ret, **kwargs)
        return ret
    
    @staticmethod
    def _load_and_assign_node(node, parent, children, **kwargs):        
        pymdt.utils.details._execute_loggable_action(
            parent, "AddChildCanceled", lambda: parent.AddChild(node), **kwargs
            )

        for child in children:
            pymdt.utils.details._execute_loggable_action(
                node, "AddChildCanceled", lambda: node.AddChild(child), **kwargs
                )
        return node

    @staticmethod
    def _resolve_node_parent(parent):
        if type(parent) is MDT.Mission:
            return parent.MissionFunctions
        elif type(parent) is MDT.MissionFunction:
            return parent.TopNode
        return parent
        
def MakeMission(s: MDT.Site, name: str, **kwargs) -> MDT.Mission:
    """ This helper function creates a new mission, extracts any provided
        properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this mission is being built.
    name: str
        The name to be given to this mission.  Names of missions within a site
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        Properties
        ----------
        owner:
            An optional parameter to serve as the owner of the new mission.
            This is typically used if one does not want the mission added to the
            site as part of this call in which case None is specified as the
            owner.  If no owner is provided, then the supplied site (s) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes:
            Any notes to assign to the resulting mission.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Mission:
        The newly created mission instance.
    """
    m = details.build_mission(s, name, **kwargs)
    owner = pymdt.core.details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddMissionCanceled", "get_Missions", m, **kwargs
            )
    return m

def MakeMissionFunction(s: MDT.Site, name: str, **kwargs) -> MDT.MissionFunction:
    """ This helper function creates a new mission function, extracts any
        provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this mission function is being built.
    name: str
        The name to be given to this mission function.  Names of mission
        functions within a site must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        Properties
        ----------
        owner:
            An optional parameter to serve as the owner of the new mission
            function. This is typically used if one does not want the mission
            function added to the site as part of this call in which case None
            is specified as the owner.  If no owner is provided, then the
            supplied site (s) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes:
            Any notes to assign to the resulting mission function.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.MissionFunction:
        The newly created mission function instance.
    """
    mf = details.build_mission_function(s, name, **kwargs)
    owner = pymdt.core.details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddMissionFunctionCanceled", "get_MissionFunctions", mf,
            **kwargs
            )
    return mf

def MakeOrNode(parent, children, **kwargs) -> TMO.OrNode:
    """ This helper function creates a new or node, extracts any provided
        properties, loads it into its parent, and returns it.
        
    Parameters
    ----------
    parent
        The parent node of the new or node being created.  This can be a mission
        function or another node such as an and, or, or M of N node.
    children
        The nodes to include as children in this new or node.  This can be an
        empty collection if desired as children can be added subsequently.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        This function does not use any keyword arguments.
        
    Returns
    -------
    TMO.OrNode:
        The newly created or node instance.
    """
    parent = details._resolve_node_parent(parent)
    return details._load_and_assign_node(
        TMO.OrNode(parent), parent, children, **kwargs
        )

def MakeAndNode(parent, children, **kwargs) -> TMO.AndNode:
    """ This helper function creates a new and node, extracts any provided
        properties, loads it into its parent, and returns it.
        
    Parameters
    ----------
    parent
        The parent node of the new and node being created.  This can be a
        mission function or another node such as an and, or, or M of N node.
    children
        The nodes to include as children in this new and node.  This can be an
        empty collection if desired as children can be added subsequently.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        This function does not use any keyword arguments.
        
    Returns
    -------
    TMO.AndNode:
        The newly created and node instance.
    """
    parent = details._resolve_node_parent(parent)
    return details._load_and_assign_node(
        TMO.AndNode(parent), parent, children, **kwargs
        )

def MakeMofNNode(parent, children, m: int, **kwargs) -> TMO.MofNNode:
    """ This helper function creates a new M of N node, extracts any provided
        properties, loads it into its parent, and returns it.
        
    Parameters
    ----------
    parent
        The parent node of the new M of N node being created.  This can be a
        mission function or another node such as an and, or, or M of N node.
    children
        The nodes to include as children in this new M of N node.  This can be
        an empty collection if desired as children can be added subsequently.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        This function does not use any keyword arguments.
        
    Returns
    -------
    TMO.MofNNode:
        The newly created M of N node instance.
    """
    parent = details._resolve_node_parent(parent)        
    ret = details._load_and_assign_node(
        TMO.MofNNode(parent), parent, children, **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        ret, "M", m, **kwargs
        )
    return ret

def MakeNotNode(parent, child, **kwargs) -> TMO.NotNode:
    """ This helper function creates a new not node, extracts any
        provided properties, loads it into its parent, and returns it.
        
    Parameters
    ----------
    parent
        The parent node of the new not node being created.  This can be a
        mission function or another node such as an and, or, or M of N node.
    child
        The node to include as the children in this new not node.  This can be
        none if desired as the child can be added subsequently.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        This function does not use any keyword arguments.
        
    Returns
    -------
    TMO.NotNode:
        The newly created not node instance.
    """
    parent = details._resolve_node_parent(parent)
    return details._load_and_assign_node(
        TMO.NotNode(parent), parent, [child], **kwargs
        )