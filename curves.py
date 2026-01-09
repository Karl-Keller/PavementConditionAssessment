"""
Curve interpolation utilities for deduct value and CDV lookups.

The ASTM D6433 standard provides curves as figures. These must be
digitized into point lists for interpolation.
"""
from typing import List, Tuple
import bisect


def interpolate_curve(points: List[Tuple[float, float]], x: float) -> float:
    """
    Linear interpolation on a curve defined by (x, y) points.
    
    Args:
        points: List of (x, y) tuples, sorted by x ascending
        x: The x value to interpolate
        
    Returns:
        Interpolated y value
        
    Raises:
        ValueError: If points list is empty or x is out of range
    """
    if not points:
        raise ValueError("Points list cannot be empty")
    
    # Handle edge cases
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    
    # Find insertion point
    x_values = [p[0] for p in points]
    idx = bisect.bisect_right(x_values, x)
    
    # Linear interpolation between points[idx-1] and points[idx]
    x0, y0 = points[idx - 1]
    x1, y1 = points[idx]
    
    # Avoid division by zero
    if x1 == x0:
        return y0
    
    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


def validate_curve(points: List[Tuple[float, float]], name: str = "curve") -> bool:
    """
    Validate that a curve is properly formatted.
    
    Args:
        points: List of (x, y) tuples
        name: Name for error messages
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If curve is invalid
    """
    if not points:
        raise ValueError(f"{name}: Points list cannot be empty")
    
    if len(points) < 2:
        raise ValueError(f"{name}: Need at least 2 points for interpolation")
    
    # Check monotonically increasing x values
    for i in range(1, len(points)):
        if points[i][0] <= points[i-1][0]:
            raise ValueError(f"{name}: X values must be monotonically increasing")
    
    # Check non-negative values (deduct values and CDVs are always >= 0)
    for x, y in points:
        if x < 0 or y < 0:
            raise ValueError(f"{name}: X and Y values must be non-negative")
    
    return True


class DeductCurve:
    """
    A single deduct value curve for a specific distress type and severity.
    
    Maps density (%) -> deduct value (0-100)
    """
    
    def __init__(self, distress_id: int, severity: str, points: List[Tuple[float, float]]):
        """
        Args:
            distress_id: Distress type ID (1-19)
            severity: Severity level ('L', 'M', 'H', or None for no-severity distresses)
            points: List of (density, deduct_value) tuples
        """
        self.distress_id = distress_id
        self.severity = severity
        self.points = sorted(points, key=lambda p: p[0])
        validate_curve(self.points, f"Distress {distress_id} severity {severity}")
    
    def get_deduct_value(self, density: float) -> float:
        """
        Get deduct value for a given density.
        
        Args:
            density: Distress density as percentage (0-100+)
            
        Returns:
            Deduct value (0-100)
        """
        dv = interpolate_curve(self.points, density)
        return max(0, min(100, dv))  # Clamp to valid range


class CDVCurve:
    """
    A Corrected Deduct Value curve for a specific q value.
    
    Maps Total Deduct Value -> Corrected Deduct Value
    """
    
    def __init__(self, q: int, points: List[Tuple[float, float]]):
        """
        Args:
            q: Number of deduct values > 2.0
            points: List of (TDV, CDV) tuples
        """
        self.q = q
        self.points = sorted(points, key=lambda p: p[0])
        validate_curve(self.points, f"CDV curve q={q}")
    
    def get_cdv(self, tdv: float) -> float:
        """
        Get corrected deduct value for a given total deduct value.
        
        Args:
            tdv: Total deduct value (sum of all DVs)
            
        Returns:
            Corrected deduct value (0-100)
        """
        cdv = interpolate_curve(self.points, tdv)
        return max(0, min(100, cdv))


# Placeholder curve data - MUST BE REPLACED with digitized curves from ASTM D6433
# These are illustrative examples only and will not produce correct PCI values!

