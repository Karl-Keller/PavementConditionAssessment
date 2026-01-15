# PCI Calculator Architecture

This document describes the architecture of the PCI (Pavement Condition Index) calculation system. UML diagrams are provided as separate `.mmd` files for VS Code preview compatibility.

## Diagrams

| Diagram | File | Description |
|---------|------|-------------|
| Process Flow | [architecture-flowchart.mmd](./architecture-flowchart.mmd) | End-to-end PCI calculation workflow |
| Class Diagram | [architecture-classes.mmd](./architecture-classes.mmd) | Domain model and class relationships |
| Sequence Diagram | [architecture-sequence.mmd](./architecture-sequence.mmd) | Runtime interaction between components |
| State Diagram | [architecture-cdv-state.mmd](./architecture-cdv-state.mmd) | CDV iteration state machine |

## Overview

The PCI calculation follows ASTM D6433 methodology:

1. **Density Calculation** — Convert raw distress measurements (area, length, or count) to density percentages relative to the sample unit area.

2. **Deduct Value Lookup** — Interpolate deduct values from ~57 predefined curves based on distress type, severity, and density.

3. **CDV Iteration** — Iteratively calculate Corrected Deduct Values using the q-curve method until q=1, tracking the maximum CDV.

4. **Final PCI** — Compute `PCI = 100 - max(CDV)` and map to a condition rating (Good → Failed).

## Key Classes

- **`PCICalculator`** — Main entry point; orchestrates the calculation pipeline
- **`SampleUnit`** — Represents a survey sample with area and distress observations
- **`DeductCurve` / `CDVCurve`** — Interpolation logic for the ASTM lookup tables
- **`PavementSection`** — Aggregates multiple sample units into a section-level PCI
