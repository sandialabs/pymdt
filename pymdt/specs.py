import System

import pymdt.utils

import MDT
import Common

class details:
    
    @staticmethod
    def _extract_battery_spec_efficiency_values(bat_spec, **kwargs):
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()
        maxlen = bat_spec.NumberOfEfficiencyValues
        ceff_vals = kwargs.get("charge_efficiencies")
        if ceff_vals is not None:
            ceffs = bat_spec.get_ChargeEfficiencies()
            for i in range(min(len(ceff_vals), maxlen)):
                ceffs.set_Item(i, undos, ceff_vals[i])
        
        deff_vals = kwargs.get("discharge_efficiencies")
        if deff_vals is not None:
            deffs = bat_spec.get_DischargeEfficiencies()
            for i in range(min(len(deff_vals), maxlen)):
                deffs.set_Item(i, undos, deff_vals[i])
                
    @staticmethod
    def _extract_gen_spec_perf_values(gen_spec, **kwargs):
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()
        maxlen = gen_spec.NumberOfPerformanceValues
        eff_vals = kwargs.get("efficiencies")
        if eff_vals is not None:
            effs = gen_spec.get_EfficiencyValues()
            for i in range(min(len(eff_vals), maxlen)):
                effs.set_Item(i, undos, eff_vals[i])
        
        fuse_vals = kwargs.get("fuel_usages")
        if fuse_vals is not None:
            fuses = gen_spec.get_EfficiencyValues()
            for i in range(min(len(fuse_vals), maxlen)):
                fuses.set_Item(i, undos, fuse_vals[i])
                
    @staticmethod
    def _extract_gen_start_probabilities(gen_spec, **kwargs):
        # Don't use kwargs.get to avoid creation of the UndoPack if not needed.
        undos = kwargs["undos"] if "undos" in kwargs else Common.Undoing.UndoPack()
        st_probs = kwargs.get("start_probabilities")
        if st_probs is not None:
            probs = gen_spec.get_StartProbabilities()
            for i in range(len(st_probs)):
                probs.Add(st_probs[i], undos)
        
    @staticmethod
    def _extract_fossil_gen_spec_props(gen_spec, capacity: float, **kwargs):
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            gen_spec, "Capacity", capacity, **kwargs
            )
        pymdt.utils.details._extract_voltage(gen_spec, **kwargs)
        details._extract_gen_spec_perf_values(gen_spec, **kwargs)
        details._extract_gen_start_probabilities(gen_spec, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            gen_spec, "StartFailureMTTR", kwargs.get("startup_mttr"), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            gen_spec, "StartupTime", kwargs.get("startup_time", 10/3600.0),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            gen_spec, "RecoverableHeatRate",
            kwargs.get("recoverable_heat_rate", 0.0), **kwargs
            )

    @staticmethod
    def _set_basic_spec_props(
        spec: MDT.Specification, name: str, capital_cost: float,
        op_cost: float=0.0, weight: float=0.0, volume: float=0.0, **kwargs
        ):
        
        pymdt.utils.details._extract_notes(spec, **kwargs)
        pymdt.utils.details._extract_failure_modes(spec, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Cost", System.Decimal(capital_cost), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "OperationalCost", System.Decimal(op_cost), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Weight", weight, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Volume", volume, **kwargs
            )
                    
    @staticmethod
    def build_line_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.LineSpec:
        
        spec = MDT.LineSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._extract_impedance(spec, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        return spec
    
    @staticmethod
    def build_switch_spec(
        name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
        volume: float=0.0, **kwargs
        ) -> MDT.SwitchSpec:
        
        spec = MDT.SwitchSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._extract_impedance(spec, **kwargs)
        return spec
    
    @staticmethod
    def build_transformer_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.TransformerSpec:
        
        spec = MDT.TransformerSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._extract_impedance(spec, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        return spec
    
    @staticmethod
    def build_diesel_tank_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.DieselTankSpec:
        
        spec = MDT.DieselTankSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        return spec
    
    @staticmethod
    def build_propane_tank_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.PropaneTankSpec:
        
        spec = MDT.PropaneTankSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        return spec
    
    @staticmethod
    def build_solar_generator_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.SolarGeneratorSpec:
        
        spec = MDT.SolarGeneratorSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        pymdt.utils.details._extract_voltage(spec, **kwargs)
        return spec
    
    @staticmethod
    def build_wind_generator_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.WindGeneratorSpec:
        
        spec = MDT.WindGeneratorSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        pymdt.utils.details._extract_voltage(spec, **kwargs)
        return spec
    
    @staticmethod
    def build_hydro_generator_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.HydroGeneratorSpec:
        
        spec = MDT.HydroGeneratorSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "Capacity", capacity, **kwargs
            )
        pymdt.utils.details._extract_voltage(spec, **kwargs)
        return spec
    
    @staticmethod
    def build_inverter_spec(
        name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
        volume: float=0.0, **kwargs
        ) -> MDT.InverterSpec:
        
        spec = MDT.InverterSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        return spec
    
    @staticmethod
    def build_battery_spec(
        name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
        volume: float=0.0, **kwargs
        ) -> MDT.BatterySpec:
        
        spec = MDT.BatterySpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._extract_voltage(spec, **kwargs)
        details._extract_battery_spec_efficiency_values(spec, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MaxChargeRate", kwargs.get("max_charge_rate", 0.0), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MaxDischargeRate", kwargs.get("max_discharge_rate", 0.0),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "EnergyCapacity", kwargs.get("energy_capacity", 0.0), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MinStateOfCharge", kwargs.get("min_state_of_charge", 0.1),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MaxStateOfCharge", kwargs.get("max_state_of_charge", 0.9),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "DesiredStateOfCharge",
            kwargs.get("desired_state_of_charge", 0.7), **kwargs
            )
        return spec
    
    @staticmethod
    def build_ups_spec(
        name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
        volume: float=0.0, **kwargs
        ) -> MDT.UPSSpec:
        
        spec = MDT.UPSSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        pymdt.utils.details._extract_voltage(spec, **kwargs)
        details._extract_battery_spec_efficiency_values(spec, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MaxChargeRate", kwargs.get("max_charge_rate", 0.0), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MaxDischargeRate", kwargs.get("max_discharge_rate", 0.0),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "EnergyCapacity", kwargs.get("energy_capacity", 0.0), **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MinStateOfCharge", kwargs.get("min_state_of_charge", 10.0),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "MaxStateOfCharge", kwargs.get("max_state_of_charge", 90.0),
            **kwargs
            )
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            spec, "DesiredStateOfCharge",
            kwargs.get("desired_state_of_charge", 90.0), **kwargs
            )
        return spec
    
    @staticmethod
    def build_diesel_generator_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.DieselGeneratorSpec:
        
        spec = MDT.DieselGeneratorSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        details._extract_fossil_gen_spec_props(spec, capacity, **kwargs)
        return spec
    
    @staticmethod
    def build_propane_generator_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.PropaneGeneratorSpec:
        
        spec = MDT.PropaneGeneratorSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        details._extract_fossil_gen_spec_props(spec, capacity, **kwargs)
        return spec
    
    @staticmethod
    def build_nat_gas_generator_spec(
        name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
        weight: float=0.0, volume: float=0.0, **kwargs
        ) -> MDT.NaturalGasGeneratorSpec:
        
        spec = MDT.NaturalGasGeneratorSpec(name)
        pymdt.utils.details._extract_guid(spec, **kwargs)
        details._set_basic_spec_props(
            spec, name, capital_cost, op_cost, weight, volume, **kwargs
            )
        details._extract_fossil_gen_spec_props(spec, capacity, **kwargs)
        return spec
    
    def _execute_spec_add(specType, spec, **kwargs) -> Common.Logging.Log:
        hndlrName = "Add" + specType + "SpecificationCanceled"
        specLstName = "get_" + specType + "Specifications"
        return pymdt.utils.details._execute_1_arg_add_with_undo(
            MDT.Driver.INSTANCE, hndlrName, specLstName, spec, **kwargs
            )

def MakeLineSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.LineSpec:
    """ This helper function creates a new LineSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The capacity of this component type to carry power (in kW).
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs/ft of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        impedance
            A 2 element tuple or a list with 2 items in it where the first is
            the resistance part and the second is the reactance.
        resistance: float
            The resistance component of impedance.  Only used if the "impedance"
            keyword argument is not provided.
        reactance: float
            The reactance component of impedance.  Only used if the "impedance"
            keyword argument is not provided.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.LineSpec:
        The newly created specification instance.
    """
    spec = details.build_line_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("Line", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeSwitchSpecification(
    name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
    volume: float=0.0, **kwargs
    ) -> MDT.SwitchSpec:
    """ This helper function creates a new SwitchSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        impedance
            A 2 element tuple or a list with 2 items in it where the first is
            the resistance part and the second is the reactance.
        resistance: float
            The resistance component of impedance.  Only used if the "impedance"
            keyword argument is not provided.
        reactance: float
            The reactance component of impedance.  Only used if the "impedance"
            keyword argument is not provided.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.SwitchSpec:
        The newly created specification instance.
    """
    spec = details.build_switch_spec(
        name, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("Switch", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeTransformerSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.TransformerSpec:
    """ This helper function creates a new TransformerSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The capacity of this component type to carry power (in kW).
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        impedance
            A 2 element tuple or a list with 2 items in it where the first is
            the resistance part and the second is the reactance.
        resistance: float
            The resistance component of impedance.  Only used if the "impedance"
            keyword argument is not provided.
        reactance: float
            The reactance component of impedance.  Only used if the "impedance"
            keyword argument is not provided.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.TransformerSpec:
        The newly created specification instance.
    """
    spec = details.build_transformer_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("Transformer", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeDieselTankSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.DieselTankSpec:
    """ This helper function creates a new DieselTankSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The capacity of this tank to hold fuel (in gallons).
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.DieselTankSpec:
        The newly created specification instance.
    """
    spec = details.build_diesel_tank_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("DieselTank", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakePropaneTankSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.PropaneTankSpec:
    """ This helper function creates a new PropaneTankSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The capacity of this tank to hold fuel (in gallons).
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.PropaneTankSpec:
        The newly created specification instance.
    """
    spec = details.build_propane_tank_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("PropaneTank", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeDieselGeneratorSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.DieselGeneratorSpec:
    """ This helper function creates a new DieselGeneratorSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The maximum output power this generator can produce (in kW).
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        efficiencies: [float]
            A list of 5 efficiency values, 1 each for this generator running at
            0% (idle), 25%, 50%, 75%, and 100% running rate.  The units of
            efficiency are fraction (0.0-1.0).
        fuel_usages: [float]
            A list of 5 fuel use values, 1 each for this generator running at
            0% (idle), 25%, 50%, 75%, and 100% running rate.  The units of
            efficiency during idling are gallons per hour.  The units of the
            other rates is gallon per kW per hour.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        start_probabilities: [float]
            A list of 1 or more startup probability values as fractions
            (0.0-1.0).  The first is the likelihood of a generator starting on
            the first attempt.  Each subsequent value corresponds to the
            likelihood of the generator starting on subsequent attempts.  The
            number of items in the list defines the maximum number of start
            attempts allowed before the generator is considered to have suffered
            startup failure.
        startup_mttr: Common.Distributions.IDistribution
            The distribution used to determine the time required to repair a
            startup failure for this generator.  If no startup MTTR distribution
            is provided, then the generator cannot be repaired during the DBT
            occurrence.
        startup_time: float
            The amount of time required to start this generator and warm it up
            to the point that it can begin to carry load in hours.
        recoverable_heat_rate: float
            An indicator of how much heat energy can be extracted from this
            generator as a function of it's electrical output as a fraction
            (0.0-1.0).  The fraction represents the number of kWh of heat per
            kWh of electrical energy that can be extracted.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.DieselGeneratorSpec:
        The newly created specification instance.
    """
    spec = details.build_diesel_generator_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("DieselGenerator", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakePropaneGeneratorSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.PropaneGeneratorSpec:
    """ This helper function creates a new PropaneGeneratorSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The maximum output power this generator can produce (in kW).
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        efficiencies: [float]
            A list of 5 efficiency values, 1 each for this generator running at
            0% (idle), 25%, 50%, 75%, and 100% running rate.  The units of
            efficiency are fraction (0.0-1.0).
        fuel_usages: [float]
            A list of 5 fuel use values, 1 each for this generator running at
            0% (idle), 25%, 50%, 75%, and 100% running rate.  The units of
            efficiency during idling are gallons per hour.  The units of the
            other rates is gallon per kW per hour.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        start_probabilities: [float]
            A list of 1 or more startup probability values as fractions
            (0.0-1.0).  The first is the likelihood of a generator starting on
            the first attempt.  Each subsequent value corresponds to the
            likelihood of the generator starting on subsequent attempts.  The
            number of items in the list defines the maximum number of start
            attempts allowed before the generator is considered to have suffered
            startup failure.
        startup_mttr: Common.Distributions.IDistribution
            The distribution used to determine the time required to repair a
            startup failure for this generator.  If no startup MTTR distribution
            is provided, then the generator cannot be repaired during the DBT
            occurrence.
        startup_time: float
            The amount of time required to start this generator and warm it up
            to the point that it can begin to carry load in hours.
        recoverable_heat_rate: float
            An indicator of how much heat energy can be extracted from this
            generator as a function of it's electrical output as a fraction
            (0.0-1.0).  The fraction represents the number of kWh of heat per
            kWh of electrical energy that can be extracted.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.PropaneGeneratorSpec:
        The newly created specification instance.
    """
    spec = details.build_propane_generator_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("PropaneGenerator", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeNaturalGasGeneratorSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.NaturalGasGeneratorSpec:
    """ This helper function creates a new NaturalGasGeneratorSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The maximum output power this generator can produce (in kW).
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        efficiencies: [float]
            A list of 5 efficiency values, 1 each for this generator running at
            0% (idle), 25%, 50%, 75%, and 100% running rate.  The units of
            efficiency are fraction (0.0-1.0).
        fuel_usages: [float]
            A list of 5 fuel use values, 1 each for this generator running at
            0% (idle), 25%, 50%, 75%, and 100% running rate.  The units of
            efficiency during idling are MMBTUs per hour.  The units of the
            other rates is MMBTU per kW per hour.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        start_probabilities: [float]
            A list of 1 or more startup probability values as fractions
            (0.0-1.0).  The first is the likelihood of a generator starting on
            the first attempt.  Each subsequent value corresponds to the
            likelihood of the generator starting on subsequent attempts.  The
            number of items in the list defines the maximum number of start
            attempts allowed before the generator is considered to have suffered
            startup failure.
        startup_mttr: Common.Distributions.IDistribution
            The distribution used to determine the time required to repair a
            startup failure for this generator.  If no startup MTTR distribution
            is provided, then the generator cannot be repaired during the DBT
            occurrence.
        startup_time: float
            The amount of time required to start this generator and warm it up
            to the point that it can begin to carry load in hours.
        recoverable_heat_rate: float
            An indicator of how much heat energy can be extracted from this
            generator as a function of it's electrical output as a fraction
            (0.0-1.0).  The fraction represents the number of kWh of heat per
            kWh of electrical energy that can be extracted.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.NaturalGasGeneratorSpec:
        The newly created specification instance.
    """    
    spec = details.build_nat_gas_generator_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("NaturalGasGenerator", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeSolarGeneratorSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.SolarGeneratorSpec:
    """ This helper function creates a new SolarGeneratorSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The maximum output power this generator can produce (in kW).
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs/ft of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.SolarGeneratorSpec:
        The newly created specification instance.
    """
    spec = details.build_solar_generator_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("SolarGenerator", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeWindGeneratorSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.WindGeneratorSpec:
    """ This helper function creates a new WindGeneratorSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The maximum output power this generator can produce (in kW).
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs/ft of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.WindGeneratorSpec:
        The newly created specification instance.
    """
    spec = details.build_wind_generator_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("WindGenerator", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeHydroGeneratorSpecification(
    name: str, capacity: float, capital_cost: float, op_cost: float=0.0,
    weight: float=0.0, volume: float=0.0, **kwargs
    ) -> MDT.HydroGeneratorSpec:
    """ This helper function creates a new HydroGeneratorSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capacity: float
        The maximum output power this generator can produce (in kW).
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs/ft of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.HydroGeneratorSpec:
        The newly created specification instance.
    """
    spec = details.build_hydro_generator_spec(
        name, capacity, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("HydroGenerator", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeInverterSpecification(
    name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
    volume: float=0.0, **kwargs
    ) -> MDT.InverterSpec:
    """ This helper function creates a new InverterSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capital_cost: float
        The cost per foot for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs/ft of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        failure_modes:
            A list of all defined failure modes for the resulting specification,
            if any. The elements of the list are of type MDT.FailureMode.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.InverterSpec:
        The newly created specification instance.
    """
    spec = details.build_inverter_spec(
        name, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("Inverter", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeBatterySpecification(
    name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
    volume: float=0.0, **kwargs
    ) -> MDT.BatterySpec:
    """ This helper function creates a new BatterySpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        charge_efficiencies: [float]
            A list of 5 charging efficiency values, 1 each for this battery at
            0%, 25%, 50%, 75%, and 100% state of charge.  The units of
            efficiency are fraction (0.0-1.0).
        discharge_efficiencies: [float]
            A list of 5 discharging efficiency values, 1 each for this battery
            at 0%, 25%, 50%, 75%, and 100% state of charge.  The units of
            efficiency are fraction (0.0-1.0).
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        max_charge_rate: float
            The maximum rate at which power can be pushed into the battery in
            kW.
        max_discharge_rate: float
            The maximum rate at which power can be extracted from the battery in
            kW.
        energy_capacity: float
            The maximum number of kWh that can be stored in this battery
            (at 100% state of charge).
        min_state_of_charge: float
            The minimum allowable state of charge of the battery in %.  The
            default is 10%.
        max_state_of_charge: float
            The maximum allowable state of charge of the battery in %.  The
            default is 90%.
        desired_state_of_charge: float
            The desired state of charge of the battery in %.  The default is
            70%.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.BatterySpec:
        The newly created specification instance.
    """
    spec = details.build_battery_spec(
        name, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("Battery", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def MakeUPSSpecification(
    name: str, capital_cost: float, op_cost: float=0.0, weight: float=0.0,
    volume: float=0.0, **kwargs
    ) -> MDT.UPSSpec:
    """ This helper function creates a new UPSSpec, extracts any
    provided properties, loads it into the master list of specifications,
    and returns it.
        
    Parameters
    ----------
    name: str
        The name to be given to the new specification.  Names of like-type
        specifications must be unique.
    capital_cost: float
        The cost for this component type.
    op_cost: float
        The cost per hour of operation of this type of component.
    weight: float
        The weight in lbs of this component type.
    volume: float
        The physical volume in cubic feet of this component type.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        charge_efficiencies: [float]
            A list of 5 charging efficiency values, 1 each for this UPS at
            0%, 25%, 50%, 75%, and 100% state of charge.  The units of
            efficiency are fraction (0.0-1.0).
        discharge_efficiencies: [float]
            A list of 5 discharging efficiency values, 1 each for this UPS
            at 0%, 25%, 50%, 75%, and 100% state of charge.  The units of
            efficiency are fraction (0.0-1.0).
        voltage
            A 2 element tuple or a list with 2 items in it where the first is
            the real part and the second is the imaginary.
        real: float
            The real component of voltage.  Only used if the "voltage" keyword
            argument is not provided.
        imaginary: float
            The imaginary component of voltage.  Only used if the "voltage"
            keyword argument is not provided.
        max_charge_rate: float
            The maximum rate at which power can be pushed into the UPS in kW.
        max_discharge_rate: float
            The maximum rate at which power can be extracted from the UPS in kW.
        energy_capacity: float
            The maximum number of kWh that can be stored in this UPS
            (at 100% state of charge).
        min_state_of_charge: float
            The minimum allowable state of charge of the UPS in %.  The default
            is 10%.
        max_state_of_charge: float
            The maximum allowable state of charge of the UPS in %.  The default
            is 90%.
        desired_state_of_charge: float
            The desired state of charge of the UPS in %.  The default is 70%.
        sync: bool
            Whether or not to save the newly created spec to the specification
            database.  This can be done later using the
            SaveSpecificationDatabase method.  The default is to save the change
            (True).
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting specification.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
        
    Returns
    -------
    MDT.UPSSpec:
        The newly created specification instance.
    """
    spec = details.build_ups_spec(
        name, capital_cost, op_cost, weight, volume, **kwargs
        )
    errLog = details._execute_spec_add("UPS", spec, **kwargs)
    if(kwargs.get("sync", True)): SaveSpecificationDatabase(errLog)
    return spec

def SaveSpecificationDatabase(errLog: Common.Logging.Log=None) -> Common.Logging.Log:
    """ A helper function to store any new, deleted, or changed specifications
    to the underlying database.
        
    Without calling this function, any changes made will not be saved for
    use in the future. 
        
    Parameters
    ----------
    errLog: Common.Logging.Log
        A log that will receive any messages produced while saving the database
        changes and additions. If this parameter is None, then the
        pymdt.GlobalErrorLog will be used.
        
    Returns
    -------
    Common.Logging.Log:
        A log containing any errors or messages creating during the
        synchronization operation.  If the errLog parameter is None, then the
        pymdt.GlobalErrorLog will be used and returned.
    """
    MDT.Driver.INSTANCE.SynchronizeSpecificationsDB(
        errLog or pymdt.GlobalErrorLog
        )