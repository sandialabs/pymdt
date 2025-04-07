import os
import glob
import subprocess
import pymdt.utils
import pymdt.specs

from enum import Enum

import System
from System import Exception as SYSEX

import MDT
import Common

class controller_types(Enum):
    """ An enumeration of the types of microgrid controller available for
    selection.
    """
    
    Standard = MDT.MicrogridControllerSettings.ControllerTypeEnum.Standard    
    """ The Standard controller uses batteries as an energy source of last
    resort.
    """
    
    CycleCharging = MDT.MicrogridControllerSettings.ControllerTypeEnum.BatteryUser
    """ The CycleCharging controller uses batteries aggressively in an attempt
    to shave peaks and minimize diesel fuel usage.
    """
    
class powerflow_types(Enum):
    """ An enumeration of the possible powerflow calculations supported by
    the MDT.
    """

    NONE = getattr(MDT.PRMSettings.PowerflowTypeEnum, "None")
    """ Indicates that no powerflow calculations should be conducted.
    """
    
    DC = MDT.PRMSettings.PowerflowTypeEnum.DC
    """ Indicates that DC powerflow calculations should be conducted.
    """

class details:
    
    StoredLoadProfiles = []
    StoredSolarProfiles = []
    StoredWindProfiles = []
    StoredHydroProfiles = []
    StoredThermalProfiles = []
        
    @staticmethod
    def _load_all_stored_configs(pth, list, ext="*.msrd"):
        for fname in glob.iglob(os.path.join(pth, ext)):
            list.append(MDT.StoredTierLoadConfiguration(fname))

    @staticmethod
    def _set_node_location(node, location: tuple[float,float], **kwargs):
        if location is None: return
        x, y = location
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            node, "Location", System.Drawing.PointF(x, y), **kwargs
            )
    
    @staticmethod
    def _resolve_spec(specObj, allSpecs, **kwargs):
        return pymdt.utils.FindEntityByName(allSpecs, specObj, **kwargs) \
            if (type(specObj) is str) else specObj
    
    @staticmethod
    def _resolve_all_specs(specList, allSpecs, **kwargs):
        return [details._resolve_spec(specObj, allSpecs, **kwargs) \
            for specObj in specList]

    @staticmethod    
    def _extract_fragilities(fragile, **kwargs):
        fcs = kwargs.get("fragilities")
        if fcs is None: return
        # The object obtained must be either a tuple or a dictionary.  If a
        # tuple, then it must be (Hazard, FragilityCurve)
        if type(fcs) is tuple: fcs = {fcs[0]: fcs[1]}
        for key, value in fcs.items():
            pymdt.utils.details._execute_2_arg_add_with_undo(
                fragile, "AddFragilityCurveCanceled", "get_FragilityCurves",
                key, value, **kwargs
                )
            
    @staticmethod
    def _extract_specifications(node, all_specs, **kwargs):
        if "base_spec" in kwargs:
            bSpec = details._resolve_spec(
                kwargs["base_spec"], all_specs, **kwargs
                )
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                node, "BaselineSpecification", bSpec, **kwargs
                )

        if "specs" in kwargs:
            specentry = kwargs["specs"]
            if not pymdt.utils.details._is_collection(specentry):
                specentry = [specentry]
            specs = details._resolve_all_specs(specentry, all_specs, **kwargs)
            for spec in specs:
                pymdt.utils.details._execute_1_arg_add_with_undo(
                    node, "AddSpecificationCanceled", "get_Specifications",
                    spec, **kwargs
                    )
        
    @staticmethod
    def _extract_node_location(node, **kwargs):
        if "loc" in kwargs:
            details._set_node_location(node, kwargs["loc"], **kwargs)
            
    @staticmethod
    def _extract_retrofit_cost(component, **kwargs):
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            component, "RetrofitCost",
            System.Decimal(kwargs.get("retrofit_cost", 0.0)), **kwargs
            )
            
    @staticmethod
    def _extract_tank(tank, all_tanks, **kwargs):
        if type(tank) is str:
            tank = pymdt.utils.FindEntityByName(all_tanks, tank, **kwargs)
        return tank
        
    @staticmethod
    def _extract_fuel_tanks(gen, all_tanks, **kwargs):
        if "tanks" not in kwargs: return
        tanks = kwargs["tanks"]
        if not pymdt.utils.details._is_collection(tanks): tanks = [tanks]
        for t in tanks:
            pymdt.utils.details._execute_1_arg_add_with_undo(
                gen, "AddTankCanceled", "get_Tanks",
                details._extract_tank(t, all_tanks, **kwargs), **kwargs
                )
        
    @staticmethod
    def _extract_resource(all_recs, **kwargs):
        rec = kwargs.get("resource")
        if rec is None: return None
        return pymdt.utils.FindEntityByName(all_recs, rec, **kwargs) \
            if (type(rec) is str) else rec
    
    @staticmethod
    def _extract_period_and_interval(rpd: MDT.IRegularPeriodData, **kwargs):
        # allow for the provision of some but not all values.  If all are found,
        # use SetPeriodAndInterval
        interval = kwargs.get("interval", 1)
        int_units = kwargs.get("interval_units", pymdt.utils.time_units.days)
        period = kwargs.get("period", 1)
        per_units = kwargs.get("period_units", pymdt.utils.time_units.hours)
        
        if hasattr(int_units, "value"): int_units = int_units.value
        if hasattr(per_units, "value"): per_units = per_units.value
            
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()

        rpd.SetPeriodAndInterval(
            period, per_units, interval, int_units, undos
            )
        
    @staticmethod
    def _extract_tier(ldwt, **kwargs) -> MDT.LoadTier:
        t = kwargs.get("tier")
        if t is None: return None
        if type(t) is str:
            t = pymdt.utils.FindEntityByName(
                pymdt.DriverProxy.LoadTiers, t,
                find_fail_behavior=pymdt.utils.find_fail_behavior.throw,
                find_context="load tier master list"
                )
            
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ldwt, "LoadTier", t, **kwargs
            )

    @staticmethod
    def _extract_owner(default_owner, **kwargs):
        return kwargs.get("owner", default_owner)

    @staticmethod
    def _extract_prm_microgrid_settings(mg: MDT.Microgrid) -> MDT.PRMMicrogridSettings:
        prmSets = details._extract_prm_settings()
        return prmSets.get_MicrogridSettings(mg)
    
    @staticmethod
    def _extract_prm_settings() -> MDT.PRMSettings:
        return pymdt.DriverProxy.PRMSettings

    @staticmethod
    def _extract_refueler_settings(refueler, **kwargs):
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            refueler, "RefuelingTimeOfDay",
            kwargs.get("time_of_day", refueler.RefuelingTimeOfDay), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            refueler, "RefuelingPeriod",
            kwargs.get("period", refueler.RefuelingPeriod), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            refueler, "RefuelingQuantity",
            kwargs.get("quantity", refueler.RefuelingQuantity), **kwargs
            )

    @staticmethod
    def _add_spec_find_args(context_lead_in: str, kwargs: dict):
        kwargs["find_fail_behavior"] = pymdt.utils.find_fail_behavior.throw
        kwargs["find_context"] = context_lead_in + " specifications"
        
    @staticmethod
    def build_line(mg: MDT.Microgrid, name: str, fn, sn, **kwargs) -> MDT.Line:
        if name is None: name = MDT.Line.MakeDefaultName(fn, sn)
        l = MDT.Line(mg, name)
        pymdt.utils.details._extract_guid(l, **kwargs)
        
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            l, "FirstNode", fn, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            l, "SecondNode", sn, **kwargs
            )
        
        details._add_spec_find_args("line", kwargs)
        details._extract_specifications(
            l, pymdt.DriverProxy.LineSpecifications, **kwargs
            )
        details._extract_retrofit_cost(l, **kwargs)
        pymdt.utils.details._extract_failure_modes(l, **kwargs)
        details._extract_fragilities(l, **kwargs)
        pymdt.utils.details._extract_notes(l, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            l, "Length", kwargs.get("length", 0.0), **kwargs
            )
        return l

    @staticmethod
    def build_diesel_tank(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.DieselTank:
        t = MDT.DieselTank(mg, name)
        pymdt.utils.details._extract_guid(t, **kwargs)
        details._extract_node_location(t, **kwargs)
        details._add_spec_find_args("diesel tank", kwargs)
        details._extract_specifications(
            t, pymdt.DriverProxy.DieselTankSpecifications, **kwargs
            )
        pymdt.utils.details._extract_notes(t, **kwargs)
        details._extract_retrofit_cost(t, **kwargs)
        if "infinite_fuel" in kwargs:
            mgSets = details._extract_prm_microgrid_settings(mg)
            pymdt.utils.details._execute_loggable_indexed_property_set(
                mgSets, "UseInfiniteDieselFuel", t, kwargs["infinite_fuel"],
                **kwargs
                )
        return t
    
    @staticmethod
    def build_propane_tank(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PropaneTank:
        t = MDT.PropaneTank(mg, name)
        pymdt.utils.details._extract_guid(t, **kwargs)
        details._extract_node_location(t, **kwargs)
        details._add_spec_find_args("propane tank", kwargs)
        details._extract_specifications(
            t, pymdt.DriverProxy.PropaneTankSpecifications, **kwargs
            )
        pymdt.utils.details._extract_notes(t, **kwargs)
        details._extract_retrofit_cost(t, **kwargs)
        if "infinite_fuel" in kwargs:
            mgSets = details._extract_prm_microgrid_settings(mg)
            pymdt.utils.details._execute_loggable_indexed_property_set(
                mgSets, "UseInfinitePropane", t, kwargs["infinite_fuel"],
                **kwargs
                )
        return t
    
    @staticmethod
    def build_hazard(name: str, **kwargs) -> MDT.Hazard:
        haz = MDT.Hazard(name)
        pymdt.utils.details._extract_guid(haz, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            haz, "IntensityGenerator", kwargs.get("intensity_generator"),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            haz, "Units", kwargs.get("units", ""), **kwargs
            )
        pymdt.utils.details._extract_notes(haz, **kwargs)
        return haz

    @staticmethod
    def build_design_basis_threat(name: str, **kwargs) -> MDT.DesignBasisThreat:
        dbt = MDT.DesignBasisThreat(name)
        pymdt.utils.details._extract_guid(dbt, **kwargs)
        pymdt.utils.details._extract_failure_distributions(dbt, **kwargs)
        pymdt.utils.details._extract_notes(dbt, **kwargs)
        return dbt
        
    @staticmethod
    def build_solar_generator(b: MDT.Bus, name: str, **kwargs) -> MDT.SolarGenerator:
        sg = MDT.SolarGenerator(b, name)
        pymdt.utils.details._extract_guid(sg, **kwargs)
        details._add_spec_find_args("solar generator", kwargs)
        details._extract_specifications(
            sg, pymdt.DriverProxy.SolarGeneratorSpecifications, **kwargs
            )
        details._extract_node_location(sg, **kwargs)
        pymdt.utils.details._extract_failure_modes(sg, **kwargs)
        details._extract_fragilities(sg, **kwargs)
        pymdt.utils.details._extract_notes(sg, **kwargs)
        details._extract_retrofit_cost(sg, **kwargs)
        kwargs["find_context"] = "solar resources"
        rec = details._extract_resource(b.Site.SolarResources, **kwargs)
        if rec is not None:
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                sg, "SolarResource", rec, **kwargs
                )
        return sg

    @staticmethod
    def build_wind_generator(b: MDT.Bus, name: str, **kwargs) -> MDT.WindGenerator:
        wg = MDT.WindGenerator(b, name)
        pymdt.utils.details._extract_guid(wg, **kwargs)
        details._add_spec_find_args("wind generator", kwargs)
        details._extract_specifications(
            wg, pymdt.DriverProxy.WindGeneratorSpecifications, **kwargs
            )
        details._extract_node_location(wg, **kwargs)
        pymdt.utils.details._extract_failure_modes(wg, **kwargs)
        details._extract_fragilities(wg, **kwargs)
        pymdt.utils.details._extract_notes(wg, **kwargs)
        details._extract_retrofit_cost(wg, **kwargs)
        kwargs["find_context"] = "wind resources"
        rec = details._extract_resource(b.Site.WindResources, **kwargs)
        if rec is not None:           
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                wg, "WindResource", rec, **kwargs
                )
        return wg

    @staticmethod
    def build_hydro_generator(b: MDT.Bus, name: str, **kwargs) -> MDT.HydroGenerator:
        hg = MDT.HydroGenerator(b, name)
        pymdt.utils.details._extract_guid(hg, **kwargs)
        details._add_spec_find_args("hydro generator", kwargs)
        details._extract_specifications(
            hg, pymdt.DriverProxy.HydroGeneratorSpecifications, **kwargs
            )
        details._extract_node_location(hg, **kwargs)
        pymdt.utils.details._extract_failure_modes(hg, **kwargs)
        details._extract_fragilities(hg, **kwargs)
        pymdt.utils.details._extract_notes(hg, **kwargs)
        details._extract_retrofit_cost(hg, **kwargs)
        kwargs["find_context"] = "hydro resources"
        rec = details._extract_resource(b.Site.HydroResources, **kwargs)
        if rec is not None:
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                hg, "HydroResource", rec, **kwargs
                )
        return hg
    
    @staticmethod
    def build_diesel_generator(b: MDT.Bus, name: str, **kwargs) -> MDT.DieselGenerator:
        dg = MDT.DieselGenerator(b, name)
        pymdt.utils.details._extract_guid(dg, **kwargs)
        details._add_spec_find_args("diesel generator", kwargs)
        details._extract_specifications(
            dg, pymdt.DriverProxy.DieselGeneratorSpecifications, **kwargs
            )
        details._extract_fuel_tanks(dg, b.Microgrid.get_DieselTanks(), **kwargs)
        pymdt.utils.details._extract_failure_modes(dg, **kwargs)
        details._extract_fragilities(dg, **kwargs)
        details._extract_node_location(dg, **kwargs)
        details._extract_retrofit_cost(dg, **kwargs)
        pymdt.utils.details._extract_notes(dg, **kwargs)
        return dg
    
    @staticmethod
    def build_propane_generator(b: MDT.Bus, name: str, **kwargs) -> MDT.PropaneGenerator:
        pg = MDT.PropaneGenerator(b, name)
        pymdt.utils.details._extract_guid(pg, **kwargs)
        details._add_spec_find_args("propane generator", kwargs)
        details._extract_specifications(
            pg, pymdt.DriverProxy.PropaneGeneratorSpecifications, **kwargs
            )
        details._extract_fuel_tanks(pg, b.Microgrid.get_PropaneTanks(), **kwargs)
        pymdt.utils.details._extract_failure_modes(pg, **kwargs)
        details._extract_fragilities(pg, **kwargs)
        details._extract_node_location(pg, **kwargs)
        details._extract_retrofit_cost(pg, **kwargs)
        pymdt.utils.details._extract_notes(pg, **kwargs)
        return pg
    
    @staticmethod
    def build_natural_gas_generator(b: MDT.Bus, name: str, **kwargs) -> MDT.NaturalGasGenerator:
        ngg = MDT.NaturalGasGenerator(b, name)
        pymdt.utils.details._extract_guid(ngg, **kwargs)
        details._add_spec_find_args("natural gas generator", kwargs)
        details._extract_specifications(
            ngg, pymdt.DriverProxy.NaturalGasGeneratorSpecifications, **kwargs
            )
        details._extract_node_location(ngg, **kwargs)
        pymdt.utils.details._extract_failure_modes(ngg, **kwargs)
        details._extract_fragilities(ngg, **kwargs)
        details._extract_retrofit_cost(ngg, **kwargs)
        pymdt.utils.details._extract_notes(ngg, **kwargs)
        return ngg
    
    @staticmethod
    def build_battery(b: MDT.Bus, name: str, **kwargs) -> MDT.Battery:
        bat = MDT.Battery(b, name)
        pymdt.utils.details._extract_guid(bat, **kwargs)
        details._add_spec_find_args("battery", kwargs)
        details._extract_specifications(
            bat, pymdt.DriverProxy.BatterySpecifications, **kwargs
            )
        details._extract_node_location(bat, **kwargs)
        pymdt.utils.details._extract_failure_modes(bat, **kwargs)
        details._extract_fragilities(bat, **kwargs)
        details._extract_retrofit_cost(bat, **kwargs)
        pymdt.utils.details._extract_notes(bat, **kwargs)
        return bat
    
    @staticmethod
    def build_inverter(b: MDT.Bus, name: str, **kwargs) -> MDT.Inverter:
        inv = MDT.Inverter(b, name)
        pymdt.utils.details._extract_guid(inv, **kwargs)
        details._add_spec_find_args("inverter", kwargs)
        details._extract_specifications(
            inv, pymdt.DriverProxy.InverterSpecifications, **kwargs
            )
        details._extract_node_location(inv, **kwargs)
        pymdt.utils.details._extract_failure_modes(inv, **kwargs)
        details._extract_fragilities(inv, **kwargs)
        details._extract_retrofit_cost(inv, **kwargs)
        pymdt.utils.details._extract_notes(inv, **kwargs)
        return inv
    
    @staticmethod
    def build_ups(b: MDT.Bus, name: str, **kwargs) -> MDT.UninterruptiblePowerSupply:
        ups = MDT.UninterruptiblePowerSupply(b, name)
        pymdt.utils.details._extract_guid(ups, **kwargs)
        details._add_spec_find_args("UPS", kwargs)
        details._extract_specifications(
            ups, pymdt.DriverProxy.UninterruptiblePowerSupplySpecifications,
            **kwargs
            )
        details._extract_node_location(ups, **kwargs)
        pymdt.utils.details._extract_failure_modes(ups, **kwargs)
        details._extract_fragilities(ups, **kwargs)
        details._extract_retrofit_cost(ups, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ups, "LoadSection", kwargs.get("load_section"), **kwargs
            )
        pymdt.utils.details._extract_notes(ups, **kwargs)
        return ups
    
    @staticmethod    
    def build_load_section(b: MDT.Bus, name: str, **kwargs) -> MDT.LoadSection:
        ls = MDT.LoadSection(b, name)
        pymdt.utils.details._extract_guid(ls, **kwargs)
        details._extract_period_and_interval(ls, **kwargs)
        details._extract_node_location(ls, **kwargs)
        pymdt.utils.details._extract_voltage(ls, **kwargs)
        pymdt.utils.details._extract_notes(ls, **kwargs)
        return ls

    @staticmethod    
    def build_load_tier(name: str, priority: int, **kwargs) -> MDT.LoadTier:
        lt = MDT.LoadTier(name)
        pymdt.utils.details._extract_guid(lt, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            lt, "Priority", priority, **kwargs
            )
        pymdt.utils.details._extract_notes(lt, **kwargs)
        return lt

    @staticmethod    
    def build_tranformer(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Transformer:
        t = MDT.Transformer(mg, name)
        pymdt.utils.details._extract_guid(t, **kwargs)
        details._extract_node_location(t, **kwargs)
        details._add_spec_find_args("transformer", kwargs)
        details._extract_specifications(
            t, pymdt.DriverProxy.TransformerSpecifications, **kwargs
            )
        pymdt.utils.details._extract_failure_modes(t, **kwargs)
        details._extract_fragilities(t, **kwargs)
        details._extract_retrofit_cost(t, **kwargs)
        pymdt.utils.details._extract_notes(t, **kwargs)
        return t
    
    @staticmethod
    def build_bus(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Bus:
        b = MDT.Bus(mg, name)
        pymdt.utils.details._extract_guid(b, **kwargs)
        details._extract_node_location(b, **kwargs)
        pymdt.utils.details._extract_voltage(b, **kwargs)
        pymdt.utils.details._extract_notes(b, **kwargs)
        return b
    
    @staticmethod
    def build_microgrid(s: MDT.Site, name: str, **kwargs) -> MDT.Microgrid:
        mg = MDT.Microgrid(s, name)
        pymdt.utils.details._extract_guid(mg, **kwargs)
        pymdt.utils.details._extract_notes(mg, **kwargs)
        return mg
    
    @staticmethod
    def _extract_node_group_properties(ng: MDT.NodeGroup, x, y, width, height, **kwargs):
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ng, "Color", pymdt.utils.details._extract_color(**kwargs), **kwargs
            )

        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ng, "TextFont", pymdt.utils.details._extract_font(**kwargs), **kwargs
            )
            
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ng, "Location", System.Drawing.PointF(x, y), **kwargs
            )
            
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ng, "Size", System.Drawing.SizeF(width, height), **kwargs
            )

        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ng, "TextAlignment",
            pymdt.utils.details._extract_text_alignment(**kwargs), **kwargs
            )

    @staticmethod
    def build_microgrid_node_group(mg: MDT.Microgrid, name: str, x, y, width, height, **kwargs) -> MDT.MicrogridNodeGroup:
        g = MDT.MicrogridNodeGroup(mg, name)
        pymdt.utils.details._extract_guid(g, **kwargs)
        pymdt.utils.details._extract_notes(g, **kwargs)
        details._extract_node_group_properties(g, x, y, width, height, **kwargs)
        return g
    
    @staticmethod
    def build_site_node_group(s: MDT.Site, name: str, x, y, width, height, **kwargs) -> MDT.SiteNodeGroup:
        g = MDT.SiteNodeGroup(s, name)
        pymdt.utils.details._extract_guid(g, **kwargs)
        pymdt.utils.details._extract_notes(g, **kwargs)
        details._extract_node_group_properties(g, x, y, width, height, **kwargs)
        return g
    
    @staticmethod
    def build_node(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Node:
        n = MDT.Node(mg, name)
        pymdt.utils.details._extract_guid(n, **kwargs)
        details._extract_node_location(n, **kwargs)
        pymdt.utils.details._extract_voltage(n, **kwargs)
        pymdt.utils.details._extract_notes(n, **kwargs)
        return n
    
    @staticmethod
    def build_switch(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Switch:
        sw = MDT.Switch(mg, name)
        pymdt.utils.details._extract_guid(sw, **kwargs)
        details._extract_node_location(sw, **kwargs)
        details._add_spec_find_args("switch", kwargs)
        details._extract_specifications(
            sw, pymdt.DriverProxy.SwitchSpecifications, **kwargs
            )
        pymdt.utils.details._extract_failure_modes(sw, **kwargs)
        details._extract_fragilities(sw, **kwargs)
        details._extract_retrofit_cost(sw, **kwargs)
        pymdt.utils.details._extract_notes(sw, **kwargs)
        return sw

    @staticmethod
    def _extract_stored_configuration(ds, all_configs: list, **kwargs) -> MDT.StoredTierLoadConfiguration:
        if "stored_configuration" not in kwargs: return
        stc = kwargs["stored_configuration"]
        if type(stc) is str: stc = details._find_stored_config(
            all_configs, kwargs["stored_configuration"], **kwargs
            )
        stc.LoadConfigurationData()        
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            ds, "StoredConfiguration", stc, **kwargs
            )
        return stc
        
    @staticmethod
    def _extract_stored_configuration_or_data(ds, all_configs: list, **kwargs):
        if "stored_configuration" in kwargs:
            details._extract_stored_configuration(ds, all_configs, **kwargs)
        elif "data" in kwargs:
            ResetRegularPeriodData(ds, kwargs["data"], **kwargs)

    @staticmethod
    def build_load_data_with_tier(lc: MDT.ILoadContainer, name: str, **kwargs) -> MDT.LoadDataWithTier:
        ldwt = MDT.LoadDataWithTier(name, lc)
        pymdt.utils.details._extract_guid(ldwt, **kwargs)
        details._extract_stored_configuration_or_data(
            ldwt, details.StoredLoadProfiles, **kwargs
            )
        details._extract_tier(ldwt, **kwargs)
        pymdt.utils.details._extract_notes(ldwt, **kwargs)
        return ldwt
    
    @staticmethod    
    def build_microgrid_design_option(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.MicrogridDesignOption:
        mdo = MDT.MicrogridDesignOption(mg, name)
        pymdt.utils.details._extract_guid(mdo, **kwargs)
        pymdt.utils.details._extract_notes(mdo, **kwargs)
        return mdo
    
    @staticmethod
    def build_bus_design_option(mdo: MDT.MicrogridDesignOption, b: MDT.Bus, name: str, **kwargs) -> MDT.BusDesignOption:
        if b is None:
            name = pymdt.utils.MakeUsableName(mdo.Microgrid.AllBusses, "Bus 1")
            b = details.build_bus(mdo.Microgrid, name)
        bdo = MDT.BusDesignOption(b, name)
        pymdt.utils.details._extract_guid(bdo, **kwargs)
        pymdt.utils.details._extract_notes(bdo, **kwargs)
        return bdo
    
    @staticmethod
    def build_solar_resource(name: str, **kwargs) -> MDT.SolarResource:
        sr = MDT.SolarResource(name)
        pymdt.utils.details._extract_guid(sr, **kwargs)
        if "stored_configuration" in kwargs:
            kwargs["find_fail_behavior"] = pymdt.utils.find_fail_behavior.throw
            kwargs["fail_context="] = "stored solar resource configurations"
            details._extract_stored_configuration(sr, details.StoredSolarProfiles, **kwargs)
        else:
            details._extract_period_and_interval(sr, **kwargs)
            if "data" in kwargs:
                ResetRegularPeriodData(sr, kwargs["data"], **kwargs)
        pymdt.utils.details._extract_notes(sr, **kwargs)
        return sr
    
    @staticmethod
    def build_wind_resource(name: str, **kwargs) -> MDT.WindResource:
        wr = MDT.WindResource(name)
        pymdt.utils.details._extract_guid(wr, **kwargs)
        if "stored_configuration" in kwargs:
            kwargs["find_fail_behavior"] = pymdt.utils.find_fail_behavior.throw
            kwargs["fail_context="] = "stored wind resource configurations"
            details._extract_stored_configuration(wr, details.StoredWindProfiles, **kwargs)
        else:
            details._extract_period_and_interval(wr, **kwargs)
            if "data" in kwargs:
                ResetRegularPeriodData(wr, kwargs["data"], **kwargs)
        pymdt.utils.details._extract_notes(wr, **kwargs)
        return wr
    
    @staticmethod
    def build_hydro_resource(name: str, **kwargs) -> MDT.HydroResource:
        hr = MDT.HydroResource(name)
        pymdt.utils.details._extract_guid(hr, **kwargs)
        if "stored_configuration" in kwargs:
            kwargs["find_fail_behavior"] = pymdt.utils.find_fail_behavior.throw
            kwargs["fail_context="] = "stored hydro resource configurations"
            details._extract_stored_configuration(hr, details.StoredHydroProfiles, **kwargs)
        else:
            details._extract_period_and_interval(hr, **kwargs)
            if "data" in kwargs:
                ResetRegularPeriodData(hr, kwargs["data"], **kwargs)
        pymdt.utils.details._extract_notes(hr, **kwargs)
        return hr
    
    @staticmethod
    def _find_stored_config(all_configs: list, name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
        return pymdt.utils.FindEntityByName(all_configs, name, **kwargs)
    
    @staticmethod
    def _find_and_load_stored_config(all_configs: list, name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
        sc = details._find_stored_config(all_configs, name, **kwargs)
        if sc is not None: sc.LoadConfigurationData()
        return sc

    @staticmethod
    def _create_stored_data_file(name: str, data_dir: str, **kwargs) -> MDT.StoredTierLoadConfiguration:                
        fName = os.path.join(data_dir, name + ".msrd")
        stDat = MDT.StoredTierLoadConfiguration(fName)    
        pymdt.utils.details._extract_guid(stDat, **kwargs)
        pymdt.utils.details._extract_notes(stDat, **kwargs)
        details._extract_tier(stDat, **kwargs)
        
        int_units = kwargs.get("interval_units", pymdt.utils.time_units.days)
        per_units = kwargs.get("period_units", pymdt.utils.time_units.hours)
        if hasattr(int_units, "value"): int_units = int_units.value
        if hasattr(per_units, "value"): per_units = per_units.value

        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stDat, "Interval", kwargs.get("interval", 1), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stDat, "IntervalUnits", int_units, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stDat, "Period", kwargs.get("period", 1), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stDat, "PeriodUnits", per_units, **kwargs
            )

        if "data" in kwargs:
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                stDat, "LoadData",
                ResetRegularPeriodData(None, kwargs["data"], **kwargs), **kwargs
                )

        fStr = System.IO.FileStream(fName, System.IO.FileMode.Create)
        fmt = System.Runtime.Serialization.Formatters.Binary.BinaryFormatter()
        fmt.Binder = MDT.Driver.CustomSerializationBinder()
        ar = Common.Serialization.Archive(pymdt.MDT_VERSION)
        node = ar.AddEmptyNode(stDat.GetType(), stDat.GUID.ToString())
        stDat.SaveConfigurationData(node)
        ar.WriteFormatted(fmt, fStr)
        fStr.Close()
        return stDat
    
details._load_all_stored_configs(
    pymdt.DriverProxy.MakeLoadDataDirectory(), details.StoredLoadProfiles
    )
        
details._load_all_stored_configs(
    pymdt.DriverProxy.MakeThermalLoadDataDirectory(),
    details.StoredThermalProfiles
    )
        
details._load_all_stored_configs(
    pymdt.DriverProxy.MakeSolarDataDirectory(), details.StoredSolarProfiles
    )
        
details._load_all_stored_configs(
    pymdt.DriverProxy.MakeWindDataDirectory(), details.StoredWindProfiles
    )
        
details._load_all_stored_configs(
    pymdt.DriverProxy.MakeHydroDataDirectory(), details.StoredHydroProfiles
    )
    
def FindStoredSolarConfiguration(name: str) -> MDT.StoredTierLoadConfiguration:
    """ This function searches through all previously defined stored solar
    resource data sets and returns the one found with the supplied name or None.
    
    Parameters
    ----------
    name: str
        The name of the stored profile to find.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The found stored solar data set with data loaded or None if there is no
        data set by the supplied name.
    """
    return pymdt.details._find_and_load_stored_config(
        details.StoredSolarProfiles, name,
        find_fail_behavior=pymdt.utils.find_fail_behavior.throw,
        find_context="stored solar data configurations"
        )

def FindStoredLoadConfiguration(name: str) -> MDT.StoredTierLoadConfiguration:
    """ This function searches through all previously defined stored load
    profile data sets and returns the one found with the supplied name or None.
    
    Parameters
    ----------
    name: str
        The name of the stored profile to find.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The found stored load data set with data loaded or None if there is no
        data set by the supplied name.
    """
    return pymdt.details._find_and_load_stored_config(
        details.StoredLoadProfiles, name,
        find_fail_behavior=pymdt.utils.find_fail_behavior.throw,
        find_context="stored load data configurations"
        )

def FindStoredWindConfiguration(name: str) -> MDT.StoredTierLoadConfiguration:
    """ This function searches through all previously defined stored wind
    resource data sets and returns the one found with the supplied name or None.
    
    Parameters
    ----------
    name: str
        The name of the stored profile to find.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The found stored wind data set with data loaded or None if there is no
        data set by the supplied name.
    """
    return details._find_and_load_stored_config(
        details.StoredWindProfiles, name,
        find_fail_behavior=pymdt.utils.find_fail_behavior.throw,
        find_context="stored wind data configurations"
        )

def FindStoredHydroConfiguration(name: str) -> MDT.StoredTierLoadConfiguration:
    """ This function searches through all previously defined stored hydro
    resource data sets and returns the one found with the supplied name or None.
    
    Parameters
    ----------
    name: str
        The name of the stored profile to find.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The found stored hydro data set with data loaded or None if there is no
        data set by the supplied name.
    """
    return details._find_and_load_stored_config(details.StoredHydroProfiles, name)

def FindStoredThermalConfiguration(name: str) -> MDT.StoredTierLoadConfiguration:
    """ This function searches through all previously defined stored thermal
    load data sets and returns the one found with the supplied name or None.
    
    Parameters
    ----------
    name: str
        The name of the stored profile to find.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The found stored thermal data set with data loaded or None if there is
        no data set by the supplied name.
    """
    return details._find_and_load_stored_config(
        details.StoredThermalProfiles, name,
        find_fail_behavior=pymdt.utils.find_fail_behavior.throw,
        find_context="stored thermal data configurations"
        )

def MakeStoredLoadConfiguration(name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
    """ This helper function creates a new file containing load data information
    and makes it available for use in any models.
        
    Parameters
    ----------
    name: str
        The name to be given to this stored data file.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created data set.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        data: iterable of float
            The data to be stored in this new stored data file.
        period: int
            The number of period_units in the period of the data of this
            new file.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this new file.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            new file.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this new file.  The
            interval is the total time duration of the data set.
        notes: str
            Any notes to assign to the resulting data set.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The newly created representation of the new data file.
    """
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return details._create_stored_data_file(
            name, pymdt.DriverProxy.MakeLoadDataDirectory(), **kwargs
            )

def MakeStoredSolarDataConfiguration(name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
    """ This helper function creates a new file containing solar data information
    and makes it available for use in any models.
        
    Parameters
    ----------
    name: str
        The name to be given to this stored data file.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created data set.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        data: iterable of float
            The data to be stored in this new stored data file.
        period: int
            The number of period_units in the period of the data of this
            new file.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this new file.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            new file.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this new file.  The
            interval is the total time duration of the data set.
        notes: str
            Any notes to assign to the resulting data set.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The newly created representation of the new data file.
    """
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return details._create_stored_data_file(
            name, pymdt.DriverProxy.MakeSolarDataDirectory(), **kwargs
            )

def MakeStoredWindDataConfiguration(name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
    """ This helper function creates a new file containing wind data information
    and makes it available for use in any models.
        
    Parameters
    ----------
    name: str
        The name to be given to this stored data file.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created data set.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        data: iterable of float
            The data to be stored in this new stored data file.
        period: int
            The number of period_units in the period of the data of this
            new file.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this new file.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            new file.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this new file.  The
            interval is the total time duration of the data set.
        notes: str
            Any notes to assign to the resulting data set.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The newly created representation of the new data file.
    """
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return details._create_stored_data_file(
            name, pymdt.DriverProxy.MakeWindDataDirectory(), **kwargs
            )

def MakeStoredHydroDataConfiguration(name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
    """ This helper function creates a new file containing hydro data
    information and makes it available for use in any models.
        
    Parameters
    ----------
    name: str
        The name to be given to this stored data file.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created data set.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        data: iterable of float
            The data to be stored in this new stored data file.
        period: int
            The number of period_units in the period of the data of this
            new file.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this new file.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            new file.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this new file.  The
            interval is the total time duration of the data set.
        notes: str
            Any notes to assign to the resulting data set.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The newly created representation of the new data file.
    """
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return details._create_stored_data_file(
            name, pymdt.DriverProxy.MakeHydroDataDirectory(), **kwargs
            )

def MakeStoredThermalDataConfiguration(name: str, **kwargs) -> MDT.StoredTierLoadConfiguration:
    """ This helper function creates a new file containing thermal data
    information and makes it available for use in any models.
        
    Parameters
    ----------
    name: str
        The name to be given to this stored data file.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
                
        tier:
            The tier for this newly created data set.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        data: iterable of float
            The data to be stored in this new stored data file.
        period: int
            The number of period_units in the period of the data of this
            new file.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this new file.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            new file.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this new file.  The
            interval is the total time duration of the data set.
        notes: str
            Any notes to assign to the resulting data set.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.StoredTierLoadConfiguration:
        The newly created representation of the new data file.
    """
    if "__PYMDT_DOC_BUILD__" not in os.environ:
        return details._create_stored_data_file(
            name, pymdt.DriverProxy.MakeThermalDataDirectory(), **kwargs
            )

def MakeLine(mg: MDT.Microgrid, name: str, fn, sn, **kwargs) -> MDT.Line:
    """ This helper function creates a new line, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this line is being built.  If an "owner"
        parameter is not provided, then this microgrid is also used as the
        owner.
    name: str
        The name to be given to this line.  Names of lines within a microgrid
        must be unique.  If the name is None, then a default name is generated
        using the first and second nodes.
    fn
        The node to which to attach the first end of this line. This parameter
        can be None if you wish to assign the first node at a later time.
    sn
        The node to which to attach the second end of this line. This parameter
        can be None if you wish to assign the second node at a later time.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new line.  If not provided, the
            baseline specification is No Line.  This can  either be provided as
            an MDT.LineSpec object or as the name of the specification
            in which case a search will be conducted to find and assign the
            correct spec in the master list.
        specs:
            The list of all allowable specifications for the new line. This can
            be provided as a single entity or a list of entities. Each  entity
            can either be provided as an MDT.LineSpec object or as the
            name of the specification to use in which case a search of the
            master list will be conducted to find and assign the correct spec.
        length: float
            A value that is greater than or equal to 0 to be the length of the
            new line (ft).
        owner:
            An optional parameter to serve as the owner of the new line.  This
            is typically used when the new line is being created for a microgrid
            design option in which case the MDT.MicrogridDesignOption instance
            should be supplied.  If no owner is provided, then the supplied
            microgrid (mg) is used.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting line.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Line:
        The newly created line instance.
    """
    l = details.build_line(mg, name, fn, sn, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddLineCanceled", "get_Lines", l, **kwargs
            ) 
    return l

def MakeTransformer(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Transformer:
    """ This helper function creates a new transformer, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this transformer is being built.  If an "owner"
        parameter is not provided, then this microgrid is also used as the
        owner.
    name: str
        The name to be given to this transformer.  Names of transformers within
        a microgrid must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new transformer.  If not
            provided, the baseline specification is No Transformer.  This can
            either be provided as an MDT.TransformerSpec object or as
            the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new transformer.
            This can be provided as a single entity or a list of entities. Each 
            entity can either be provided as an MDT.TransformerSpecification
            object or as the name of the specification to use in which case a
            search of the master list will be conducted to find and assign the
            correct spec.
        owner:
            An optional parameter to serve as the owner of the new transformer. 
            This is typically used when the new transformer is being created for
            a microgrid design option in which case the
            MDT.MicrogridDesignOption instance should be supplied.  If no owner
            is provided, then the supplied microgrid (mg) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting transformer.  This is only useful if you intend to save
            and open a model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting transformer.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Transformer:
        The newly created transformer instance.
    """
    t = details.build_tranformer(mg, name, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddTransformerCanceled", "get_Transformers", t, **kwargs
            )
    return t

def MakeSwitch(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Switch:
    """ This helper function creates a new switch, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this switch is being built.  If an "owner"
        parameter is not provided, then this microgrid is also used as the
        owner.
    name: str
        The name to be given to this switch.  Names of switches within a
        microgrid must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new switch.  If not provided, the
            baseline specification is No Switch.  This can either be provided as
            an MDT.SwitchSpec object or as the name of the
            specification in which case a search will be conducted to find and
            assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new switch. This
            can be provided as a single entity or a list of entities. Each 
            entity can either be provided as an MDT.SwitchSpec object
            or as the name of the specification to use in which case a search of
            the master list will be conducted to find and assign the correct
            spec.
        owner:
            An optional parameter to serve as the owner of the new switch. 
            This is typically used when the new switch is being created for
            a microgrid design option in which case the
            MDT.MicrogridDesignOption instance should be supplied.  If no owner
            is provided, then the supplied microgrid (mg) is used.    
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting switch. This is only useful if you intend to save and open
            a model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting switch.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Switch:
        The newly created switch instance.   
    """
    sw = details.build_switch(mg, name, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddSwitchCanceled", "get_Switches", sw, **kwargs
            )
    return sw

def MakeBus(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Bus:
    """ This helper function creates a new bus, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this bus is being built.
    name: str
        The name to be given to this node.  Names of nodes within a microgrid
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting bus. This is only useful if you intend to save and open a
            model in the MDT GUI.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        owner:
            An optional parameter to serve as the owner of the new bus.  This
            is typically used if one does not want the bus added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting node.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Bus:
        The newly created bus instance.       
    """
    b = details.build_bus(mg, name, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddBusCanceled", "get_Busses", b, **kwargs
            )
    return b

def MakeMicrogrid(s: MDT.Site, name: str, **kwargs) -> MDT.Microgrid:
    """ This helper function creates a new microgrid, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this microgrid is being built.
    name: str
        The name to be given to this microgrid.  Names of microgrids within a
        site must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new microgrid.
            This is typically used if one does not want the microgrid added to
            the site as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied site (s) is
            used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting microgrid.
        guid:
            The unique identifier to use for this new microgrid.  This can be a
            string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created, random
            Guid is used.
        
    Returns
    -------
    MDT.Microgrid:
        The newly created microgrid instance.       
    """
    mg = details.build_microgrid(s, name, **kwargs)
    owner = details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddModelCanceled", "get_Models", mg, **kwargs
            )
    return mg

def MakeNode(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.Node:
    """ This helper function creates a new node, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this node is being built.  If an "owner"
        parameter is not provided, then this microgrid is also used as the
        owner.
    name: str
        The name to be given to this node.  Names of nodes within a microgrid
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new node. This is
            typically used when the new node is being created for a microgrid
            design option in which case the MDT.MicrogridDesignOption instance
            should be supplied.  If no owner is provided, then the supplied
            microgrid (mg) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting node. This is only useful if you intend to save and open a
            model in the MDT GUI.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting node.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Node:
        The newly created node instance.
    """
    n = details.build_node(mg, name, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddNodeCanceled", "get_Nodes", n, **kwargs
            )
    return n

def MakeDieselTank(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.DieselTank:
    """ This helper function creates a new diesel tank, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this tank is being built.  If an "owner"
        parameter is not provided, then this microgrid is also used as the
        owner.
    name: str
        The name to be given to this tank.  Names of tanks within a microgrid
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new tank.  If not provided, the
            baseline specification is No Tank.  This can either be provided as
            an MDT.DieselTankSpec object or as the name of the
            specification in which case a search will be conducted to find and
            assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new tank. This can
            be provided as a single entity or a list of entities. Each  entity
            can either be provided as an MDT.DieselTankSpec object or
            as the name of the specification to use in which case a search of
            the master list will be conducted to find and assign the correct
            spec.
        owner:
            An optional parameter to serve as the owner of the new tank. This
            is typically used when the new tank is being created for a microgrid
            design option in which case the MDT.MicrogridDesignOption instance
            should be supplied.  If no owner is provided, then the supplied
            microgrid (mg) is used.    
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting tank. This is only useful if you intend to save and open a
            model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        infinite_fuel: bool
            Whether or not this tank should be granted infinite fuel in the
            controller settings.  The default is False.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting tank.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.DieselTank:
        The newly created diesel tank instance.
    """
    t = details.build_diesel_tank(mg, name, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddDieselTankCanceled", "get_DieselTanks", t, **kwargs
            )
    return t

def MakePropaneTank(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PropaneTank:
    """ This helper function creates a new propane tank, extracts any provided
    properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this tank is being built.  If an "owner"
        parameter is not provided, then this microgrid is also used as the
        owner.
    name: str
        The name to be given to this tank.  Names of tanks within a microgrid
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new tank.  If not  provided, the
            baseline specification is No Tank.  This can either be provided as
            an MDT.PropaneTankSpec object or as the name of the
            specification in which case a search will be conducted to find and
            assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new tank. This can
            be provided as a single entity or a list of entities. Each  entity
            can either be provided as an MDT.PropaneTankSpec object or
            as the name of the specification to use in which case a search of
            the master list will be conducted to find and assign the correct
            spec.
        owner:
            An optional parameter to serve as the owner of the new tank. This is
            typically used when the new tank is being created for a microgrid
            design option in which case the MDT.MicrogridDesignOption instance
            should be supplied.  If no owner is provided, then the supplied
            microgrid (mg) is used.    
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting tank. This is only useful if you intend to save and open a
            model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        infinite_fuel: bool
            Whether or not this tank should be granted infinite fuel in the
            controller settings.  The default is False.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting propane tank.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.PropaneTank:
        The newly created propane tank instance.
    """
    t = details.build_propane_tank(mg, name, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddPropaneTankCanceled", "get_PropaneTanks", t, **kwargs
            )
    return t

def MakeDieselGenerator(b: MDT.Bus, name: str, **kwargs) -> MDT.DieselGenerator:
    """ This helper function creates a new diesel generator, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this diesel generator is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this diesel generator.  Names of diesel generators
        within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new diesel generator.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.DieselGeneratorSpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new diesel
            generator. This can be provided as a single entity or a list of
            entities. Each  entity can either be provided as an
            MDT.DieselGeneratorSpec object or as the name of the
            specification to use in which case a search of the master list will
            be conducted to find and assign the correct spec.
        owner:
            An optional parameter to serve as the owner of the new diesel
            generator.  This is typically used when the new diesel generator is
            being created for a microgrid design option in which case the
            MDT.BusDesignOption made for the microgrid design option instance
            should be supplied.  If no owner is provided, then the supplied bus
            (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting diesel generator. This is only useful if you intend to
            save and open a model in the MDT GUI.
        tanks:
            The list of the diesel tanks to be assigned to the new diesel
            generator.  This input can be an MDT.DieselTank instance, the name
            of a diesel tank in which case a search will be conducted to find
            the correct tank in the supplied microgrid, or a list of instances
            and/or names.  If not provided, no tanks are assigned.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting diesel generator.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.DieselGenerator:
        The newly created diesel generator instance.
    """
    dg = details.build_diesel_generator(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddDieselGeneratorCanceled", "get_DieselGenerators", dg,
            **kwargs
            )
    return dg

def MakeBattery(b: MDT.Bus, name: str, **kwargs) -> MDT.Battery:
    """ This helper function creates a new battery, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this battery is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this battery.  Names of batteries within a bus
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new battery.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.BatterySpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new battery. This
            can be provided as a single entity or a list of entities. Each
            entity can either be provided as an MDT.BatterySpec object
            or as the name of the specification to use in which case a search of
            the master list will be conducted to find and assign the correct
            spec.
        owner:
            An optional parameter to serve as the owner of the new battery.
            This is typically used when the new battery is being created for a
            microgrid design option in which case the MDT.BusDesignOption made
            for the microgrid design option instance should be supplied.  If no
            owner is provided, then the supplied bus (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting battery. This is only useful if you intend to
            save and open a model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting battery.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Battery:
        The newly created battery instance.
    """
    bat = details.build_battery(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddBatteryCanceled", "get_Batteries", bat, **kwargs
            )
    return bat

def MakeInverter(b: MDT.Bus, name: str, **kwargs) -> MDT.Inverter:
    """ This helper function creates a new inverter, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this inverter is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this inverter.  Names of inverters within a bus
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec
            The baseline specification for the new inverter.  If not provided,
            the baseline specification is No Generator.  This can either be
            provided as an MDT.BatterySpec object or as the name of the
            specification in which case a search will be conducted to find and
            assign the correct spec in the master list.
        specs
            The list of all allowable specifications for the new inverter. This
            can be provided as a single entity or a list of entities. Each
            entity can either be provided as an MDT.BatterySpec object
            or as the name of the specification to use in which case a search of
            the master list will be conducted to find and assign the correct
            spec.
        owner
            An optional parameter to serve as the owner of the new inverter.
            This is typically used when the new inverter is being created for a
            microgrid design option in which case the MDT.BusDesignOption made
            for the microgrid design option instance should be supplied.  If no
            owner is provided, then the supplied bus (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting inverter. This is only useful if you intend to
            save and open a model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes
            Any notes to assign to the resulting inverter.
        
    Returns
    -------
    MDT.Inverter:
        The newly created inverter instance.
    """
    inv = details.build_inverter(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddInverterCanceled", "get_Inverters", inv, **kwargs
            )
    return inv

def MakeUPS(b: MDT.Bus, name: str, **kwargs) -> MDT.UninterruptiblePowerSupply:
    """ This helper function creates a new UPS, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this UPS is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this UPS.  Names of UPSs within a bus
        must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new UPS.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.UPSSpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new UPS. This
            can be provided as a single entity or a list of entities. Each
            entity can either be provided as an MDT.UPSSpec object
            or as the name of the specification to use in which case a search of
            the master list will be conducted to find and assign the correct
            spec.
        owner:
            An optional parameter to serve as the owner of the new UPS.
            This is typically used when the new UPS is being created for a
            microgrid design option in which case the MDT.BusDesignOption made
            for the microgrid design option instance should be supplied.  If no
            owner is provided, then the supplied bus (b) is used.
        load_section: MDT.LoadSection
            The load section to which this UPS is assigned and to which it will
            provide power when/if necessary.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting UPS. This is only useful if you intend to
            save and open a model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting UPS.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.UninterruptiblePowerSupply:
        The newly created UPS instance.
    """
    ups = details.build_ups(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddUninterruptiblePowerSupplyCanceled",
            "get_UninterruptiblePowerSupplies", ups, **kwargs
            )
    return ups

def MakePropaneGenerator(b: MDT.Bus, name: str, **kwargs) -> MDT.PropaneGenerator:
    """ This helper function creates a new propane generator, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this propane generator is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this propane generator.  Names of propane
        generators within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new propane generator.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.PropaneGeneratorSpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new propane
            generator. This can be provided as a single entity or a list of
            entities. Each  entity can either be provided as an
            MDT.PropaneGeneratorSpec object or as the name of the
            specification to use in which case a search of the master list will
            be conducted to find and assign the correct spec.
        owner:
            An optional parameter to serve as the owner of the new propane
            generator.  This is typically used when the new propane generator is
            being created for a microgrid design option in which case the
            MDT.BusDesignOption made for the microgrid design option instance
            should be supplied.  If no owner is provided, then the supplied bus
            (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting propane generator. This is only useful if you intend to
            save and open a model in the MDT GUI.
        tanks:
            The list of the propane tanks to be assigned to the new propane
            generator.  This input can be an MDT.PropaneTank instance, the name
            of a propane tank in which case a search will be conducted to find
            the correct tank in the supplied microgrid, or a list of instances
            and/or names.  If not provided, no tanks are assigned.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting propane generator.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.PropaneGenerator:
        The newly created propane generator instance.
    """
    pg = details.build_propane_generator(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddPropaneGeneratorCanceled", "get_PropaneGenerators", pg,
            **kwargs
            )
    return pg

def MakeNaturalGasGenerator(b: MDT.Bus, name: str, **kwargs) -> MDT.NaturalGasGenerator:
    """ This helper function creates a new natural gas generator, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this natural gas generator is being built.  If an
        "owner" parameter is not provided, then this bus is also used as the
        owner.
    name: str
        The name to be given to this natural gas generator.  Names of natural
        gas generators within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new natural gas generator.  If
            not provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.NaturalGasGeneratorSpec object
            or as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new natural gas
            generator. This can be provided as a single entity or a list of
            entities. Each  entity can either be provided as an
            MDT.NaturalGasGeneratorSpec object or as the name of the
            specification to use in which case a search of the master list will
            be conducted to find and assign the correct spec.
        owner:
            An optional parameter to serve as the owner of the new natural gas
            generator.  This is typically used when the new natural gas
            generator is being created for a microgrid design option in which
            case the MDT.BusDesignOption made for the microgrid design option
            instance should be supplied.  If no owner is provided, then the
            supplied bus (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting natural gas generator. This is only useful if you intend
            to save and open a model in the MDT GUI.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting natural gas generator.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.NaturalGasGenerator:
        The newly created natural gas generator instance.
    """
    ngg = details.build_natural_gas_generator(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddNaturalGasGeneratorCanceled", "get_NaturalGasGenerators",
            ngg, **kwargs
            )
    return ngg

def MakeSolarGenerator(b: MDT.Bus, name: str, **kwargs) -> MDT.SolarGenerator:
    """ This helper function creates a new solar generator, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this solar generator is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this solar generator.  Names of solar generators
        within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new solar generator.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.SolarGeneratorSpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new solar
            generator. This can be provided as a single entity or a list of
            entities. Each  entity can either be provided as an
            MDT.SolarGeneratorSpec object or as the name of the
            specification to use in which case a search of the master list will
            be conducted to find and assign the correct spec.
        owner:
            An optional parameter to serve as the owner of the new solar
            generator.  This is typically used when the new solar generator is
            being created for a microgrid design option in which case the
            MDT.BusDesignOption made for the microgrid design option instance
            should be supplied.  If no owner is provided, then the supplied bus
            (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting solar generator. This is only useful if you intend to save
            and open a model in the MDT GUI.
        resource:
            The instance or name of the solar resource to be assigned to the
            new solar generator.  If not provided, no resource is assigned.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting solar generator.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.SolarGenerator:
        The newly created solar instance.
    """
    sg = details.build_solar_generator(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddSolarGeneratorCanceled", "get_SolarGenerators", sg,
            **kwargs
            )
    return sg

def MakeWindGenerator(b: MDT.Bus, name: str, **kwargs) -> MDT.WindGenerator:
    """ This helper function creates a new wind generator, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this wind generator is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this wind generator.  Names of wind generators
        within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new wind generator.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.WindGeneratorSpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new wind generator.
            This can be provided as a single entity or a list of entities. Each
            entity can either be provided as an MDT.WindGeneratorSpecification
            object or as the name of the specification to use in which case a
            search of the master list will be conducted to find and assign the
            correct spec.
        owner:
            An optional parameter to serve as the owner of the new wind
            generator.  This is typically used when the new wind generator is
            being created for a microgrid design option in which case the
            MDT.BusDesignOption made for the microgrid design option instance
            should be supplied.  If no owner is provided, then the supplied bus
            (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting wind generator. This is only useful if you intend to save
            and open a model in the MDT GUI.
        resource:
            The instance or name of the wind resource to be assigned to the
            new wind generator.  If not provided, no resource is assigned.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting wind generator.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.WindGenerator:
        The newly created wind instance.
    """
    wg = details.build_wind_generator(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddWindGeneratorCanceled", "get_WindGenerators", wg,
            **kwargs
            )
    return wg

def MakeHydroGenerator(b: MDT.Bus, name: str, **kwargs) -> MDT.HydroGenerator:
    """ This helper function creates a new hydro generator, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this hydro generator is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this hydro generator.  Names of hydro generators
        within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        base_spec:
            The baseline specification for the new hydro generator.  If not
            provided, the baseline specification is No Generator.  This can
            either be provided as an MDT.HydroGeneratorSpec object or
            as the name of the specification in which case a search will be
            conducted to find and assign the correct spec in the master list.
        specs:
            The list of all allowable specifications for the new hydro
            generator. This can be provided as a single entity or a list of
            entities. Each entity can either be provided as an
            MDT.HydroGeneratorSpec object or as the name of the
            specification to use in which case a search of the master list will
            be conducted to find and assign the correct spec.
        owner:
            An optional parameter to serve as the owner of the new hydro
            generator.  This is typically used when the new hydro generator is
            being created for a microgrid design option in which case the
            MDT.BusDesignOption made for the microgrid design option instance
            should be supplied.  If no owner is provided, then the supplied bus
            (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting hydro generator. This is only useful if you intend to save
            and open a model in the MDT GUI.
        resource:
            The instance or name of the hydro resource to be assigned to the
            new hydro generator.  If not provided, no resource is assigned.
        retrofit_cost: float
            The cost, if any, to keep the baseline specification in a solution.
            If not supplied, the value defaults to $0.
        failure_modes:
            A list of all defined failure modes for the resulting component,
            if any.  The elements of the list are of type MDT.FailureMode.
        fragilities:
            A dictionary in which the keys are hazards and the values are
            fragility curves for those hazards.  Each entry in the dictionary
            results in a fragility for the new component.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting hydro generator.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.HydroGenerator:
        The newly created hydro instance.
    """
    hg = details.build_hydro_generator(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddHydroGeneratorCanceled", "get_HydroGenerators", hg, **kwargs
            )
    return hg

def MakeSolarResource(s: MDT.Site, name: str, **kwargs) -> MDT.SolarResource:
    """ This helper function creates a new solar resource, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this solar resource is being built.
    name: str
        The name to be given to this solar resource.  Names of solar resources
        within a site must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        data: iterable of float
            The data to assign to this newly created resource.  This is only
            used of a stored_configuration is not provided.
        stored_configuration:
            Either an MDT.StoredTierLoadConfiguration or the name of one to be
            used as the load data for this new data object.  If this is
            provided, then the data, period, period_units, interval, and
            interval_units are all taken from this configuration object and any
            that were provided are ignored.  If a stored configuration is not to
            be used, then don't provide this parameter.
        period: int
            The number of period_units in the period of the data of this
            resource.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this resource.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            resource.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this resource.  The
            interval is the total time duration of the data set.
        owner:
            An optional parameter to serve as the owner of the new resource.
            This is typically used if one does not want the resource added to
            the site as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied site (s) is
            used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting solar resource.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.SolarResource:
        The newly created solar resource instance.
    """
    sr = details.build_solar_resource(name, **kwargs)
    owner = details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddSolarResourceCanceled", "get_SolarResources", sr, **kwargs
            )
    return sr

def MakeWindResource(s: MDT.Site, name: str, **kwargs) -> MDT.WindResource:
    """ This helper function creates a new wind resource, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this wind resource is being built.
    name: str
        The name to be given to this wind resource.  Names of wind resources
        within a site must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        data: iterable of float
            The data to assign to this newly created resource.  This is only
            used of a stored_configuration is not provided.
        stored_configuration:
            Either an MDT.StoredTierLoadConfiguration or the name of one to be
            used as the load data for this new data object.  If this is
            provided, then the data, period, period_units, interval, and
            interval_units are all taken from this configuration object and any
            that were provided are ignored.  If a stored configuration is not to
            be used, then don't provide this parameter.
        period: int
            The number of period_units in the period of the data of this
            resource.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this resource.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            resource.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this resource.  The
            interval is the total time duration of the data set.
        owner:
            An optional parameter to serve as the owner of the new resource.
            This is typically used if one does not want the resource added to
            the site as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied site (s) is
            used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting wind resource.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.WindResource:
        The newly created wind resource instance.
    """
    wr = details.build_wind_resource(name, **kwargs)
    owner = details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddWindResourceCanceled", "get_WindResources", wr, **kwargs
            )
    return wr

def MakeHydroResource(s: MDT.Site, name: str, **kwargs) -> MDT.HydroResource:
    """ This helper function creates a new hydro resource, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this hydro resource is being built.
    name: str
        The name to be given to this hydro resource.  Names of hydro resources
        within a site must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        data: iterable of float
            The data to assign to this newly created resource.  The number of
            elements that should be in the list, if any, is determined by the
            period, period units, interval, and interval units of the owning
            load container (lc).  This is only used of a stored_configuration is
            not provided.
        stored_configuration:
            Either an MDT.StoredTierLoadConfiguration or the name of one to be
            used as the load data for this new data object.  If this is
            provided, then the data, period, period_units, interval, and
            interval_units are all taken from this configuration object and any
            that were provided are ignored.  If a stored configuration is not to
            be used, then don't provide this parameter.
        period: int
            The number of period_units in the period of the data of this
            resource.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this resource.  The period
            is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            resource.  The interval is the total time duration of the data set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this resource.  The
            interval is the total time duration of the data set.
        owner:
            An optional parameter to serve as the owner of the new resource.
            This is typically used if one does not want the resource added to
            the site as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied site (s) is
            used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting hydro resource.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.HydroResource:
        The newly created hydro resource instance.
    """
    hr = details.build_hydro_resource(name, **kwargs)
    owner = details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddHydroResourceCanceled", "get_HydroResources", hr, **kwargs
            )
    return hr

def MakeLoadSection(b: MDT.Bus, name: str, **kwargs) -> MDT.LoadSection:
    """ This helper function creates a new load section, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    b: MDT.Bus
        The bus for which this load section is being built.  If an "owner"
        parameter is not provided, then this bus is also used as the owner.
    name: str
        The name to be given to this load section.  Names of load sections
        within a bus must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new load section.
            This is typically used when the new load section is being created
            for a microgrid design option in which case the MDT.BusDesignOption
            made for the microgrid design option instance should be supplied.
            If no owner is provided, then the supplied bus (b) is used.
        loc: tuple[float,float]
            An optional parameter to set the x,y diagram location for the
            resulting load section. This is only useful if you intend to save
            and open a model in the MDT GUI.
        period: int
            The number of period_units in the period of the data of this
            load section.  The period is the time duration between data points.
        period_units: Common.Time.TimeAccumulation.Units
            The units of the period for the data of this load section.  The
            period is the time duration between data points.
        interval: int
            The number of interval_units in the interval of the data of this
            load section.  The interval is the total time duration of the data
            set.
        interval_units: Common.Time.TimeAccumulation.Units
            The units of the interval for the data of this load section.  The
            interval is the total time duration of the data set.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting load section.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.LoadSection:
        The newly created solar load section instance.
    """
    ls = details.build_load_section(b, name, **kwargs)
    owner = details._extract_owner(b, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddLoadSectionCanceled", "get_LoadSections", ls, **kwargs
            )
    return ls

def MakeLoadDataTier(lc: MDT.ILoadContainer, name: str, **kwargs) -> MDT.LoadDataWithTier:
    """ This helper function creates a new load section, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    lc: MDT.ILoadContainer
        The load container that will hold the newly created data.
    name: str
        The name to be given to this new load data set.  Names of tier load
        data sets within a load container must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created data set.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        data:
            A vector of double precision numbers to be the data assigned to this
            new tier load data set.  The number of elements that should be in
            the list, if any, is determined by the period, period units,
            interval, and interval units of the owning load container (lc).
            This input is ignored if a stored_configuration is provided.
        stored_configuration:
            Either an MDT.StoredTierLoadConfiguration or the name of one to be
            used as the load data for this new data object if desired.  If this
            is provided, then the data, period, period_units, interval, and
            interval_units are all taken from this configuration object and any
            that were provided are ignored.  If a stored configuration is not to
            be used, then don't provide this parameter.
        owner:
            An optional parameter to serve as the owner of the new load data.
            This is typically used if one does not want the load data added to
            the container as part of this call in which case None is specified
            as the owner.  If no owner is provided, then the supplied container
            (lc) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting load data set.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.LoadDataWithTier:
        The newly created solar load data instance.
    """
    ldwt = details.build_load_data_with_tier(lc, name, **kwargs)
    owner = details._extract_owner(lc, **kwargs)
    if owner is not None:
        if "data" in kwargs:
            dataset = kwargs["data"]
            if not pymdt.utils.details._is_collection(dataset): dataset = [dataset]
            
            if len(dataset) != owner.get_NumTimePeriods():
                errLog = kwargs.get("err_log", pymdt.GlobalErrorLog)
                errLog.AddEntry(
                    Common.Logging.LogCategories.Warning,
                    "A dataset with " +
                    Common.Util.UtilFuncs.MakePluralPhrase("entry", len(dataset), False, True) +
                    " was provided for " + owner.GetTypeAndIDString() + " that houses " +
                    Common.Util.UtilFuncs.MakePluralPhrase("entry", owner.get_NumTimePeriods(), False, True) +
                    "."
                    )
        
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddLoadDataSetCanceled", "get_LoadDataSets", ldwt, **kwargs
            )
    return ldwt

def MakeDesignBasisThreat(pu: MDT.PowerUtility, name: str, **kwargs) -> MDT.DesignBasisThreat:
    """ This helper function creates a new design basis threat, extracts any
    provided properties, loads it into its owner (pu), and returns it.
        
    Parameters
    ----------
    pu: MDT.PowerUtility
        The unreliable entity for which this design basis threat is being built.
    name: str
        The name to be given to the new design basis threat.  Names of design
        basis threat within an unreliable entity must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        mtbf: Common.Distributions.IDistribution
            The probability distribution describing the mean time between
            failures for this design basis threat.
        mttr: Common.Distributions.IDistribution
            The probability distribution describing the mean time to repair for
            this design basis threat.
        owner:
            An optional parameter to serve as the owner of the new DBT.
            This is typically used if one does not want the DBT added to
            the power utility as part of this call in which case None is
            specified as the owner.  If no owner is provided, then the supplied
            power utility (pu) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting design basis threat.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.DesignBasisThreat:
        The newly created design basis threat instance.
    """
    dbt = details.build_design_basis_threat(name, **kwargs)
    owner = details._extract_owner(pu, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddFailureModeCanceled", "get_FailureModes", dbt, **kwargs
            )
    return dbt

def MakeHazard(dbt: MDT.DesignBasisThreat, name: str, **kwargs) -> MDT.Hazard:
    """ This helper function creates a new hazard, extracts any provided
    properties, loads it into the provided DBT, and returns it.
        
    Parameters
    ----------
    dbt: MDT.DesignBasisThreat
        The DBT for which this hazard is being built.
    name: str
        The name to be given to this hazard.  Names of hazards within a DBT must
        be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        intensity_generator: MDT.IDistribution
            The distribution from which intensity values are drawn at the onset
            of each DBT.
        units:
            The units of this hazard to be used as a label.
        owner:
            An optional parameter to serve as the owner of the new hazard.
            This is typically used if one does not want the hazard added to
            the DBT as part of this call in which case None is specified as the
            owner.  If no owner is provided, then the supplied DBT (dbt) is
            used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting hazard.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Hazard:
        The newly created hazard instance.
    """
    haz = details.build_hazard(name, **kwargs)
    owner = details._extract_owner(dbt, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddHazardCanceled", "get_Hazards", haz, **kwargs
            )
    return haz
    
def MakeMicrogridDesignOption(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.MicrogridDesignOption:
    """ This helper function creates a new microgrid design option, extracts any
    provided properties, loads it into its owner (mg), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid into which the new design option will be installed.
    name: str
        The name to be given to the new design option.  Names of design options
        within a microgrid must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new design
            option.  This is typically used if one does not want the design
            option added to the microgrid as part of this call in which case
            None is specified as the owner.  If no owner is provided, then the
            supplied microgrid (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting design option.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.MicrogridDesignOption:
        The newly created microgrid design option instance.
    """
    mdo = details.build_microgrid_design_option(mg, name)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddDesignOptionCanceled", "get_DesignOptions", mdo, **kwargs
            )
    return mdo

def MakeBusDesignOption(mdo: MDT.MicrogridDesignOption, b: MDT.Bus, name: str, **kwargs) -> MDT.BusDesignOption:
    """ This helper function creates a new bus design option, extracts any
    provided properties, loads it into its owner (mdo), and returns it.
        
    Parameters
    ----------
    mdo: MDT.MicrogridDesignOption
        The microgrid design option into which the new bus design option will be
        installed.
    b: MDT.Bus
        The bus for which this bus design option is being built.  If this option
        is being built for a bus that is not part of the microgrid but instead
        should be added as part of the mdo, then this argument should be None.
        In that case, a new bus will be built.
    name: str
        The name to be given to the new bus design option.  Names of bus design
        options within a microgrid design option must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new bus design
            option.  This is typically used if one does not want the bus design
            option added to the microgrid design option as part of this call in
            which case None is specified as the owner.  If no owner is provided,
            then the supplied microgrid design option (mdo) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting bus design option.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.BusDesignOption:
        The newly created bus design option instance.
    """
    bdo = details.build_bus_design_option(mdo, b, name, **kwargs)
    owner = details._extract_owner(mdo, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddBusDesignOptionCanceled", "get_BusOptions", bdo, **kwargs
            )
    return bdo

def MakeLoadTier(name: str, priority: int, **kwargs) -> MDT.LoadTier:
    """ This helper function creates a new load tier, extracts any
    provided properties, loads it into the master list, and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new load tier.  Names of load tiers
        must be unique in the master list.
    priority: int
        The priority to be assigned to this new load tier.  The lower the value
        the higher the importance.  Negative numbers are not allowed.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new load tier.
            This is typically used if one does not want the load tier added to
            the driver as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the global Driver is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting load tier.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.LoadTier:
        The newly created load tier instance.
    """
    lt = details.build_load_tier(name, priority, **kwargs)
    owner = details._extract_owner(MDTDVR, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddLoadTierCanceled", "get_LoadTiers", lt, **kwargs
            )
    return lt

def MakeMicrogridNodeGroup(mg: MDT.Microgrid, name: str, x, y, width, height, **kwargs) -> MDT.MicrogridNodeGroup:
    """ This helper function creates a new microgrid node group, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which this node group is being built.
    name: str
        The name to be given to this node group.  Names of node groups within a
        microgrid must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new group.  This
            is typically used if one does not want the group added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting node group.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Bus:
        The newly created node group instance.       
    """
    g = details.build_microgrid_node_group(mg, name, x, y, width, height, **kwargs)
    owner = details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddNodeGroupCanceled", "get_NodeGroups", g, **kwargs
            )
    return g
        
def MakeSiteNodeGroup(s: MDT.Site, name: str, x, y, width, height, **kwargs) -> MDT.SiteNodeGroup:
    """ This helper function creates a new site node group, extracts any
    provided properties, loads it into its owner, and returns it.
        
    Parameters
    ----------
    s: MDT.Site
        The site for which this node group is being built.
    name: str
        The name to be given to this node group.  Names of node groups within a
        site must be unique.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new group. This
            is typically used if one does not want the group added to the site
            as part of this call in which case None is specified as the owner.
            If no owner is provided, then the supplied site (s) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new item.  If this argument is
            not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting node group.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.Bus:
        The newly created node group instance.       
    """
    g = details.build_site_node_group(s, name, x, y, width, height, **kwargs)
    owner = details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddNodeGroupCanceled", "get_NodeGroups", g, **kwargs
            )
    return g
        
def SetDieselInfiniteFuel(tank: MDT.DieselTank, infinite: bool = True, **kwargs):
    """ Assigns infinite fuel to the supplied tank or not depending on the value
    of the infinite parameter.
        
    Parameters
    ----------
    tank: MDT.DieselTank
        The tank to assign to have infinite fuel capacity or not.
    infinite: bool
        Whether or not the supplied tank should have infinite fuel capacity.
    """
    mgSets = details._extract_prm_microgrid_settings(tank.Microgrid)
    pymdt.utils.details._execute_loggable_indexed_property_set(
        mgSets, "UseInfiniteDieselFuel", tank, infinite, **kwargs
        )
    
def SetPropaneInfiniteFuel(tank: MDT.PropaneTank, infinite: bool = True, **kwargs):
    """ Assigns infinite fuel to the supplied tank or not depending on the value
    of the infinite parameter.
        
    Parameters
    ----------
    tank: MDT.PropaneTank
        The tank to assign to have infinite fuel capacity or not.
    infinite: bool
        Whether or not the supplied tank should have infinite fuel capacity.
    """
    mgSets = details._extract_prm_microgrid_settings(tank.Microgrid)
    pymdt.utils.details._execute_loggable_indexed_property_set(
        mgSets, "UseInfinitePropaneFuel", tank, infinite, **kwargs
        )

def ResetRegularPeriodData(rpd: MDT.IRegularPeriodData, dataset, **kwargs):
    """ Assigns the data in the supplied data set (data) to the supplied regular
    period data instance.
        
    Parameters
    ----------
    rpd: MDT.IRegularPeriodData
        The MDT data structure to load using the items in the second argument.
    data: iterable
        A collection of the values that should be pushed into the MDT data
        construct.  The items in this list must be float or convertible to
        float.
    """
    dat = Common.Databinding.ObservableBindingListWithUndo[float]()
    if not pymdt.utils.details._is_collection(dataset): dataset = [dataset]
    for d in dataset: dat.Add(float(d))
    if rpd is not None:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            rpd, "LoadDataList", dat, **kwargs
            )
    
def ConfigureMicrogridController(mg: MDT.Microgrid, **kwargs):
    """ Sets the type and properties of the controller that controls islanded
    microgrid operations (as opposed to startup or grid-tied behavior.)
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which the microgrid controller is to be configured.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        controller_type:
            An optional parameter that indicates what type of controller to
            use.  This is one of the controller_types enumeration members.
            If no controller_type is provided, then the default is standard.
        gen_restart_delay: float
            The number of seconds of delay if a generator fails to start and
            further attempts should be made.  This is the time between attempts.
            The default is 15 seconds.
        bus_sync_delay: float
            The number of seconds required to synchronize two busses that are to
            be connected together.  The default is 20 seconds.
        gen_sync_delay: float
            The number of seconds required to synchronize a generator onto an
            already powered bus.  The default is 15 seconds.
        min_power_dispatch_threshold: float
            The fraction of load to current online generator below which a
            re-dispatch should be attempted.  A re-dispatch in this case may
            choose to shut some generation down.  The default is 0.4 (40%).
        forecast_duration: float
            The number of hours over which to do load, solar, etc. forecasting
            for the purposes of generator dispatch.  The default is 1 hour.
        """
    mgSets = details._extract_prm_microgrid_settings(mg)
    mgCSets = mgSets.MicrogridControllerSettings
    
    if "controller_type" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            mgCSets, "ControllerType", kwargs["controller_type"].value,
            **kwargs
            )
        
    if "gen_restart_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            mgCSets, "GeneratorRestartDelay", kwargs["gen_restart_delay"],
            **kwargs
            )
        
    if "bus_sync_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            mgCSets, "BusSyncDelay", kwargs["bus_sync_delay"], **kwargs
            )
        
    if "gen_sync_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            mgCSets, "GeneratorSyncDelay", kwargs["gen_sync_delay"], **kwargs
            )
        
    if "min_power_dispatch_threshold" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            mgCSets, "MinimumPowerDispatchThreshold",
            kwargs["min_power_dispatch_threshold"], **kwargs
            )
        
    if "forecast_duration" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            mgCSets, "ForecastDuration", kwargs["forecast_duration"], **kwargs
            )
    
