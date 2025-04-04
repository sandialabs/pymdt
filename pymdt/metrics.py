from enum import Enum

import TMO
import MDT
import MDT.PRM

import pymdt.utils
    
class improvement_types(Enum):
    """ An enumeration of the improvement types used for metrics.
    """

    minimize = TMO.ImprovementType.MINIMIZE
    """ The metric is to be minimized (lower is better).
    """

    maximize = TMO.ImprovementType.MAXIMIZE
    """ The metric is to be maximized (higher is better).
    """
    
    seek_value = TMO.ImprovementType.SEEK_VALUE
    """ The specified value is sought (value is better).
    """
    
class limit_stiffnesses(Enum):
    """ An enumeration of the stiffness indicator used for metrics.
    """

    minimize = TMO.ResponseFunction.StiffnessLevel.Soft
    """ The limit is such that violation is bad but not a really big deal.
    """

    maximize = TMO.ResponseFunction.StiffnessLevel.Medium
    """ The limit is such that violation is bad and causes a significant
    detriment to fitness.
    """
    
    seek_value = TMO.ResponseFunction.StiffnessLevel.Hard
    """ The limit is such that violation is very bad and causes a major
    detriment to fitness.  In addition, this limit is treated as a hard
    constraint by the optimizer such that its satisfaction is paramount when
    comparing solution quality amongst candidate solutions.        
    """
    
class value_beyond_objective(Enum):
    """ An enumeration of the value beyond objective indicator used for metrics.
    """
    
    low = TMO.ResponseFunction.ValueBeyondObjective.Low
    """ Indicates that the rate if diminishing returns is high and therefore
    the value of exceeding the objective is low.
    """

    medium = TMO.ResponseFunction.ValueBeyondObjective.Medium
    """ Indicates that the rate if diminishing returns is moderate and therefore
    the value of exceeding the objective is moderate.
    """
    
    high = TMO.ResponseFunction.ValueBeyondObjective.High
    """ Indicates that the rate if diminishing returns is low and therefore
    the value of exceeding the objective is high.
    """

class sim_phases(Enum):
    """ An enumeration of the different phases of simulation over which metrics
    may be calculated.
    """
    
    post_startup = MDT.MicrogridLoadConstraint.PHASE_ENUM.POST_STARTUP
    """ The period of simulation that begins when the startup phase ends and
    ends when the DBT ends.  This excludes the startup phase and any periods of
    grid-tied operation.
    """

    startup = MDT.MicrogridLoadConstraint.PHASE_ENUM.STARTUP
    """ The period of simulation that begins at the onset of the DBT and ends
    when the Microgrid is ready to begin networked operation.  This excludes
    the startup phase and any periods of grid-tied operation.
    """

    overall = MDT.MicrogridLoadConstraint.PHASE_ENUM.OVERALL
    """ The period of simulation that begins at the onset of the DBT and ends
    when the DBT ends.  This includes startup and microgrid operations phases
    but excludes any periods of grid-tied operation.
    """

    n_a = MDT.MicrogridLoadConstraint.PHASE_ENUM.N_A
    """ Used in limited circumstances when it is appropriate to indicate that
    a simulation phase need or should not be provided.
    """


