"""
ASTM D6433 Distress Type Definitions for Asphalt Pavements

Each distress type has:
- Unique ID (1-19)
- Name
- Unit of measurement (area, linear, count)
- Whether severity levels apply
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Severity(Enum):
    """Distress severity levels per ASTM D6433"""
    LOW = 'L'
    MEDIUM = 'M'
    HIGH = 'H'


class DistressUnit(Enum):
    """Unit of measurement for distress quantities"""
    AREA = 'area'           # square feet
    LINEAR = 'linear'       # linear feet
    COUNT = 'count'         # number of occurrences


@dataclass
class DistressType:
    """Definition of a pavement distress type"""
    id: int
    name: str
    unit: DistressUnit
    has_severity: bool = True
    
    def calculate_density(self, quantity: float, sample_area: float) -> float:
        """
        Calculate density as percentage of sample area.
        
        For area-based: (distress_area / sample_area) * 100
        For linear: (linear_feet / sample_area) * 100
        For count (potholes): (count / sample_area) * 100
        
        Args:
            quantity: Measured quantity (sq ft, linear ft, or count)
            sample_area: Total sample unit area in sq ft
            
        Returns:
            Density as a percentage
        """
        if sample_area <= 0:
            raise ValueError("Sample area must be positive")
        return (quantity / sample_area) * 100


# ASTM D6433 Asphalt Pavement Distress Types
ASPHALT_DISTRESSES = {
    1: DistressType(1, "Alligator Cracking", DistressUnit.AREA),
    2: DistressType(2, "Bleeding", DistressUnit.AREA),
    3: DistressType(3, "Block Cracking", DistressUnit.AREA),
    4: DistressType(4, "Bumps and Sags", DistressUnit.LINEAR),
    5: DistressType(5, "Corrugation", DistressUnit.AREA),
    6: DistressType(6, "Depression", DistressUnit.AREA),
    7: DistressType(7, "Edge Cracking", DistressUnit.LINEAR),
    8: DistressType(8, "Joint Reflection Cracking", DistressUnit.LINEAR),
    9: DistressType(9, "Lane/Shoulder Drop-off", DistressUnit.LINEAR),
    10: DistressType(10, "Longitudinal & Transverse Cracking", DistressUnit.LINEAR),
    11: DistressType(11, "Patching and Utility Cut Patching", DistressUnit.AREA),
    12: DistressType(12, "Polished Aggregate", DistressUnit.AREA, has_severity=False),
    13: DistressType(13, "Potholes", DistressUnit.COUNT),
    14: DistressType(14, "Railroad Crossing", DistressUnit.AREA),
    15: DistressType(15, "Rutting", DistressUnit.AREA),
    16: DistressType(16, "Shoving", DistressUnit.AREA),
    17: DistressType(17, "Slippage Cracking", DistressUnit.AREA),
    18: DistressType(18, "Swell", DistressUnit.AREA),
    19: DistressType(19, "Weathering/Raveling", DistressUnit.AREA),
}


@dataclass
class DistressObservation:
    """A single distress observation from field inspection"""
    distress_type: DistressType
    severity: Optional[Severity]  # None for distresses without severity (e.g., polished aggregate)
    quantity: float               # In appropriate units (sq ft, linear ft, or count)
    
    def __post_init__(self):
        if self.distress_type.has_severity and self.severity is None:
            raise ValueError(f"{self.distress_type.name} requires a severity level")
        if not self.distress_type.has_severity and self.severity is not None:
            raise ValueError(f"{self.distress_type.name} does not use severity levels")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")


def get_distress_by_id(distress_id: int) -> DistressType:
    """Get distress type by ID"""
    if distress_id not in ASPHALT_DISTRESSES:
        raise ValueError(f"Unknown distress ID: {distress_id}")
    return ASPHALT_DISTRESSES[distress_id]


def get_distress_by_name(name: str) -> DistressType:
    """Get distress type by name (case-insensitive partial match)"""
    name_lower = name.lower()
    for distress in ASPHALT_DISTRESSES.values():
        if name_lower in distress.name.lower():
            return distress
    raise ValueError(f"Unknown distress name: {name}")