def ConfigureStartupController(mg: MDT.Microgrid, **kwargs):
    """ Sets the type and properties of the controller that controls the startup
    of islanded microgrid operations (as opposed to the established microgrid or
    grid-tied behavior.)
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid for which the startup controller is to be configured.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        gen_restart_delay: float
            The number of seconds of delay if a generator fails to start and
            further attempts should be made.  This is the time between attempts.
            The default is 15 seconds.
        bus_sync_delay: float
            The number of seconds required to synchronize two busses that are to
            be connected together.  The default is 20 seconds.
        gen_sync_delay: float
            The number of seconds required to synchronize a generator onto an
            already powered bus.  The default is 15 seconds.
        gen_failed_formation_delay: float
            The number of seconds between the onset of a DBT occurrence and the
            formation of a microgrid if some backup generators failed to start.
            With a start failure, some critical load may be at risk and so it
            may be desirable to start networking generators with less delay.
            The default is 120 seconds.
        no_gen_failed_formation_delay: float
            The number of seconds between the onset of a DBT occurrence and the
            formation of a microgrid if all backup generators started properly.
            This allows a ride-through for short duration DBTs. The default is
            600 seconds.
        renewable_start_delay: float
            The number of seconds of delay between the end of the startup
            procedure and the reconnection of any non-ride-through inverter
            controlled renewable assets.  The default is 300 seconds.
        """
    mgSets = details._extract_prm_microgrid_settings(mg)
    stCSets = mgSets.StartupControllerSettings
    
    if "gen_restart_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stCSets, "GeneratorRestartDelay", kwargs["gen_restart_delay"],
            **kwargs
            )
        
    if "gen_sync_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stCSets, "GeneratorSyncDelay", kwargs["gen_sync_delay"], **kwargs
            )
        
    if "bus_sync_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stCSets, "BusSyncDelay", kwargs["bus_sync_delay"], **kwargs
            )
        
    if "gen_failed_formation_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stCSets, "GeneratorFailedGridFormationDelay",
            kwargs["gen_failed_formation_delay"], **kwargs
            )
        
    if "no_gen_failed_formation_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stCSets, "NoGeneratorFailedGridFormationDelay",
            kwargs["no_gen_failed_formation_delay"], **kwargs
            )
    
    if "renewable_start_delay" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            stCSets, "RenewablesStartDelay", kwargs["renewable_start_delay"],
            **kwargs
            )
    
