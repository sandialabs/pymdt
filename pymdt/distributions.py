import MDT
import Common
import Common.Distributions as CD

def MakeExponential(mean: float, location: float=0.0) -> CD.Exponential:
    """ Creates, configures, and returns a new instance of an Exponential
    distribution using the supplied parameters.
        
    Parameters
    ----------
    mean: float
        The mean of the new exponential distribution which is the inverse of the
        more common "lambda" parameter.
    location: float
        An optional parameter that shifts the distribution along the x-axis.
        
    Returns
    -------
    Common.Distributions.Exponential:
        The newly created and configured Exponential distribution.
    """
    return CD.Exponential(1.0/mean, location)

def MakeNormal(mean: float=0.0, std_dev: float=1.0) -> CD.Normal:
    """ Creates, configures, and returns a new instance of a Normal distribution
    using the supplied parameters.
        
    Parameters
    ----------
    mean: float
        The mean of the new Normal distribution.
    std_dev: float
        The standard deviation of the newly created Normal distribution.
        
    Returns
    -------
    Common.Distributions.Normal:
        The newly created and configured Normal distribution.
    """
    return CD.Normal(mean, std_dev)

def MakeUniform(lower: float=0.0, upper: float=1.0) -> CD.Uniform:
    """ Creates, configures, and returns a new instance of a Uniform
    distribution using the supplied parameters.
        
    Parameters
    ----------
    lower: float
        The lower value of the new Uniform distribution.
    upper: float
        The upper value of the new Uniform distribution.
        
    Returns
    -------
    Common.Distributions.Uniform:
        The newly created and configured Uniform distribution.
    """
    return CD.Uniform(lower, upper)

def MakeFixed(value: float=0.0) -> CD.Fixed:
    """ Creates, configures, and returns a new instance of a Fixed
    distribution using the supplied parameters.
        
    Parameters
    ----------
    value: float
        The fixed value of the new Fixed distribution.
        
    Returns
    -------
    Common.Distributions.Fixed:
        The newly created and configured Fixed distribution.
    """
    return CD.Fixed(value)

def MakeLogNormal(location: float=0.0, scale: float=1.0) -> CD.LogNormal:
    """ Creates, configures, and returns a new instance of a LogNormal
    distribution using the supplied parameters.
        
    Parameters
    ----------
    location: float
        The location value of the new LogNormal distribution.  This is
        equivalent to the mean of the logarithm of the random variable.
    scale: float
        The scale value of the new LogNormal distribution.  This is equivalent
        to the standard deviation of the logarithm of the random variable.
        
    Returns
    -------
    Common.Distributions.LogNormal:
        The newly created and configured LogNormal distribution.
    """
    return CD.LogNormal(location, scale)

def MakeCauchy(location: float=0.0, scale: float=1.0) -> CD.Cauchy:
    """ Creates, configures, and returns a new instance of a Cauchy
    distribution using the supplied parameters.
        
    Parameters
    ----------
    location: float
        The location value of the new Cauchy distribution.
    scale: float
        The scale value of the new Cauchy distribution.
        
    Returns
    -------
    Common.Distributions.Cauchy:
        The newly created and configured Cauchy distribution.
    """
    return CD.Cauchy(location, scale)

def MakeBinomial(trials: float=1.0, success_fraction: float=0.5) -> CD.Binomial:
    """ Creates, configures, and returns a new instance of a Binomial
    distribution using the supplied parameters.
        
    Parameters
    ----------
    trials: float
        The trials value of the new Binomial distribution.
    success_fraction: float
        The success fraction value of the new Binomial distribution.
        
    Returns
    -------
    Common.Distributions.Binomial:
        The newly created and configured Binomial distribution.
    """
    return CD.Binomial(trials, success_fraction)

