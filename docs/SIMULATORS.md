# Simulator Guide

This document provides detailed information about the supported simulation engines and how to use them.

## Overview

The platform supports two N-body cosmological simulators:
- **Gadget4**: Production-grade code for large-scale simulations
- **CONCEPT**: Python-based code for rapid prototyping and testing

## Gadget4

### Description
Gadget4 is a massively parallel cosmological N-body and SPH code optimized for high-resolution simulations.

### Features
- Hybrid TreePM algorithm for gravity calculation
- Smoothed Particle Hydrodynamics (SPH)
- MPI parallelization
- Adaptive timestepping
- HDF5 output format

### Use Cases
- Large-scale structure formation
- Galaxy cluster simulations
- Dark matter halo studies
- High-resolution cosmological zoom simulations

### Configuration Example

```json
{
  "name": "Large scale structure",
  "simulator_type": "gadget4",
  "num_particles": 10000000,
  "box_size": 200.0,
  "parameters": {
    "TimeMax": 1.0,
    "Omega0": 0.3,
    "OmegaLambda": 0.7,
    "HubbleParam": 0.7,
    "MaxSizeTimestep": 0.01,
    "ErrTolIntAccuracy": 0.012
  }
}
```

### Parameter Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `BoxSize` | Simulation box size in Mpc/h | From API |
| `TimeMax` | End time of simulation | 1.0 |
| `Omega0` | Matter density parameter | 0.3 |
| `OmegaLambda` | Dark energy density | 0.7 |
| `HubbleParam` | Hubble constant (H0/100) | 0.7 |
| `MaxSizeTimestep` | Maximum timestep | 0.01 |
| `ErrTolIntAccuracy` | Integration accuracy | 0.012 |

## CONCEPT

### Description
CONCEPT (COsmological N-body CodE in PyThon) is a modern, flexible cosmological simulation code written in Python and optimized with Cython.

### Features
- Pure Python interface with C-level performance
- Multiple gravity solvers (PM, P³M, TreePM)
- Support for particles and fluids
- Built-in cosmological integration
- Easy to customize and extend

### Use Cases
- Fast prototyping of simulation setups
- Educational demonstrations
- Parameter space exploration
- Small to medium scale simulations
- Testing new physics modules

### Configuration Example

```json
{
  "name": "CONCEPT test simulation",
  "simulator_type": "concept",
  "num_particles": 1000000,
  "box_size": 100.0,
  "parameters": {
    "H0": 70,
    "Ωcdm": 0.26,
    "Ωb": 0.04,
    "a_begin": 0.02,
    "a_end": 1.0,
    "shortrange_scale": "1.25*boxsize/cbrt(N)"
  }
}
```

### Parameter Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `boxsize` | Box size in Mpc/a | From API |
| `H0` | Hubble constant (km/s/Mpc) | 70 |
| `Ωcdm` | Cold dark matter density | 0.26 |
| `Ωb` | Baryon density | 0.04 |
| `a_begin` | Initial scale factor | 0.02 |
| `a_end` | Final scale factor | 1.0 |
| `shortrange_scale` | Force softening scale | Auto |

## Choosing a Simulator

### Choose Gadget4 when:
- Running large-scale production simulations (>10M particles)
- Need maximum performance and optimization
- Require SPH hydrodynamics
- Need battle-tested, widely-used code
- Working with standard cosmological parameters

### Choose CONCEPT when:
- Rapid prototyping and testing
- Educational or demonstration purposes
- Parameter exploration and small runs
- Need easy customization
- Want pure Python interface
- Testing new physics before production

## API Usage

### Submit a Gadget4 Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gadget4 simulation",
    "simulator_type": "gadget4",
    "num_particles": 5000000,
    "box_size": 150.0,
    "parameters": {
      "TimeMax": 1.0
    }
  }'
```

### Submit a CONCEPT Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CONCEPT simulation",
    "simulator_type": "concept",
    "num_particles": 1000000,
    "box_size": 100.0,
    "parameters": {
      "a_end": 1.0
    }
  }'
```

### Filter Jobs by Simulator

```bash
# Get all Gadget4 jobs
curl "http://localhost:8000/api/v1/jobs?simulator_filter=gadget4"

# Get all CONCEPT jobs
curl "http://localhost:8000/api/v1/jobs?simulator_filter=concept"
```

## Worker Configuration

The platform uses separate worker pools for each simulator type, managed by Celery queues.

### Kubernetes Deployment

Workers are deployed as separate deployments:
- `gadget4-worker`: Handles Gadget4 simulations
- `concept-worker`: Handles CONCEPT simulations

### Scaling

Scale workers independently based on workload:

```bash
# Scale Gadget4 workers
kubectl scale deployment gadget4-worker --replicas=5 -n gadget4-stable

# Scale CONCEPT workers
kubectl scale deployment concept-worker --replicas=3 -n gadget4-stable
```

## Performance Comparison

| Aspect | Gadget4 | CONCEPT |
|--------|---------|---------|
| **Speed** | ⭐⭐⭐⭐⭐ Very Fast | ⭐⭐⭐ Fast |
| **Memory** | ⭐⭐⭐⭐ Optimized | ⭐⭐⭐ Good |
| **Scalability** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good |
| **Ease of Use** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Easy |
| **Flexibility** | ⭐⭐⭐ Fixed | ⭐⭐⭐⭐⭐ Highly Flexible |
| **Setup Time** | ⭐⭐ Complex | ⭐⭐⭐⭐⭐ Simple |

## Troubleshooting

### Gadget4 Issues

**Problem**: Simulation fails with memory error
- **Solution**: Increase worker memory limits in Kubernetes deployment
- Check `resources.limits.memory` in deployment YAML

**Problem**: Gadget4 binary not found
- **Solution**: Verify Docker image was built correctly with Gadget4 compiled

### CONCEPT Issues

**Problem**: CONCEPT import errors
- **Solution**: Check that `CONCEPT_DIR` environment variable is set
- Verify CONCEPT installation in Docker image

**Problem**: Slow execution
- **Solution**: Adjust `shortrange_scale` parameter for your particle count
- Consider using Gadget4 for large simulations

## References

### Gadget4
- [Official Repository](https://gitlab.mpcdf.mpg.de/vrs/gadget4)
- [Documentation](https://wwwmpa.mpa-garching.mpg.de/gadget4/)
- Paper: Springel et al. (2021)

### CONCEPT
- [GitHub Repository](https://github.com/jmd-dk/concept)
- [Documentation](https://jmd-dk.github.io/concept/)
- Paper: Dakin et al. (2019)

## Support

For issues specific to:
- **Platform/API**: Create an issue in this repository
- **Gadget4**: Consult Gadget4 documentation
- **CONCEPT**: Check CONCEPT documentation or GitHub issues