def ConfigureGridTiedController(mg: MDT.Microgrid, **kwargs):
    """ This helper function sets the properties of the controller that manages
    activities in the periods between DBT occurrences.
        
    The parameters all have to do with the tracking of failures and repairs
    during the grid-tied operation phase of the simulation.  A couple things to
    note are:

    1 - Even if tracking, statistics for failures and repairs are not kept
        during this phase.  The only real effect of doing so is that it is
        possible (or more possible) for an asset to be broken at the start
        of the next DBT.
    2 - Even if not tracking, a repair for an asset that failed during the
        DBT still may occur during the grid tied period and the full time
        of the repair will be tallied in statistics.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid instance for which the grid-tied controller is being
        configured.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        track_line_failures: bool
            Whether or not to execute failures and repairs of lines during the
            grid-tied operations.
        track_transformer_failures: bool
            Whether or not to execute failures and repairs of transformers
            during the grid-tied operations.
        track_switch_failures: bool
            Whether or not to execute failures and repairs of switches
            during the grid-tied operations.
        track_ups_failures: bool
            Whether or not to execute failures and repairs of UPSs
            during the grid-tied operations.
        track_battery_failures: bool
            Whether or not to execute failures and repairs of Batteries
            during the grid-tied operations.
        track_wind_failures: bool
            Whether or not to execute failures and repairs of Wind generators
            during the grid-tied operations.
        track_hydro_failures: bool
            Whether or not to execute failures and repairs of Hydro generators
            during the grid-tied operations.
        track_solar_failures: bool
            Whether or not to execute failures and repairs of Solar generators
            during the grid-tied operations.
        track_inverter_failures: bool
            Whether or not to execute failures and repairs of inverters during
            the grid-tied operations.
    """
    mgSets = details._extract_prm_microgrid_settings(mg)
    gtCSets = mgSets.GridTiedControllerSettings
    defVal = MDT.GridTiedControllerSettings.DefaultTrackingStatus
    
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackLineFailures",
        kwargs.get("track_line_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackTransformerFailures",
        kwargs.get("track_transformer_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackSwitchFailures",
        kwargs.get("track_switch_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackUPSFailures",
        kwargs.get("track_ups_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackBatteryFailures",
        kwargs.get("track_battery_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackWindGeneratorFailures",
        kwargs.get("track_wind_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackHydroGeneratorFailures",
        kwargs.get("track_hydro_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackSolarGeneratorFailures",
        kwargs.get("track_solar_failures", defVal), **kwargs
        )
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        gtCSets, "TrackInverterFailures",
        kwargs.get("track_inverter_failures", defVal), **kwargs
        )

def ConfigureDieselRefueller(mg: MDT.Microgrid, **kwargs):
    """ This helper function sets the properties of the diesel refueling
    schedule.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid instance for which the diesel refueller is being
        configured.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        time_of_day: float
            The hour of day at which the first refuel action takes place.  A
            real valued number of hours from midnight [0-24].
        period: float
            The amount of time in hours between refuellings.
        quantity: float
            The maximum amount of fuel that can be delivered in any refuelling
            action.  A value of -1 allows for the delivery of any amount of fuel
            (infinite).
    """
    mgSets = details._extract_prm_microgrid_settings(mg)
    rfSets = mgSets.DieselRefuelingStrategySettings
    details._extract_refueler_settings(rfSets, **kwargs)
    
def ConfigurePropaneRefueller(mg: MDT.Microgrid, **kwargs):
    """ This helper function sets the properties of the propane refueling
    schedule.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid instance for which the propane refueller is being
        configured.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        time_of_day: float
            The hour of day at which the first refuel action takes place.  A
            real valued number of hours from midnight [0-24].
        period: float
            The amount of time in hours between refuellings.
        quantity: float
            The maximum amount of fuel that can be delivered in any refuelling
            action.  A value of -1 allows for the delivery of any amount of fuel
            (infinite).
    """
    mgSets = details._extract_prm_microgrid_settings(mg)
    rfSets = mgSets.PropaneRefuelingStrategySettings
    details._extract_refueler_settings(rfSets, **kwargs)
    
def ExtractPRMSettings() -> MDT.PRMSettings:
    """ A helper method to extract and return the MDT.PRMSettings object.
    
    Returns
    -------
    MDT.PRMSettings:
        The settings object that controls the operation of the PRM simulation
        that evaluates the function of microgrid configurations.
    """
    return details._extract_prm_settings()

def RunMDTGUI(filename: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(
       [os.path.join(pymdt.MDT_BIN_DIR, "MDT-GUI.exe"), " " + filename]
       )

def ConfigurePRM(**kwargs):
    """ This helper function sets the properties of the PRM simulation.
        
    Parameters
    ----------    
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        simulation_years: float
            The total number of years of simulation to run for every
            configuration.  This includes both DBT or "black sky" time and
            normal operations (or "blue sky) time.  The default is 1000 years.
        powerflow_type:
            The type of powerflow calculations to do. The only options are DC
            powerflow calculations and no (NONE) calculations.  These should be
            provided as members of the pymdt.core.powerflow_types enumeration.
            The default is NONE.
        use_reliability: bool
            Whether or not to include reliability calculations in the
            simulation.  This serves as a means of telling the simulation to
            ignore reliability inputs which can be useful for comparison trials.
            The default is True.
        use_fragility: bool
            Whether or not to include fragility calculations in the simulation.
            This serves as a means of telling the simulation to ignore fragility
            inputs which can be useful for comparison trials. The default is
            True.
    """
    prmsets = ExtractPRMSettings()

    if "simulation_years" in kwargs:
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            prmsets, "SimulationYears", kwargs["simulation_years"]
            )

    powerflow = kwargs.get("powerflow_type", pymdt.core.powerflow_types.NONE)
    if hasattr(powerflow, "value"): powerflow = powerflow.value
  
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        prmsets, "PowerflowType", powerflow
        )
    
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        prmsets, "UseReliability", kwargs.get("use_reliability", True)
        )
    
    pymdt.utils.details._execute_loggable_property_set_with_undo(
        prmsets, "UseFragility", kwargs.get("use_fragility", True)
        )