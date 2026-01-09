#!/usr/bin/env python3
"""
Example usage of the ASTM D6433 PCI Calculator

NOTE: This uses placeholder curve data and will NOT produce accurate PCI values.
To get accurate results, you must:
1. Purchase ASTM D6433 from astm.org
2. Digitize the deduct value curves (Figures X1-X19)
3. Digitize the CDV curves (Figure X20)
4. Load them via calculator.load_deduct_curves() and calculator.load_cdv_curves()
"""

import sys

from calculator import (
    PCICalculator, SampleUnit, PavementSection,
    Severity, get_distress_by_id, ASPHALT_DISTRESSES
)


def example_single_sample():
    """Calculate PCI for a single sample unit"""
    print("=" * 60)
    print("Example 1: Single Sample Unit Calculation")
    print("=" * 60)
    
    calc = PCICalculator()
    
    # Create a sample unit (typical size: 2500 sq ft for roads)
    sample = SampleUnit(id="SU-001", area=2500)
    
    # Add distress observations from field inspection
    # Format: distress_id, severity, quantity
    
    # Alligator cracking, Medium severity, 150 sq ft
    sample.add_observation(1, 'M', 150)
    
    # Longitudinal & Transverse cracking, Low severity, 75 linear ft
    sample.add_observation(10, 'L', 75)
    
    # Weathering/Raveling, Low severity, 500 sq ft
    sample.add_observation(19, 'L', 500)
    
    # Calculate PCI
    result = calc.calculate_sample_pci(sample.observations, sample.area)
    
    print(f"\nSample Unit: {sample.id}")
    print(f"Area: {sample.area} sq ft")
    print(f"\nDistress Observations:")
    for obs in sample.observations:
        sev = obs.severity.value if obs.severity else "N/A"
        print(f"  - {obs.distress_type.name}: {obs.quantity} {obs.distress_type.unit.value}, severity {sev}")
    
    print(f"\nDeduct Values: {[f'{dv:.1f}' for dv in result.deduct_values]}")
    print(f"CDV Iterations: {[f'{cdv:.1f}' for cdv in result.iteration_cdvs]}")
    print(f"Max CDV: {result.max_cdv:.1f}")
    print(f"\n>>> PCI: {result.pci:.0f} ({result.rating.value})")
    

def example_section():
    """Calculate PCI for a pavement section with multiple sample units"""
    print("\n" + "=" * 60)
    print("Example 2: Section-Level Calculation (Multiple Samples)")
    print("=" * 60)
    
    calc = PCICalculator()
    
    # Create a pavement section
    section = PavementSection(id="Main-St-Block-1")
    
    # Add sample units
    su1 = SampleUnit(id="SU-001", area=2500)
    su1.add_observation(1, 'M', 150)   # Alligator cracking
    su1.add_observation(10, 'L', 75)   # L&T cracking
    section.sample_units.append(su1)
    
    su2 = SampleUnit(id="SU-002", area=2500)
    su2.add_observation(3, 'L', 200)   # Block cracking
    su2.add_observation(19, 'L', 300)  # Weathering
    section.sample_units.append(su2)
    
    su3 = SampleUnit(id="SU-003", area=2500)
    su3.add_observation(1, 'H', 100)   # Alligator cracking, High severity
    su3.add_observation(13, 'M', 2)    # Potholes
    su3.add_observation(15, 'M', 50)   # Rutting
    section.sample_units.append(su3)
    
    # Calculate individual sample PCIs
    print(f"\nSection: {section.id}")
    print(f"Sample Units: {len(section.sample_units)}")
    print("\nIndividual Sample Results:")
    
    for su in section.sample_units:
        result = calc.calculate_sample_pci(su.observations, su.area)
        print(f"  {su.id}: PCI = {result.pci:.0f} ({result.rating.value})")
    
    # Calculate section-level (area-weighted) PCI
    section_pci = section.calculate_section_pci(calc)
    from calculator import get_pci_rating
    section_rating = get_pci_rating(section_pci)
    
    print(f"\n>>> Section PCI: {section_pci:.0f} ({section_rating.value})")


def example_distress_catalog():
    """Show available distress types"""
    print("\n" + "=" * 60)
    print("Distress Type Catalog (ASTM D6433 Asphalt)")
    print("=" * 60)
    
    print(f"\n{'ID':<4} {'Name':<40} {'Unit':<8} {'Severity'}")
    print("-" * 60)
    for distress in ASPHALT_DISTRESSES.values():
        sev = "L/M/H" if distress.has_severity else "None"
        print(f"{distress.id:<4} {distress.name:<40} {distress.unit.value:<8} {sev}")


def main():
    print("\n" + "#" * 60)
    print("# ASTM D6433 PCI Calculator - Example Usage")
    print("# WARNING: Using placeholder curves - results are illustrative only!")
    print("#" * 60)
    
    example_distress_catalog()
    example_single_sample()
    example_section()
    
    print("\n" + "=" * 60)
    print("NOTE: To get accurate PCI values, replace the example curves")
    print("with digitized data from ASTM D6433 standard.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
