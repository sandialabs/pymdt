import MDT
import TMO
import Common
import System

import pymdt
import pymdt.utils

class details:
    
    _site_list_extractors = {
        MDT.Microgrid: lambda mg: mg.Microgrids,
        MDT.SolarResource: lambda mg: mg.SolarResources,
        MDT.WindResource: lambda mg: mg.WindResources,
        MDT.HydroResource: lambda mg: mg.HydroResources,
        MDT.Mission: lambda mg: mg.Missions,
        MDT.MissionFunction: lambda mg: mg.MissionFunctions,
        MDT.SiteNodeGroup: lambda mg: mg.NodeGroups
        }
    
    _mg_list_extractors = {
        MDT.Line: lambda mg: mg.get_Lines(False),
        MDT.Bus: lambda mg: mg.get_Busses(False),
        MDT.Node: lambda mg: mg.get_Nodes(False),
        MDT.Switch: lambda mg: mg.get_Switches(False),
        MDT.DieselTank: lambda mg: mg.get_DieselTanks(False),
        MDT.PropaneTank: lambda mg: mg.get_PropaneTanks(False),
        MDT.ThermalLoad: lambda mg: mg.get_ThermalLoads(False),
        MDT.Transformer: lambda mg: mg.get_Transformers(False),
        MDT.MicrogridNodeGroup: lambda mg: mg.NodeGroups,
        MDT.MicrogridNecessitationDependency: lambda mg: mg.NecessitationDependencies,
        MDT.MicrogridDesignOption: lambda mg: mg.DesignOptions
        }
    
    _bus_list_extractors = {
        MDT.ILoadSection: (lambda b: b.LoadSections),
        MDT.DieselGenerator: (lambda b: b.DieselGenerators),
        MDT.NaturalGasGenerator: (lambda b: b.NaturalGasGenerators),
        MDT.PropaneGenerator: (lambda b: b.PropaneGenerators),
        MDT.WindGenerator: (lambda b: b.WindGenerators),
        MDT.HydroGenerator: (lambda b: b.HydroGenerators),
        MDT.SolarGenerator: (lambda b: b.SolarGenerators),
        MDT.Battery: (lambda b: b.Batteries),
        MDT.Inverter: (lambda b: b.Inverters),
        MDT.UninterruptiblePowerSupply: (lambda b: b.UninterruptiblePowerSupplies)
        }
    
    @staticmethod
    def extract_site(asset: MDT.Site, within) -> MDT.Site:        
        if isinstance(within, MDT.Site):
            return within if within.StringID == asset.StringID else None
    
        if isinstance(within, MDT.SiteUpgradeConfiguration):
            return details.extract_site_from_config(asset, within.MainSite)
    
        if isinstance(within, TMO.SolverRunInfo):
            return details.extract_site_from_run_info(
                asset, within.SystemOfSystems
                )
    
        return None
        
    @staticmethod
    def extract_site_from_run_info(asset: MDT.Site, inSRI: TMO.SolverRunInfo) -> MDT.Site:
        osite = inSRI.SystemOfSystems
        return details.extract_site(asset, osite)
        
    @staticmethod
    def extract_site_from_config(asset: MDT.Site, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.Site:
        osite = inConfig.MainSite
        return details.extract_site(asset, osite)
        
    @staticmethod
    def extract_site_entity(asset: MDT.ISiteEntity, inSite: MDT.Site) -> MDT.ISiteEntity:
        if inSite is None: return None
        getter = details._site_list_extractors[type(asset)]
        return pymdt.utils.FindEntityByName(getter(inSite), asset.StringID)
    
    @staticmethod
    def extract_site_entity_from_site(asset: MDT.ISiteEntity, inSite: MDT.Site) -> MDT.ISiteEntity:
        osite = details.extract_site(asset.Site, inSite)
        return details.extract_site_entity(asset, osite)
    
    @staticmethod
    def extract_site_entity_from_run_info(asset: MDT.ISiteEntity, inSRI: TMO.SolverRunInfo) -> MDT.ISiteEntity:
        osite = details.extract_site_from_run_info(asset.Site, inSRI)
        return details.extract_site_entity(asset, osite)
    
    @staticmethod
    def extract_site_entity_from_config(asset: MDT.ISiteEntity, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.ISiteEntity:
        osite = details.extract_site_from_config(asset.Site, inConfig)
        return details.extract_site_entity(asset, osite)
    
    @staticmethod
    def extract_microgrid_entity(asset: MDT.IMicrogridEntity, inMG: MDT.Microgrid) -> MDT.IMicrogridEntity:
        if inMG is None: return None
        getter = details._mg_list_extractors[type(asset)]
        return pymdt.utils.FindEntityByName(getter(inMG), asset.StringID)
    
    @staticmethod
    def extract_microgrid_entity_from_site(asset: MDT.IMicrogridEntity, inSite: MDT.Site) -> MDT.IMicrogridEntity:
        omg = details.extract_site_entity_from_site(asset.Microgrid, inSite)
        return details.extract_microgrid_entity(asset, omg)
    
    @staticmethod
    def extract_microgrid_entity_from_run_info(asset: MDT.IMicrogridEntity, inSRI: TMO.SolverRunInfo) -> MDT.IMicrogridEntity:
        omg = details.extract_site_entity_from_run_info(asset.Microgrid, inSRI)
        return details.extract_microgrid_entity(asset, omg)
    
    @staticmethod
    def extract_microgrid_entity_from_config(asset: MDT.IMicrogridEntity, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.IMicrogridEntity:
        omg = details.extract_site_entity_from_config(asset.Microgrid, inConfig)
        return details.extract_microgrid_entity(asset, omg)

    @staticmethod
    def extract_bus_entity(asset: MDT.IBusEntity, inBus: MDT.Bus) -> MDT.IBusEntity:
        if inBus is None: return None
        getter = details._bus_list_extractors[type(asset)]
        return pymdt.utils.FindEntityByName(getter(inBus), asset.StringID)
    
    @staticmethod
    def extract_bus_entity_from_site(asset: MDT.IBusEntity, inSite: MDT.Site) -> MDT.IBusEntity:
        obus = details.extract_microgrid_entity_from_site(asset.Bus, inSite)
        return details.extract_bus_entity(asset, obus)
    
    @staticmethod
    def extract_bus_entity_from_run_info(asset: MDT.IBusEntity, inSRI: TMO.SolverRunInfo) -> MDT.IBusEntity:
        obus = details.extract_microgrid_entity_from_run_info(asset.Bus, inSRI)
        return details.extract_bus_entity(asset, obus)
    
    @staticmethod
    def extract_bus_entity_from_config(asset: MDT.IBusEntity, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.IBusEntity:
        obus = details.extract_microgrid_entity_from_config(asset.Bus, inConfig)
        return details.extract_bus_entity(asset, obus)
    
    @staticmethod
    def extract_variable_selections(respSet) -> {}:
        upgs = respSet.Upgrades
        ret = {}
        for kvp in upgs:
            tecOpt = kvp.Key
            entity = None
        
            if isinstance(tecOpt, MDT.MicrogridDesignOptionOption):
                entity = tecOpt.DesignOption
            else:
                entity = tecOpt.Entity
            
            rdMap = kvp.Value
            subOpt = rdMap[0].Value

            if isinstance(subOpt, MDT.MicrogridDesignOptionRealizationSuboption):
                ret[entity] = subOpt.Realization
            else:
                ret[entity] = subOpt.Specification
        
        return ret
    
def GetResultManagers() -> Common.Databinding.IKeyedCollectionWithUndo[System.Guid, MDT.ResultViewManager]:
    return MDT.Driver.INSTANCE.ResultViewManagers

def MakeResultManager(sri) -> MDT.ResultViewManager:
    rvm = MDT.ResultViewManager()
    if not pymdt.utils.details._is_collection(sri): sri = [sri]
    for r in sri: rvm.get_SolverRunInfos().Add(r)
    return rvm


def GetMicrogridRealization(mg: MDT.Microgrid, config: MDT.SiteUpgradeConfiguration) -> MDT.MicrogridRealization:
    """ Extracts and returns the MDT.MicrogridRealization for the specified
    Microgrid (mg) from the specified upgrade configuration.
        
    The supplied microgrid must be one extracted from a result set as opposed 
    to one created as part of an input set.  See the
    FindCorrespondingMicrogridFromRunInfo or similar function in this module for
    more information.

    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which the realization is sought.
    config: MDT.SiteUpgradeConfiguration
        The site configuration from which to attempt to extract a realization
        for the supplied Microgrid.
        
    Returns
    -------
    MDT.MicrogridRealization:
        The found realization if one.  None otherwise.
    """
    return config.RealizedSite.get_MicrogridRealization(mg)

def GetResponseFunctionGroups(sri: TMO.SolverRunInfo) -> Common.Databinding.IKeyedCollectionWithUndo[System.Guid, TMO.ResponseFunctionGroup]:
    """ Extracts and returns the collection of TMO.ResponseFunctionGroup objects
    used in the creation of the results in sri.

    Parameters
    ----------
    sri: TMO.SolverRunInfo
        The solver run information object that contains results.  These results
        were generated for a set of response function groups.  Those groups
        are extracted from this object.
        
    Returns
    -------
    Common.Databinding.IKeyedCollectionWithUndo[System.Guid, TMO.ResponseFunctionGroup]:
        The collection of response function groups found.  None otherwise.
    """
    if sri is None: return None
    solver = sri.Solver
    if solver is None: return None
    return solver.ResponseFunctionGroups

def GetVariableSelections(config: MDT.SiteUpgradeConfiguration):
    
    ret = details.extract_variable_selections(config)
        
    for kvp in config.ModelUpgradeConfigs:
        ret |= details.extract_variable_selections(kvp.Value)

    return ret    

def GetFinalSolutionSet(sri: TMO.SolverRunInfo) -> TMO.IterationData:
    """    
    One can use the .Configurations property of the returned IterationData
    object to access an iterable collection of the actual
    SiteUpgradeConfiguration objects.
    """
    if sri.AllData.Count == 0: return None
    index = sri.AllData.Count - 1
    ids = sri.AllData.AllData[index]
    if ids.Count == 0: return None
    index = ids.Count - 1
    return ids[index]


def FindCorrespondingSiteFromSite(s: MDT.Site, inSite: MDT.Site) -> MDT.Microgrid:
    return details.extract_site(s, inSite)

def FindCorrespondingMicrogridFromSite(mg: MDT.Microgrid, inSite: MDT.Site) -> MDT.Microgrid:
    return details.extract_site_entity(mg, inSite)

def FindCorrespondingBusFromSite(b: MDT.Bus, inSite: MDT.Site) -> MDT.Bus:
    return details.extract_microgrid_entity_from_site(b, inSite)

def FindCorrespondingAssetFromSite(asset, inSite: MDT.Site):
    if isinstance(asset, MDT.Site):
        return details.extract_site(asset, inSite)
    
    if isinstance(asset, MDT.IBusEntity):
        return details.extract_bus_entity_from_site(asset, inSite)
    
    if isinstance(asset, MDT.IMicrogridEntity):
        return details.extract_microgrid_entity_from_site(asset, inSite)
    
    if isinstance(asset, MDT.ISiteEntity):
        return details.extract_site_entity_from_site(asset, inSite)
    
    return None


def FindCorrespondingSiteFromRunInfo(s: MDT.Site, inSRI: TMO.SolverRunInfo) -> MDT.Site:
    return details.extract_site_from_run_info(s, inSRI)

def FindCorrespondingMicrogridFromRunInfo(mg: MDT.Microgrid, inSRI: TMO.SolverRunInfo) -> MDT.Microgrid:
    return details.extract_site_entity_from_run_info(mg, inSRI)

def FindCorrespondingBusFromRunInfo(b: MDT.Bus, inSRI: TMO.SolverRunInfo) -> MDT.Bus:
    return details.extract_microgrid_entity_from_run_info(b, inSRI)

def FindCorrespondingAssetFromRunInfo(asset, inSRI: TMO.SolverRunInfo):
    if isinstance(asset, MDT.Site):
        return FindCorrespondingSiteFromRunInfo(asset, inSRI)
    
    if isinstance(asset, MDT.IBusEntity):
        return details.extract_bus_entity_from_run_info(asset, inSRI)
    
    if isinstance(asset, MDT.IMicrogridEntity):
        return details.extract_microgrid_entity_from_run_info(asset, inSRI)
    
    if isinstance(asset, MDT.ISiteEntity):
        return details.extract_site_entity_from_run_info(asset, inSRI)
    
    return None


def FindCorrespondingSiteFromConfig(s: MDT.Site, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.Site:
    return details.extract_site_from_config(s, inConfig)

def FindCorrespondingMicrogridFromConfig(mg: MDT.Microgrid, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.Microgrid:
    return details.extract_site_entity_from_config(mg, inConfig)

def FindCorrespondingBusFromConfig(b: MDT.Bus, inConfig: MDT.SiteUpgradeConfiguration) -> MDT.Bus:
    return details.extract_microgrid_entity_from_config(b, inConfig)

def FindCorrespondingAssetFromConfig(asset, inConfig: MDT.SiteUpgradeConfiguration):
    if isinstance(asset, MDT.Site):
        return FindCorrespondingSiteFromConfig(asset, inConfig)
    
    if isinstance(asset, MDT.IBusEntity):
        return details.extract_bus_entity_from_config(asset, inConfig)
    
    if isinstance(asset, MDT.IMicrogridEntity):
        return details.extract_microgrid_entity_from_config(asset, inConfig)
    
    if isinstance(asset, MDT.ISiteEntity):
        return details.extract_site_entity_from_config(asset, inConfig)
    
    return None


def FindCorrespondingSite(s: MDT.Site, within) -> MDT.Site:
    if isinstance(within, MDT.Site):
        return FindCorrespondingSiteFromSite(s, within)
    
    if isinstance(within, MDT.SiteUpgradeConfiguration):
        return FindCorrespondingSiteFromConfig(s, within)
    
    if isinstance(within, TMO.SolverRunInfo):
        return FindCorrespondingSiteFromRunInfo(s, within)
    
    return None

def FindCorrespondingMicrogrid(mg: MDT.Microgrid, within) -> MDT.Microgrid:
    if isinstance(within, MDT.Site):
        return FindCorrespondingMicrogridFromSite(mg, within)
    
    if isinstance(within, MDT.SiteUpgradeConfiguration):
        return FindCorrespondingMicrogridFromConfig(mg, within)
    
    if isinstance(within, TMO.SolverRunInfo):
        return FindCorrespondingMicrogridFromRunInfo(mg, within)
    
    return None

def FindCorrespondingBus(b: MDT.Bus, within) -> MDT.Bus:
    if isinstance(within, MDT.Site):
        return FindCorrespondingBusFromSite(b, within)
    
    if isinstance(within, MDT.SiteUpgradeConfiguration):
        return FindCorrespondingBusFromConfig(b, within)
    
    if isinstance(within, TMO.SolverRunInfo):
        return FindCorrespondingBusFromRunInfo(b, within)
    
    return None

def FindCorrespondingAsset(asset, within):
    if isinstance(asset, MDT.Site):
        return details.extract_site(asset, within)
    
    if isinstance(within, MDT.Site):
        return FindCorrespondingAssetFromSite(asset, within)
    
    if isinstance(within, MDT.SiteUpgradeConfiguration):
        return FindCorrespondingAssetFromConfig(asset, within)
    
    if isinstance(within, TMO.SolverRunInfo):
        return FindCorrespondingAssetFromRunInfo(asset, within)
    
    return None