EXAMPLE_DEDUCT_CURVES = {
    # Format: (distress_id, severity): [(density, deduct_value), ...]
    # 
    # IMPORTANT: These are NOT the actual ASTM curves!
    # You must digitize the real curves from ASTM D6433.
    # These placeholder values are for demonstration only.
    # 
    # 1. Alligator Cracking
    (1, 'L'): [(0, 0), (1, 6), (5, 18), (10, 26), (20, 34), (50, 44), (100, 52)],
    (1, 'M'): [(0, 0), (1, 12), (5, 32), (10, 44), (20, 56), (50, 72), (100, 84)],
    (1, 'H'): [(0, 0), (1, 18), (5, 42), (10, 56), (20, 70), (50, 88), (100, 100)],
    
    # 3. Block Cracking
    (3, 'L'): [(0, 0), (1, 2), (5, 6), (10, 10), (20, 15), (50, 22), (100, 30)],
    (3, 'M'): [(0, 0), (1, 4), (5, 12), (10, 18), (20, 26), (50, 38), (100, 50)],
    (3, 'H'): [(0, 0), (1, 8), (5, 20), (10, 30), (20, 42), (50, 60), (100, 78)],
    
    # 10. Longitudinal & Transverse Cracking
    (10, 'L'): [(0, 0), (1, 2), (5, 6), (10, 10), (20, 14), (50, 20), (100, 28)],
    (10, 'M'): [(0, 0), (1, 5), (5, 14), (10, 22), (20, 32), (50, 46), (100, 62)],
    (10, 'H'): [(0, 0), (1, 10), (5, 26), (10, 38), (20, 52), (50, 72), (100, 90)],
    
    # 13. Potholes (density = count per 1000 sq ft equivalent)
    (13, 'L'): [(0, 0), (0.1, 8), (0.5, 18), (1, 24), (2, 32), (5, 42), (10, 52)],
    (13, 'M'): [(0, 0), (0.1, 15), (0.5, 32), (1, 42), (2, 54), (5, 70), (10, 84)],
    (13, 'H'): [(0, 0), (0.1, 22), (0.5, 48), (1, 62), (2, 78), (5, 94), (10, 100)],
    
    # 15. Rutting
    (15, 'L'): [(0, 0), (1, 4), (5, 10), (10, 14), (20, 20), (50, 28), (100, 36)],
    (15, 'M'): [(0, 0), (1, 8), (5, 20), (10, 30), (20, 42), (50, 58), (100, 74)],
    (15, 'H'): [(0, 0), (1, 14), (5, 34), (10, 48), (20, 64), (50, 84), (100, 98)],
    
    # 19. Weathering/Raveling
    (19, 'L'): [(0, 0), (1, 1), (5, 3), (10, 5), (20, 8), (50, 14), (100, 20)],
    (19, 'M'): [(0, 0), (1, 4), (5, 10), (10, 16), (20, 24), (50, 36), (100, 50)],
    (19, 'H'): [(0, 0), (1, 8), (5, 20), (10, 32), (20, 46), (50, 66), (100, 86)],
    
    # ... Add remaining curves after digitizing from ASTM D6433
}

EXAMPLE_CDV_CURVES = {
    # Format: q: [(TDV, CDV), ...]
    # 
    # IMPORTANT: These are NOT the actual ASTM curves!
    # 
    1: [(0, 0), (10, 10), (20, 20), (50, 50), (100, 100), (150, 100), (200, 100)],
    2: [(0, 0), (10, 8), (20, 15), (50, 40), (100, 72), (150, 88), (200, 96)],
    3: [(0, 0), (10, 6), (20, 12), (50, 32), (100, 58), (150, 76), (200, 88)],
    4: [(0, 0), (10, 5), (20, 10), (50, 26), (100, 48), (150, 66), (200, 80)],
    5: [(0, 0), (10, 4), (20, 8), (50, 22), (100, 42), (150, 58), (200, 72)],
    6: [(0, 0), (10, 4), (20, 7), (50, 19), (100, 37), (150, 52), (200, 66)],
    7: [(0, 0), (10, 3), (20, 6), (50, 17), (100, 33), (150, 47), (200, 60)],
}
