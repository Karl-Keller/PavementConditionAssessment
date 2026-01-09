"""
ASTM D6433 Pavement Condition Index Calculator

Main calculation engine implementing the standard PCI methodology.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

from distresses import (
    DistressType, DistressObservation, Severity,
    ASPHALT_DISTRESSES, get_distress_by_id
)
from curves import (
    DeductCurve, CDVCurve, 
    EXAMPLE_DEDUCT_CURVES, EXAMPLE_CDV_CURVES
)


class PCIRating(Enum):
    """PCI condition rating categories per ASTM D6433"""
    GOOD = "Good"
    SATISFACTORY = "Satisfactory"
    FAIR = "Fair"
    POOR = "Poor"
    VERY_POOR = "Very Poor"
    SERIOUS = "Serious"
    FAILED = "Failed"


def get_pci_rating(pci: float) -> PCIRating:
    """
    Convert numeric PCI to condition rating.
    
    Args:
        pci: Pavement Condition Index (0-100)
        
    Returns:
        PCIRating enum value
    """
    if pci >= 85:
        return PCIRating.GOOD
    elif pci >= 70:
        return PCIRating.SATISFACTORY
    elif pci >= 55:
        return PCIRating.FAIR
    elif pci >= 40:
        return PCIRating.POOR
    elif pci >= 25:
        return PCIRating.VERY_POOR
    elif pci >= 10:
        return PCIRating.SERIOUS
    else:
        return PCIRating.FAILED


@dataclass
class PCIResult:
    """Result of a PCI calculation"""
    pci: float
    rating: PCIRating
    deduct_values: List[float]
    max_cdv: float
    iteration_cdvs: List[float]  # CDVs from each iteration


class PCICalculator:
    """
    Calculator for Pavement Condition Index per ASTM D6433.
    
    Usage:
        calculator = PCICalculator()
        # Load actual curves from digitized ASTM data
        calculator.load_deduct_curves(my_deduct_curves)
        calculator.load_cdv_curves(my_cdv_curves)
        
        # Calculate PCI for a sample unit
        result = calculator.calculate_sample_pci(observations, sample_area)
    """
    
    # Maximum number of deduct values allowed per ASTM procedure
    # m = 1 + (9/98) * (100 - HDV)  where HDV = highest deduct value
    MAX_DEDUCT_VALUES_FORMULA = True
    
    def __init__(self):
        self.deduct_curves: Dict[Tuple[int, Optional[str]], DeductCurve] = {}
        self.cdv_curves: Dict[int, CDVCurve] = {}
        
        # Load example curves (replace with real ASTM curves!)
        self._load_example_curves()
    
    def _load_example_curves(self):
        """Load example curves - REPLACE WITH REAL ASTM CURVES"""
        for (distress_id, severity), points in EXAMPLE_DEDUCT_CURVES.items():
            self.deduct_curves[(distress_id, severity)] = DeductCurve(
                distress_id, severity, points
            )
        
        for q, points in EXAMPLE_CDV_CURVES.items():
            self.cdv_curves[q] = CDVCurve(q, points)
    
    def load_deduct_curves(self, curves: Dict[Tuple[int, Optional[str]], List[Tuple[float, float]]]):
        """
        Load deduct value curves from digitized ASTM data.
        
        Args:
            curves: Dict mapping (distress_id, severity) to list of (density, DV) points
        """
        self.deduct_curves = {}
        for (distress_id, severity), points in curves.items():
            self.deduct_curves[(distress_id, severity)] = DeductCurve(
                distress_id, severity, points
            )
    
    def load_cdv_curves(self, curves: Dict[int, List[Tuple[float, float]]]):
        """
        Load CDV curves from digitized ASTM data.
        
        Args:
            curves: Dict mapping q value to list of (TDV, CDV) points
        """
        self.cdv_curves = {}
        for q, points in curves.items():
            self.cdv_curves[q] = CDVCurve(q, points)
    
    def get_deduct_value(
        self, 
        distress_id: int, 
        severity: Optional[Severity], 
        density: float
    ) -> float:
        """
        Look up deduct value from curves.
        
        Args:
            distress_id: Distress type ID (1-19)
            severity: Severity level (L, M, H) or None
            density: Distress density as percentage
            
        Returns:
            Deduct value (0-100)
        """
        severity_key = severity.value if severity else None
        key = (distress_id, severity_key)
        
        if key not in self.deduct_curves:
            raise ValueError(
                f"No deduct curve for distress {distress_id}, severity {severity_key}"
            )
        
        return self.deduct_curves[key].get_deduct_value(density)
    
    def get_cdv(self, tdv: float, q: int) -> float:
        """
        Look up corrected deduct value from CDV curves.
        
        Args:
            tdv: Total deduct value
            q: Number of deduct values > 2.0
            
        Returns:
            Corrected deduct value (0-100)
        """
        # Use q=7 curve for q > 7
        q_clamped = min(q, max(self.cdv_curves.keys()))
        q_clamped = max(1, q_clamped)
        
        if q_clamped not in self.cdv_curves:
            raise ValueError(f"No CDV curve for q={q_clamped}")
        
        return self.cdv_curves[q_clamped].get_cdv(tdv)
    
    def _calculate_max_deduct_values(self, highest_dv: float) -> int:
        """
        Calculate maximum number of allowable deduct values.
        
        Per ASTM D6433: m = 1 + (9/98) * (100 - HDV)
        
        Args:
            highest_dv: Highest individual deduct value
            
        Returns:
            Maximum number of deduct values to use
        """
        if not self.MAX_DEDUCT_VALUES_FORMULA:
            return 100  # No limit
        
        m = 1 + (9 / 98) * (100 - highest_dv)
        return max(1, int(m))
    
    def calculate_sample_pci(
        self, 
        observations: List[DistressObservation], 
        sample_area: float
    ) -> PCIResult:
        """
        Calculate PCI for a single sample unit.
        
        This is the core calculation implementing ASTM D6433 procedure.
        
        Args:
            observations: List of distress observations
            sample_area: Sample unit area in square feet
            
        Returns:
            PCIResult with PCI value, rating, and intermediate values
        """
        if sample_area <= 0:
            raise ValueError("Sample area must be positive")
        
        if not observations:
            # No distresses = perfect pavement
            return PCIResult(
                pci=100.0,
                rating=PCIRating.GOOD,
                deduct_values=[],
                max_cdv=0.0,
                iteration_cdvs=[]
            )
        
        # Step 1: Calculate deduct values for each observation
        deduct_values = []
        for obs in observations:
            density = obs.distress_type.calculate_density(obs.quantity, sample_area)
            dv = self.get_deduct_value(obs.distress_type.id, obs.severity, density)
            if dv > 0:  # Only include non-zero deduct values
                deduct_values.append(dv)
        
        if not deduct_values:
            return PCIResult(
                pci=100.0,
                rating=PCIRating.GOOD,
                deduct_values=[],
                max_cdv=0.0,
                iteration_cdvs=[]
            )
        
        # Step 2: Sort descending and apply maximum DV limit
        deduct_values.sort(reverse=True)
        max_dvs = self._calculate_max_deduct_values(deduct_values[0])
        deduct_values = deduct_values[:max_dvs]
        
        # Step 3: CDV iteration procedure
        iteration_cdvs = []
        dvs = deduct_values.copy()
        
        while True:
            # Count q = number of DVs > 2.0
            q = sum(1 for dv in dvs if dv > 2.0)
            
            if q == 0:
                q = 1  # Minimum q is 1
            
            # Calculate TDV and look up CDV
            tdv = sum(dvs)
            cdv = self.get_cdv(tdv, q)
            iteration_cdvs.append(cdv)
            
            # If q == 1, we're done
            if q <= 1:
                break
            
            # Find lowest DV > 2.0 and replace with 2.0
            for i in range(len(dvs) - 1, -1, -1):
                if dvs[i] > 2.0:
                    dvs[i] = 2.0
                    break
        
        # Step 4: PCI = 100 - max(CDV)
        max_cdv = max(iteration_cdvs)
        pci = 100.0 - max_cdv
        pci = max(0, min(100, pci))  # Clamp to valid range
        
        return PCIResult(
            pci=pci,
            rating=get_pci_rating(pci),
            deduct_values=deduct_values,
            max_cdv=max_cdv,
            iteration_cdvs=iteration_cdvs
        )


@dataclass
class SampleUnit:
    """A pavement sample unit with its observations"""
    id: str
    area: float  # square feet
    observations: List[DistressObservation] = field(default_factory=list)
    
    def add_observation(
        self,
        distress_id: int,
        severity: Optional[str],
        quantity: float
    ):
        """
        Add a distress observation to this sample unit.
        
        Args:
            distress_id: Distress type ID (1-19)
            severity: Severity level ('L', 'M', 'H') or None
            quantity: Measured quantity in appropriate units
        """
        distress_type = get_distress_by_id(distress_id)
        sev = Severity(severity) if severity else None
        obs = DistressObservation(distress_type, sev, quantity)
        self.observations.append(obs)


@dataclass
class PavementSection:
    """A pavement section consisting of multiple sample units"""
    id: str
    sample_units: List[SampleUnit] = field(default_factory=list)
    
    def calculate_section_pci(self, calculator: PCICalculator) -> float:
        """
        Calculate area-weighted PCI for the entire section.
        
        Args:
            calculator: PCICalculator instance
            
        Returns:
            Section-level PCI (0-100)
        """
        if not self.sample_units:
            return 100.0
        
        total_area = sum(su.area for su in self.sample_units)
        if total_area == 0:
            return 100.0
        
        weighted_sum = 0.0
        for su in self.sample_units:
            result = calculator.calculate_sample_pci(su.observations, su.area)
            weighted_sum += result.pci * su.area
        
        return weighted_sum / total_area
