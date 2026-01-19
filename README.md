# ASTM D6433 Pavement Condition Index (PCI) Calculator

A Python implementation of the ASTM D6433 standard for calculating Pavement Condition Index for roads and parking lots.

## Overview

The Pavement Condition Index (PCI) is a numerical rating from 0 (failed) to 100 (excellent) that indicates the overall condition of a pavement surface. It was developed by the U.S. Army Corps of Engineers and is now an ASTM standard (D6433 for roads/parking lots, D5340 for airfields).

## Algorithm Summary

```
PCI = 100 - max(CDV)
```

Where CDV (Corrected Deduct Value) accounts for the non-linear combination of multiple distress types.

## Core Concepts

### Distress Types (Asphalt Pavements)

| ID | Distress Type | Unit | Severity Levels |
|----|---------------|------|-----------------|
| 1 | Alligator Cracking | sq ft | L, M, H |
| 2 | Bleeding | sq ft | L, M, H |
| 3 | Block Cracking | sq ft | L, M, H |
| 4 | Bumps and Sags | linear ft | L, M, H |
| 5 | Corrugation | sq ft | L, M, H |
| 6 | Depression | sq ft | L, M, H |
| 7 | Edge Cracking | linear ft | L, M, H |
| 8 | Joint Reflection Cracking | linear ft | L, M, H |
| 9 | Lane/Shoulder Drop-off | linear ft | L, M, H |
| 10 | Longitudinal & Transverse Cracking | linear ft | L, M, H |
| 11 | Patching and Utility Cut Patching | sq ft | L, M, H |
| 12 | Polished Aggregate | sq ft | - (no severity) |
| 13 | Potholes | count | L, M, H |
| 14 | Railroad Crossing | sq ft | L, M, H |
| 15 | Rutting | sq ft | L, M, H |
| 16 | Shoving | sq ft | L, M, H |
| 17 | Slippage Cracking | sq ft | L, M, H |
| 18 | Swell | sq ft | L, M, H |
| 19 | Weathering/Raveling | sq ft | L, M, H |

### Calculation Steps

1. **Density Calculation**: For each distress observation:
   - Area-based: `density = (distress_area / sample_area) * 100`
   - Linear: `density = (distress_length / sample_area) * 100`
   - Count (potholes): `density = (count / sample_area) * 100`

2. **Deduct Value Lookup**: Use distress-specific curves to convert density → deduct value (0-100)

3. **CDV Calculation** (iterative):
   - Count q = number of deduct values > 2.0
   - Look up CDV from q-curve using Total Deduct Value (TDV)
   - Replace lowest DV > 2 with 2.0, decrement q
   - Repeat until q = 1
   - Take maximum CDV from all iterations

4. **Final PCI**: `PCI = 100 - max(CDV)`

## Data Requirements

### Deduct Value Curves (Critical)

The ASTM standard contains ~57 curves for asphalt pavements (19 distresses × 3 severities, minus a few special cases). These must be digitized from the standard figures.

**Curve format** (suggested):
```python
# Each curve: list of (density, deduct_value) points
DEDUCT_CURVES = {
    (1, 'L'): [(0, 0), (1, 5), (5, 15), (10, 22), ...],  # Alligator, Low
    (1, 'M'): [(0, 0), (1, 8), (5, 25), (10, 35), ...],  # Alligator, Medium
    (1, 'H'): [(0, 0), (1, 12), (5, 38), (10, 52), ...], # Alligator, High
    # ... etc for all 19 distress types
}
```

### CDV Curves

7 curves for q = 1 through q = 7+ (also from ASTM standard):
```python
CDV_CURVES = {
    1: [(0, 0), (10, 10), (50, 50), (100, 100)],  # q=1 is identity
    2: [(0, 0), (10, 8), (50, 42), (100, 78)],
    # ... etc
}
```

## Project Structure

```
pci_calculator/
├── README.md
├── pci/
│   ├── __init__.py
│   ├── calculator.py      # Main PCI calculation logic
│   ├── distresses.py      # Distress type definitions
│   ├── curves.py          # Deduct value & CDV curve data
│   └── interpolation.py   # Curve interpolation utilities
├── tests/
│   ├── test_calculator.py
│   └── test_curves.py
└── examples/
    └── sample_inspection.py
```

## Implementation Status

- [x] Distress type catalog with units and severity levels
- [x] Curve interpolation utilities
- [ ] Deduct value curves (placeholder only — requires ASTM D6433 document)
- [ ] CDV curves (placeholder only — requires ASTM D6433 document)
- [x] Core PCI calculation algorithm
- [x] Sample unit handling
- [x] Section-level PCI rollup (area-weighted)
- [ ] Network-level aggregation
- [ ] Validation against known PAVER outputs

## Current Scope & Future Enhancements

### Current Focus

This implementation targets **asphalt (AC) pavements** per ASTM D6433, covering the 19 distress types listed above. The calculation engine handles:

- Single sample unit PCI calculation
- Density calculation for area, linear, and count-based distresses
- Deduct value interpolation from distress-specific curves
- Iterative CDV calculation with q-curve correction
- Section-level PCI rollup via area-weighted averaging

### Not Yet Implemented (ASTM D6433)

| Feature | Notes |
|---------|-------|
| **Concrete (PCC) pavements** | Requires separate distress catalog (~15 types) and curve set |
| **Random vs. additional sample weighting** | ASTM specifies different treatment for additional samples |
| **Network-level aggregation** | Rolling up section PCIs to network/branch level |
| **Survey metadata** | Date, inspector ID, branch/network ID for historical tracking |

### Beyond ASTM D6433

The following features are outside the scope of the ASTM standard but common in pavement management systems:

| Feature | Notes |
|---------|-------|
| **Condition projection** | Deterioration modeling based on historical PCI trends |
| **Maintenance recommendation** | M&R treatment selection based on distress types and PCI |
| **Budget optimization** | Multi-year planning with funding constraints |

### Roadmap

1. Complete AC implementation with full curve coverage
2. Add network-level aggregation and sample weighting
3. Evaluate PCC pavement support based on user demand

## Legal Note

The deduct value curves and CDV curves are copyrighted by ASTM International. To complete this implementation, you must:

1. Purchase ASTM D6433 from astm.org
2. Manually digitize the curves from the standard's figures
3. Do not redistribute the digitized curve data

The algorithm itself is not copyrighted—only the specific curve data.

## References

- ASTM D6433: Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys
- ASTM D5340: Standard Test Method for Airport Pavement Condition Index Surveys
- Shahin, M.Y. (2005). Pavement Management for Airports, Roads, and Parking Lots. Springer.