class details:
    
    @staticmethod
    def _extract_load_tier(m: MDT.MicrogridLoadConstraint, **kwargs):
        t = kwargs.get("tier")
        if t is None: return
        if type(t) is str:
            t = pymdt.utils.FindEntityByName(MDT.Driver.INSTANCE.LoadTiers, t)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            m, "LoadTier", t, **kwargs
            )
        
    @staticmethod
    def _extract_sim_phase(m: MDT.MicrogridLoadConstraint, **kwargs):
        p = kwargs.get("phase")
        if p is None: return
        if type(p) is str: p = sim_phases[p]
        if type(p) is sim_phases: p = p.value
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            m, "Phase", p, **kwargs
            )
        
    @staticmethod
    def _extract_improvement_type(m: TMO.Constraint, **kwargs):
        i = kwargs.get("improvement_type")
        if i is None: return
        if type(i) is str: i = improvement_types[i]
        if type(i) is improvement_types: i = i.value
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            m, "ImprovementType", i, **kwargs
            )
        
    @staticmethod
    def _extract_limit_stiffness(m: TMO.Constraint, **kwargs):
        i = kwargs.get("limit_stiffness")
        if i is None: return
        if type(i) is str: i = limit_stiffnesses[i]
        if type(i) is limit_stiffnesses: i = i.value
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            m, "SingleValueLimitStiffness", i, **kwargs
            )
        
    @staticmethod
    def _extract_value_beyond_objective(m: TMO.Constraint, **kwargs):
        i = kwargs.get("value_beyond_objective")
        if i is None: return
        if type(i) is str: i = value_beyond_objective[i]
        if type(i) is value_beyond_objective: i = i.value
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            m, "SingleValueValueBeyondObjective", i, **kwargs
            )
        
    @staticmethod
    def _extract_mission(m: MDT.SiteMissionConstraint, **kwargs):
        mn = kwargs.get("mission")
        if mn is not None:
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                m, "Mission", mn, **kwargs
                )

    @staticmethod
    def _extract_metric_params(m: TMO.Constraint, **kwargs):
        if "limit" in kwargs:
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                m, "SingleValueLimit", kwargs["limit"],
                "ChangeSingleValueResponseDataCanceled", **kwargs
                )
        if "objective" in kwargs:
            pymdt.utils.details._execute_loggable_property_set_with_undo(
                m, "SingleValueObjective", kwargs["objective"],
                "ChangeSingleValueResponseDataCanceled", **kwargs
                )
        details._extract_improvement_type(m, **kwargs)
        details._extract_limit_stiffness(m, **kwargs)
        pymdt.utils.details._execute_loggable_property_set_with_undo(
            m, "SingleValueRelativeImportance",
            kwargs.get("relative_importance", 1.0),
            "ChangeSingleValueResponseDataCanceled", **kwargs
            )
        details._extract_value_beyond_objective(m, **kwargs)

    @staticmethod
    def _set_def_imp_type(defType, kwargs):
        if "improvement_type" not in kwargs: kwargs["improvement_type"] = defType

    @staticmethod
    def build_energy_availability_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.EnergyAvailabilityConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.EnergyAvailabilityConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        details._extract_load_tier(m, **kwargs)
        details._extract_sim_phase(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_average_energy_supplied_by_renewables_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageEnergySuppliedByRenewables:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.AverageEnergySuppliedByRenewables(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_average_renewable_energy_spilled_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageRenewableEnergySpilledConstraint:
        details._set_def_imp_type(improvement_types.minmize, kwargs)
        m = MDT.PRM.AverageRenewableEnergySpilledConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_average_renewable_penetration_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageRenewablePenetrationConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.AverageRenewablePenetrationConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_average_spinning_reserve_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageSpinningReserveConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.AverageSpinningReserveConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_diesel_efficiency_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselEfficiencyConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.DieselEfficiencyConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_diesel_fuel_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselFuelConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.DieselFuelConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_diesel_fuel_cost_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselFuelCostConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.DieselFuelCostConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_diesel_utilization_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselUtilizationConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.DieselUtilizationConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_fossil_off_time_percentage_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.FossilOffTimePercentageConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.FossilOffTimePercentageConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_frequency_of_load_not_served_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.FreqOfLNSConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.FreqOfLNSConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        details._extract_load_tier(m, **kwargs)
        details._extract_sim_phase(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_heat_recovery_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.HeatRecoveryConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.HeatRecoveryConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_magnitude_of_load_not_served_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.MagOfLNSConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.MagOfLNSConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        details._extract_load_tier(m, **kwargs)
        details._extract_sim_phase(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_maximum_mission_outage_duration_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.MaximumMissionOutageDurationConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.MaximumMissionOutageDurationConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        details._extract_mission(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_natural_gas_efficiency_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasEfficiencyConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.NaturalGasEfficiencyConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_natural_gas_fuel_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasFuelConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.NaturalGasFuelConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_natural_gas_fuel_cost_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasFuelCostConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.NaturalGasFuelCostConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_natural_gas_utilization_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasUtilizationConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.NaturalGasUtilizationConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_propane_efficiency_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneEfficiencyConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.PropaneEfficiencyConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_propane_fuel_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneFuelConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.PropaneFuelConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_propane_fuel_cost_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneFuelCostConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.PropaneFuelCostConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_propane_utilization_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneUtilizationConstraint:
        details._set_def_imp_type(improvement_types.maximize, kwargs)
        m = MDT.PRM.PropaneUtilizationConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_total_fuel_cost_metric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.TotalFuelCostConstraint:
        details._set_def_imp_type(improvement_types.minimize, kwargs)
        m = MDT.PRM.TotalFuelCostConstraint(mg, name)
        pymdt.utils.details._extract_guid(m, **kwargs)
        details._extract_metric_params(m, **kwargs)
        pymdt.utils.details._extract_notes(m, **kwargs)
        return m
    
    @staticmethod
    def build_response_function_group(name: str, metrics, **kwargs) -> TMO.ResponseFunctionGroup:
        rfg = TMO.ResponseFunctionGroup(name)
        pymdt.utils.details._extract_guid(rfg, **kwargs)
        if metrics is not None:
            if not pymdt.utils.details._is_collection(metrics): metrics = [metrics]
            for m in metrics:
                pymdt.utils.details._execute_1_arg_add_with_undo(
                    rfg, "AddResponseFunctionCanceled", "get_ResponseFunctions",
                    m, **kwargs
                    )
        pymdt.utils.details._extract_notes(rfg, **kwargs)
        return rfg
    
def MakeEnergyAvailabilityMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.EnergyAvailabilityConstraint:
    """ Builds an instance of the MDT.EnergyAvailabilityConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created metric.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        phase: pymdt.metrics.sim_phases
            This parameter should be a member of the pymdt.metrics.sim_phases
            enumeration.  This indicates what phase of the simulation the new
            metric should be applied to.  See the enumeration for details.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_energy_availability_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeAverageEnergySuppliedByRenewablesMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageEnergySuppliedByRenewables:
    """ Builds an instance of the MDT.AverageEnergySuppliedByRenewables class,
    loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_average_energy_supplied_by_renewables_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeAverageRenewableEnergySpilledMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageRenewableEnergySpilledConstraint:
    """ Builds an instance of the MDT.AverageRenewableEnergySpilledConstraint
    class, loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_average_renewable_energy_spilled_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeAverageRenewablePenetrationMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageRenewablePenetrationConstraint:
    """ Builds an instance of the MDT.AverageRenewablePenetrationConstraint
    class, loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_average_renewable_penetration_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeAverageSpinningReserveMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.AverageSpinningReserveConstraint:
    """ Builds an instance of the MDT.AverageSpinningReserveConstraint class,
    loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_average_spinning_reserve_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeDieselEfficiencyMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselEfficiencyConstraint:
    """ Builds an instance of the MDT.DieselEfficiencyConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_diesel_efficiency_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeDieselFuelMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselFuelConstraint:
    """ Builds an instance of the MDT.DieselFuelConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_diesel_fuel_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeDieselFuelCostMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselFuelCostConstraint:
    """ Builds an instance of the MDT.DieselFuelCostConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_diesel_fuel_cost_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeDieselUtilizationRateMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.DieselUtilizationConstraint:
    """ Builds an instance of the MDT.DieselUtilizationConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_diesel_utilization_rate_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeFossilOffTimePercentageMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.FossilOffTimePercentageConstraint:
    """ Builds an instance of the MDT.FossilOffTimePercentageConstraint class,
    loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_fossil_off_time_percentage_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeFrequencyOfLoadNotServedMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.FreqOfLNSConstraint:
    """ Builds an instance of the MDT.FreqOfLNSConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created metric.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        phase: pymdt.metrics.sim_phases
            This parameter should be a member of the pymdt.metrics.sim_phases
            enumeration.  This indicates what phase of the simulation the new
            metric should be applied to.  See the enumeration for details.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_frequency_of_load_not_served_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeMagnitudeOfLoadNotServedMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.MagOfLNSConstraint:
    """ Builds an instance of the MDT.MagOfLNSConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        tier:
            The tier for this newly created metric.  This can be an
            MDT.LoadTier or the name of a tier in which case the actual load
            tier will be found in the master list and assigned.
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        phase: pymdt.metrics.sim_phases
            This parameter should be a member of the pymdt.metrics.sim_phases
            enumeration.  This indicates what phase of the simulation the new
            metric should be applied to.  See the enumeration for details.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_magnitude_of_load_not_served_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeHeatRecoveryMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.HeatRecoveryConstraint:
    """ Builds an instance of the MDT.HeatRecoveryConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_heat_recovery_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeMaximumMissionOutageDurationMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.MaximumMissionOutageDurationConstraint:
    """ Builds an instance of the MDT.MaximumMissionOutageDurationConstraint
    class, loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        mission: MDT.Mission
            The mission whose outage duration is to be tracked.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_maximum_mission_outage_duration_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeNaturalGasEfficiencyMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasEfficiencyConstraint:
    """ Builds an instance of the MDT.NaturalGasEfficiencyConstraint class,
    loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_natural_gas_efficiency_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeNaturalGasFuelMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasFuelConstraint:
    """ Builds an instance of the MDT.NaturalGasFuelConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_natural_gas_fuel_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeNaturalGasFuelCostMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasFuelCostConstraint:
    """ Builds an instance of the MDT.NaturalGasFuelCostConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_natural_gas_fuel_cost_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeNaturalGasUtilizationRateMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.NaturalGasUtilizationConstraint:
    """ Builds an instance of the MDT.NaturalGasUtilizationConstraint class,
    loads its properties, adds it to the microgrid (if provided), and
    returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_natural_gas_utilization_rate_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakePropaneEfficiencyMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneEfficiencyConstraint:
    """ Builds an instance of the MDT.PropaneEfficiencyConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_propane_efficiency_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakePropaneFuelMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneFuelConstraint:
    """ Builds an instance of the MDT.PropaneFuelConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_propane_fuel_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakePropaneFuelCostMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneFuelCostConstraint:
    """ Builds an instance of the MDT.PropaneFuelCostConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_propane_fuel_cost_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakePropaneUtilizationRateMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.PropaneUtilizationConstraint:
    """ Builds an instance of the MDT.PropaneUtilizationConstraint class, loads
    its properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is maximize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_propane_utilization_rate_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeTotalFuelCostMetric(mg: MDT.Microgrid, name: str, **kwargs) -> MDT.PRM.TotalFuelCostConstraint:
    """ Builds an instance of the MDT.TotalFuelCostConstraint class, loads its
    properties, adds it to the microgrid (if provided), and returns it.
        
    Parameters
    ----------
    mg: MDT.Microgrid
        The microgrid to which to add the new metric.  If this argument is None,
        then the metric is created and loaded but not added to any entities
        metric list.  That will have to happen later.        
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        improvement_type: pymdt.metrics.improvement_types
            A member of the pymdt.metrics.improvement_types enumeration
            indicating the desired improvement direction of the new metric.  The
            default improvement type for this metric type is minimize.
        limit: float
            The worst acceptable value for this metric.  This defines the
            boundary between acceptable and not acceptable. This is required.
        objective: float
            The desired value for this metric.  This is a value that, if
            achieved, provides full satisfaction.  Achieving values better than
            the objective may still provide benefit but at a diminishing rate of
            return.  This is required.
        limit_stiffness: pymdt.metrics.limit_stiffnesses
            A member of the pymdt.metrics.limit_stiffnesses enumeration
            indicating the desired strength of the limit for the new metric.
            The default stiffness for this metric type is medium.
        relative_importance: float
            The desired weight of this metric in trade-offs that occur.  It is
            advised that you not use this parameter unless absolutely necessary.
            Instead, the limit and objective values should be the primary means
            by which a metric is valued.  Using the relative_importance may not
            provide the results expected.  The default value for this is 1.0.
        value_beyond_objective: pymdt.metrics.value_beyond_objective
            A member of the pymdt.metrics.value_beyond_objective enumeration,
            this parameter controls the rate of diminishing returns for
            exceeding (doing better than) the objective for a configuration.
            the lower the VBO, the faster the rate of diminishing returns.
            The default for this is medium.
        owner:
            An optional parameter to serve as the owner of the new metric.  This
            is typically used if one does not want the metric added to the
            microgrid as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied microgrid
            (mg) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    m = details.build_total_fuel_cost_metric(mg, name, **kwargs)
    owner = pymdt.core.details._extract_owner(mg, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddConstraintCanceled", "get_Constraints", m, **kwargs
            )
    return m

def MakeResponseFunctionGroup(s: TMO.SolverInterface, name: str, metrics, **kwargs) -> TMO.ResponseFunctionGroup:
    """ Builds an instance of a TMO.ResponseFunctionGroup class, loads its
    properties, adds it to the solver (if provided), and returns it.
        
    Parameters
    ----------
    s: TMO.SolverInterface
        The solver to which to add the new group.  If this argument is None,
        then the group is created and loaded but not added to any solvers group
        list.  That will have to happen later.
    name: str
        The name for the new response function group.  This must be unique
        within the supplied solver.
    metrics: collection of TMO.Constraint
        The list of metrics to be included in this group.  Additional metrics
        can be added directly to the group afterwards if desired.
    kwargs: dict
        A dictionary of all the variable arguments provided to this function.
        The arguments used by this method include:
        
        owner:
            An optional parameter to serve as the owner of the new group.  This
            is typically used if one does not want the group added to the
            solver as part of this call in which case None is specified as
            the owner.  If no owner is provided, then the supplied solver
            (s) is used.
        err_log: Common.Logging.Log
            The log into which to record any errors encountered during the
            building, loading, or saving of the new specification.  If this
            argument is not provided, messages will be recorded into the
            pymdt.GlobalErrorLog instance.
        undos: Common.Undoing.IUndoPack
            An optional undo pack into which to load the undoable objects
            generated during this operation (if any).
        notes: str
            Any notes to assign to the resulting metric. Not required.
        guid:
            The unique identifier to use for this new asset.  This can be
            a string formatted as described in:
            https://learn.microsoft.com/en-us/dotnet/api/system.guid.-ctor?view=net-8.0#system-guid-ctor(system-string)
            or a System.Guid instance.  If not provided, a newly created,
            random Guid is used.
    """
    rfg = details.build_response_function_group(name, metrics, **kwargs)
    owner = pymdt.core.details._extract_owner(s, **kwargs)
    if owner is not None:
        pymdt.utils.details._execute_1_arg_add_with_undo(
            owner, "AddResponseFunctionGroupCanceled",
            "get_ResponseFunctionGroups", rfg, **kwargs
            )
    return rfg