def MakeBernoulli(success_fraction: float=0.5) -> CD.Bernoulli:
    """ Creates, configures, and returns a new instance of a Bernoulli
    distribution using the supplied parameters.
        
    Parameters
    ----------
    success_fraction: float
        The success fraction value of the new Bernoulli distribution.
        
    Returns
    -------
    Common.Distributions.Bernoulli:
        The newly created and configured Bernoulli distribution.
    """
    return CD.Bernoulli(success_fraction)

def MakeGamma(shape: float, scale: float=1.0) -> CD.Gamma:
    """ Creates, configures, and returns a new instance of a Gamma
    distribution using the supplied parameters.
        
    Parameters
    ----------
    shape: float
        The shape value of the new Gamma distribution.
    scale: float
        The scale value of the new Gamma distribution.
        
    Returns
    -------
    Common.Distributions.Gamma:
        The newly created and configured Gamma distribution.
    """
    return CD.Gamma(shape, scale)

def MakePoisson(mean: float=1.0) -> CD.Poisson:
    """ Creates, configures, and returns a new instance of a Poisson
    distribution using the supplied parameters.
        
    Parameters
    ----------
    mean: float
        The mean value of the new Poisson distribution.
        
    Returns
    -------
    Common.Distributions.Poisson:
        The newly created and configured Poisson distribution.
    """
    return CD.Poisson(mean)

def MakeTriangular(lower: float=-1.0, mode: float=0.0, upper: float=1.0) -> CD.Triangular:
    """ Creates, configures, and returns a new instance of a Triangular
    distribution using the supplied parameters.
        
    Parameters
    ----------
    lower: float
        The lower value of the new Triangular distribution.
    mode: float
        The mode of the new Triangular distribution.
    upper: float
        The upper value of the new Triangular distribution.
        
    Returns
    -------
    Common.Distributions.Triangular:
        The newly created and configured Triangular distribution.
    """
    return CD.Triangular(lower, mode, upper)

def MakeDiscrete(entries) -> MDT.Discrete:
    """ Creates, configures, and returns a new instance of a Discrete
    distribution using the supplied parameters.
        
    Parameters
    ----------
    entries
        Can be a 2-tuple of a singular entry (value, probability) or a
        dictionary of multiple entries of the form {value1: probability1, ...}.
        
    Returns
    -------
    MDT.Discrete:
        The newly created and configured Discrete distribution.
    """
    d = MDT.Discrete()
    ents = d.get_Entries()
    undos = Common.Undoing.UndoPack()
    if type(entries) is tuple:
        entries = {entries(0): entries(1)}
    elif type(entries) is not dict:
        entries = {entries}
    for ent in entries.items():
        ents.Add(MDT.DiscreteEntry(ent[0], ent[1]), undos)
    return d
         
def MakePlacement(init_dist: CD.IDistribution, subseq_dist: CD.IDistribution) -> MDT.PlacementDistribution:
    """ Creates, configures, and returns a new instance of a Placement
    distribution using the supplied parameters.
        
    Parameters
    ----------
    init_dist: CD.IDistribution
        The distribution used to draw the first value produced.
    subseq_dist: CD.IDistribution
        The distribution used to draw all subsequent values produced.
        
    Returns
    -------
    MDT.PlacementDistribution:
        The newly created and configured Placement distribution.
    """
    return MDT.PlacementDistribution(init_dist, subseq_dist)

def MakeTimeOfYearBiased(basis_dist: CD.IDistribution, time_of_year_dist: CD.IDistribution) -> MDT.TimeOfYearBiasDistribution:
    """ Creates, configures, and returns a new instance of a Time-of-Year Biased
    distribution using the supplied parameters.
        
    Parameters
    ----------
    basis_dist: CD.IDistribution
        The distribution used to draw number of years between occurrences.
    time_of_year_dist: CD.IDistribution
        The distribution used to draw the time of year of the occurrence in
        hours.
        
    Returns
    -------
    MDT.TimeOfYearBiasDistribution:
        The newly created and configured Time-of-Year Biased distribution.
    """
    return MDT.TimeOfYearBiasDistribution(basis_dist, time_of_year_dist)
