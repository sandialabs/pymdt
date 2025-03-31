import System
import Common.Logging
from System import Exception as SYSEX

import MDT

import pymdt.utils

class details:

    @staticmethod
    def execute_configured_solver(rInfo: MDT.SolverRunInfo):
        MDT.PRM.PRMEvaluator.INSTANCE.ResetNativePRM(rInfo.PRMSettings, 0)
        MDT.Driver.INSTANCE.get_SolverRunInfos().Add(rInfo)
        rvm = MDT.ResultViewManager()
        rvm.get_SolverRunInfos().Add(rInfo)
        MDT.Driver.INSTANCE.get_ResultViewManagers().Add(rvm)
        
        solver = rInfo.Solver
    
        runLog = Common.Logging.Log()
        try:
            solver.Setup(runLog)
            solver.Run(runLog)
            solver.TakeDown(runLog)
        except SYSEX as e:
            runLog.AddEntry(Common.Logging.LogCategories.Error, str(e))
        except BaseException as e:
            runLog.AddEntry(Common.Logging.LogCategories.Error, str(e))
        except:
            runLog.AddEntry(
                Common.Logging.LogCategories.Error,
                "Caught an unknown exception."
                )
        
        return rInfo, runLog

def MakeParameterStudySolver(psConfig: MDT.ParameterStudyConfig, **kwargs) -> MDT.ParameterStudySolver:
    drv = MDT.Driver.INSTANCE    
    drv.ParameterStudyConfig = psConfig
    drv.ParameterStudySolver = MDT.ParameterStudySolver(drv.Site, psConfig)
    pymdt.utils.details._extract_guid(drv.ParameterStudySolver, **kwargs)
    drv.ParameterStudySolver.CopyResponseGroups(drv.Solver)
    drv.ParameterStudySolver.Evaluator = drv.Solver.Evaluator.Clone(False)
    drv.ParameterStudySolver.FitnessAssessor = \
        drv.Solver.FitnessAssessor.Clone(False)
    return drv.ParameterStudySolver

def RunIslandedSolver() -> tuple[MDT.SolverRunInfo, Common.Logging.Log]:
    rInfo = MDT.Driver.INSTANCE.GetCurrentRunInfo(
        MDT.Driver.AnalysisTypeEnum.ISLANDED
        )
    return details.execute_configured_solver(rInfo)
        