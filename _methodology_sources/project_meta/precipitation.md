# Precipitation: why smooth interpolation is rejected

## Summary

tempify **rejects by design** smooth interpolation (linear, PCHIP, Fourier) of monthly precipitation to daily. This document explains why and what alternatives exist.

## The problem

Precipitation is **fundamentally different** from temperature, humidity, or radiation:

- **Intermittent.** Most days have zero precipitation; some have intense events.
- **Right-skewed distribution.** A few days produce most of the monthly total.
- **No temporal autocorrelation comparable to temperature.** Storms are discrete events.
- **Lower bound at zero.** Negative precipitation is physically impossible.

A smooth interpolator applied to monthly precipitation produces:

1. **Constant drizzle.** Every day gets a non-zero fraction of the monthly total. Physically absurd.
2. **No dry days.** A region with a monthly total of 30 mm gets ~1 mm every day, when reality might be 30 mm in a single storm and zero on the other 30 days.
3. **No extremes.** Maximum daily precipitation is dramatically underestimated.
4. **Distorted hydrological response.** Models calibrated on daily precipitation will misbehave with smoothly interpolated input.

## Why this is not a bug to fix

The information needed to reconstruct daily precipitation from monthly totals **does not exist** in the monthly data. It must come from elsewhere:

- A daily-resolution reanalysis (ERA5-Land, CHIRPS).
- A stochastic weather generator (LARS-WG, MarkSim, WeaGETS).
- A physically-based hybrid (delta method with a high-resolution daily template).

These approaches are out of scope for tempify's core: we do not generate new variability, we only interpolate.

## What tempify does instead

The `VariableProfileMatcher` identifies precipitation by:

- Standard name `precipitation`, `prec`, `pr`, `precip`
- Filename patterns matching common products (CHIRPS, WorldClim's `prec`)
- Units of `mm`, `mm/day`, `mm/month`, `kg m-2 s-1`

When precipitation is detected, the profile sets:

```yaml
variable: precipitation
allowed_methods: []  # No smooth interpolators
rejected_methods: ["linear", "pchip", "pchip_mp", "fourier"]
recommendation: "Use a daily reanalysis (CHIRPS, ERA5-Land) or a weather generator."
```

The `MethodVariableCompatibilityChecker` raises `MethodVariableIncompatibilityError` if the user explicitly requests a smooth method on precipitation.

## Recommended workflows for precipitation

### Option A: Use a daily product directly

If you need daily precipitation, download a daily product:

- **CHIRPS** (5 km, daily, 1981-present, global excluding high latitudes)
- **ERA5-Land** (9 km, daily, 1950-present, global)
- **MERRA-2** (50 km, daily, 1980-present, global)

These already contain the variability you need.

### Option B: Delta method (tempify does NOT do this)

If you must use monthly precipitation but want daily variability:

1. Get a daily product (e.g., CHIRPS) for the same period.
2. Compute monthly totals of the daily product.
3. Apply the ratio (monthly target) / (monthly from daily) as a multiplicative correction.
4. The result has daily variability (from CHIRPS) and conserves the monthly target.

This is essentially a bias correction. It is a valid technique but **out of scope** for tempify v1.0. May be added as an opt-in module in a future release.

### Option C: Stochastic weather generator (tempify does NOT do this)

Tools like LARS-WG or simple Markov chain + gamma models can generate stochastic daily series that respect monthly statistics. These are **out of scope** for tempify.

## Override (not recommended)

A user can force smooth interpolation of precipitation by passing `--force-method pchip --i-know-what-i-am-doing`. This:

- Logs a warning in the report.
- Marks the output's metadata with `"force_method_used": true` and `"physical_validity": "questionable"`.
- Should never be used in published or operational work.

## References

- Haylock, M. R., et al. (2008). A European daily high-resolution gridded data set of surface temperature and precipitation for 1950-2006. *J. Geophys. Res.*, 113, D20119.
- Funk, C., et al. (2015). The climate hazards infrared precipitation with stations (CHIRPS). *Scientific Data*, 2, 150066.
- Wilks, D. S., & Wilby, R. L. (1999). The weather generation game: a review of stochastic weather models. *Progress in Physical Geography*, 23(3), 329-357.
