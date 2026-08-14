# AUDIT RESPONSE AGY 1 — Physics and Modelling Audit
**Auditor Role:** Physics and Modelling Specialist (Independent Audit)  
**Scope:** Governing equations, force-field validity, MD contact-angle extraction, Marangoni dominance scaling, closure mathematical structure, and consistency between claimed physics and coded implementations.  
**Target File:** `/home/azan/research/T12_MD_wettability_closure/70_audit/AUDIT_RESPONSE_AGY_1.md`  
**Date:** 2026-08-14

---

## Executive Summary & Verdict

**Verdict: CONDITIONAL PASS / MAJOR MODELLING REVISIONS REQUIRED.**

The fundamental scientific premise—deriving the wettability dependence of electrolytic bubble departure from potential-aware interface simulations and evaluating its impact on cell polarisation—is conceptually viable and addresses a real limitation in the alkaline electrolysis literature. However, the initial problem definition suffered from critical physical inconsistencies, dimensional and kinetic ambiguities, unrealistic scaling assumptions for solutal Marangoni effects, and an overextended claim regarding what an MD simulation of a flat single crystal can supply to a continuum bubble-coverage closure.

The key findings and mandatory revisions established in this physics audit are summarized below:
1. **Loss Decomposition & Kinetics:** The activation overpotential penalty was originally understated by a factor of 2 due to conflating a one-electron rate-determining step ($\alpha n = 0.5$) with the overall two-electron reaction stoichiometry ($n=2$). The corrected Tafel penalty at $\Theta = 0.8$ is **$97.9\text{ mV}$** (not $49\text{ mV}$).
2. **Current Conservation in Two-Phase Boundary Conditions:** The Faradaic wall flux in resolved simulations must strictly satisfy galvanostatic current conservation. Applying a fixed $j/(2F)$ flux over the wetted area artificially reduces total hydrogen evolution by $(1-\Theta)$ as coverage grows; the boundary flux must be $\dot{n} = j / [2F(1-\Theta)]$.
3. **Line Tension in Quasi-2D Cylindrical Caps:** Extrapolating contact angles via a $1/R$ modified Young equation from a periodic cylindrical cap is a **physical error**. Cylindrical contact lines have zero in-plane geodesic curvature ($\kappa_{\text{line}} \equiv 0$), completely suppressing line tension. The $1/R$ fit would merely fit finite-size confinement artifacts. Box-size convergence of the planar angle must replace size extrapolation.
4. **Marangoni Scaling & Well-Posedness of P3:** Solutal Marangoni forces on macroscopic electrolytic bubbles ($R_b \sim 50\text{--}100\,\mu\text{m}$) in clean alkaline electrolyte are on the order of $0.01\text{--}50\text{ nN}$, whereas capillary retention forces are $1\text{--}5\,\mu\text{N}$ ($100\text{--}1000\times$ larger). The boundary $\Lambda = |F_{\text{cap}}|/|F_{\text{Mar}}| = 1$ is **not reachable** within the standard industrial envelope unless extreme concentration gradients, surfactant effects, or near-complete wetting ($\theta \to 0$) occur. Prediction P3 must be framed as a bounding test that will likely confirm capillary dominance across the industrial window.
5. **Coverage Derivation vs. Nucleation Site Density:** A single-bubble simulation cannot derive coverage $\Theta$ from first principles because coverage is an ensemble property governed by active nucleation-site density $N_{\text{site}}$, waiting times, and coalescence. The study derives the *wettability-dependent single-bubble departure volume and residence time*; $N_{\text{site}}$ must be explicitly declared as an external empirical parameter.
6. **Measurand Mismatch (Vogt vs. Rox):** The $4\text{--}6\times$ discrepancy between Vogt ($\Theta \approx 0.15$) and Rox ($A_{\text{cov}} \to 1.0$) at $500\text{ A m}^{-2}$ is a genuine physical difference between *active catalytic contact-area screening* on a planar electrode and *projected optical shadow area* of a 3D bubble swarm on an expanded-mesh porous electrode.

---

## Detailed Audit Findings (Q1 – Q6)

---

### Q1 — Is the physics right?

#### 1.1 Loss Decomposition & Butler–Volmer Coverage Factor (Eqs. 1–5)
The cell voltage decomposition is:
$$U_{\text{cell}} = U_{\text{rev}} + \eta_{\text{act,a}} + |\eta_{\text{act,c}}| + \eta_{\text{ohm}} + \eta_{\text{conc}}$$

##### Kinetic Convention and Tafel Penalty
The local current density on the unshielded catalyst area is $j_{\text{loc}} = j / (1 - \Theta)$. Substituting into the standard Butler–Volmer equation:
$$j = (1 - \Theta) j_0 \left[ \exp\left(\frac{\alpha_a n F \eta_{\text{act}}}{RT}\right) - \exp\left(-\frac{\alpha_c n F \eta_{\text{act}}}{RT}\right) \right]$$

In the cathodic Tafel regime ($|\eta_{\text{act,c}}| \gg RT/F$), this yields:
$$\Delta \eta_{\text{act}} = \frac{RT}{\alpha_c n F} \ln\left(\frac{1}{1 - \Theta}\right)$$

*Numerical Evaluation at $T = 353.15\text{ K}$ ($80^\circ\text{C}$):*
- Universal gas constant $R = 8.31446\text{ J mol}^{-1}\text{ K}^{-1}$, Faraday constant $F = 96485.33\text{ C mol}^{-1}$.
- Thermal voltage $\frac{RT}{F} = \frac{8.31446 \times 353.15}{96485.33} = 0.030420\text{ V} = 30.420\text{ mV}$.
- For the Hydrogen Evolution Reaction (HER) in alkaline media ($2\text{H}_2\text{O} + 2e^- \rightarrow \text{H}_2 + 2\text{OH}^-$), assuming the Volmer step ($\text{H}_2\text{O} + e^- + \text{M} \rightarrow \text{M-H}_{\text{ads}} + \text{OH}^-$) is the rate-determining step with a single-electron transfer ($n = 1$) and symmetry factor $\alpha_c = 0.5$:
  $$\alpha_c n = 0.5 \implies \frac{RT}{\alpha_c n F} = \frac{30.420\text{ mV}}{0.5} = 60.84\text{ mV}$$
- At $\Theta = 0.20$: $\Delta \eta_{\text{act}} = 60.84 \times \ln(1/0.80) = 60.84 \times 0.22314 = \mathbf{13.58\text{ mV}}$ (was claimed as $6\text{ mV}$).
- At $\Theta = 0.80$: $\Delta \eta_{\text{act}} = 60.84 \times \ln(1/0.20) = 60.84 \times 1.60944 = \mathbf{97.92\text{ mV}}$ (was claimed as $49\text{ mV}$).

*Auditor Finding on Kinetics:*
The original draft's values ($6\text{ mV}$ and $49\text{ mV}$) resulted from silently setting $\alpha_c n = 1.0$ (equivalent to $\alpha_c = 0.5, n = 2$). In electrochemical kinetics, using $n=2$ directly in the exponential argument of Butler–Volmer for a multi-step reaction without defining a transfer coefficient ($\alpha_{\text{app}} = 1.0$) violates microkinetic consistency. The correction to $\alpha_c n = 0.5$ ($97.9\text{ mV}$ penalty at $\Theta = 0.8$) is **physically rigorous for a Volmer-limited cathode**. If the Heyrovsky step is rate-determining, $\alpha_{\text{app}} \approx 1.5$, yielding $\Delta \eta_{\text{act}} \approx 32.6\text{ mV}$. The paper must explicitly define the assumed elementary reaction step and state $\alpha_{\text{app}} = 0.5$ ($140\text{ mV/dec}$ Tafel slope at $353\text{ K}$).

#### 1.2 Bruggeman Exponent and Ohmic Loss Formulation
Equation (4) specifies:
$$\sigma_{\text{eff}} = \sigma_0 (1 - \varepsilon)^{3/2}, \quad \eta_{\text{ohm}} = \frac{j \cdot d_{\text{gap}}}{\sigma_{\text{eff}}}$$

- **Dimensional consistency:** Fully consistent ($[\text{A m}^{-2}] \cdot [\text{m}] / [\text{S m}^{-1}] = [\text{V}]$).
- **Physical validity:** The exponent $3/2$ is the classical Bruggeman effective medium approximation for dilute-to-moderate spherical insulating inclusions in a continuous conducting phase. For electrolysis channels with high void fraction ($\varepsilon > 0.3$) or non-spherical bubble clusters, modified Bruggeman or Meredith–Tobias forms ($\sigma_{\text{eff}} = \sigma_0 \frac{2(1-\varepsilon)}{2+\varepsilon}$) are sometimes used, but $(1-\varepsilon)^{1.5}$ is standard in the alkaline electrolysis corpus (E04, E07).
- **Caveat for CFD discretization:** The 1D algebraic form $\eta_{\text{ohm}} = j d_{\text{gap}} / \sigma_{\text{eff}}$ assumes a uniform gas fraction $\varepsilon$. In the continuum cell solver (`reactingMultiphaseEulerFoam`), the 3D/2D potential equation $\nabla \cdot (\sigma_{\text{eff}}(\mathbf{x}) \nabla \varphi) = 0$ must be solved, as the gas fraction forms a pronounced near-wall boundary layer.

#### 1.3 Concentration Overpotential Formulation
Equation (5) specifies:
$$\eta_{\text{conc}} = \frac{RT}{nF} \ln\left( \frac{1}{1 - j/j_{\text{lim}}(\Theta)} \right)$$
- **Physical audit:** For $\text{OH}^-$ accumulation/depletion at the cathode, $n=1$ per mole of $\text{OH}^-$. However, adhering bubbles also cause extreme local supersaturation of dissolved hydrogen ($S = c_{\text{H}_2}/c_{\text{H}_2,\text{sat}} \gg 1$), producing a thermodynamic Nernstian shift:
  $$\Delta E_{\text{rev}} = \frac{RT}{2F} \ln\left( \frac{c_{\text{H}_2,\text{surf}}}{c_{\text{H}_2,\text{sat}}} \right)$$
  This Nernstian dissolved-gas overpotential often reaches $40\text{--}80\text{ mV}$ at high current densities and is distinct from the mass-transfer limiting current $j_{\text{lim}}$. The manuscript must clarify whether $\eta_{\text{conc}}$ represents the Nernstian dissolved-gas shift or $\text{OH}^-$ transport limitation.

#### 1.4 Double-Counting Analysis (Active Area vs. Conductivity)
*Question:* Is bubble blockage counted both in active catalyst area and in bulk electrolyte conductivity?
- **Analysis:**
  - $\Theta$ is the **2D area fraction of the catalyst surface** covered by adhering bubble contact footprints (the "dry/gas" contact patches). It enters strictly as a boundary condition on the charge transfer kinetics (reducing active area to $1-\Theta$).
  - $\varepsilon_g$ is the **3D volume fraction of gas** in the electrolyte phase. It enters strictly into the bulk Laplace/Poisson solver for potential $\nabla \cdot (\sigma_{\text{eff}} \nabla \varphi) = 0$.
- **Potential double-counting risk:** If the two-fluid Eulerian cell model treats the first near-wall computational cell as containing both the adhering bubble volume (as part of $\varepsilon_g$) AND applies the wall coverage factor $(1-\Theta)$ to the boundary face, the ohmic drop across that first computational cell will be penalized twice.
- **Auditor requirement:** The model must enforce a clean separation: gas adhering to the wall contributes to the surface blockage $\Theta$; upon detachment, it is injected as a volumetric gas source into $\varepsilon_g$. The near-wall conductivity must not conflate the footprint contact resistance with the dispersed bubble cloud resistance.

---

### Q2 — Are the three predictions P1–P3 actually falsifiable, and is P3 well-posed?

#### 2.1 Prediction P1: Contact Angle Potential-Dependence $\theta(\Delta\Psi)$
- **Status:** **FALSIFIABLE and PHYSICALLY SOUND.**
- **Mechanism:** In classical constant-potential MD (`fix electrode/conp`), charging the electrode slab induces an electrical double layer (EDL) with capacitance $C_{\text{dl}}$. The thermodynamic Lippmann equation governs electrowetting:
  $$\frac{d\gamma_{\text{sl}}}{d\Psi} = -q_{\text{s}} \implies \cos\theta(\Delta\Psi) = \cos\theta_{\text{pzc}} + \frac{C_{\text{dl}}}{2\gamma_{\text{lv}}} (\Delta\Psi - \Psi_{\text{pzc}})^2$$
- For typical values ($C_{\text{dl}} \approx 0.1\text{--}0.3\text{ F m}^{-2}$, $\gamma_{\text{lv}} \approx 0.072\text{ N m}^{-1}$, $\Delta\Psi = 0.5\text{--}1.0\text{ V}$), $\Delta(\cos\theta) \approx 0.15\text{--}0.50$, corresponding to an observable contact angle shift of $10^\circ\text{--}30^\circ$.
- *Falsification criteria:* If the measured contact angle across $\Delta\Psi \in [0, 1.0\text{ V}]$ is constant within the replica uncertainty ($< 2^\circ$), P1 is definitively falsified.

#### 2.2 Prediction P2: Departure from Empirical Vogt Scaling $\Theta(j)$
- **Status:** **FALSIFIABLE, but subject to a critical methodological constraint.**
- **Constraint:** In the single-bubble reconstruction $\Theta = N_{\text{site}} \cdot A_{\text{footprint}} \cdot f_{\text{residence}}$, the scaling $\Theta \propto j^a$ depends heavily on the chosen active site density function $N_{\text{site}}(j)$.
- If $N_{\text{site}}$ is fixed or taken as a power law from literature ($N_{\text{site}} \propto j^m$), the derived exponent $a$ reflects the product of hydrodynamic residence time scaling and nucleation site activation.
- *Auditor ruling:* P2 is valid provided the manuscript explicitly evaluates the hydrodynamic departure volume $V_{\text{det}}(j, v, \theta)$ independently from the assumed nucleation density function $N_{\text{site}}(j)$.

#### 2.3 Prediction P3: Marangoni vs. Capillary Boundary ($\Lambda = 1$)
- **Status:** **WELL-POSED HYPOTHESIS, but the $\Lambda = 1$ boundary is UNLIKELY TO BE REACHED within the stated envelope.**
- **Physical Force Scaling Analysis:**
  Let us compute the forces acting on a departing bubble at an alkaline cathode:
  1. *Capillary retention force:*
     $$F_{\text{cap}} = \pi R_{\text{base}} \gamma_{\text{lv}} \sin\theta_c$$
     For a bubble with departure radius $R_b \approx 50\,\mu\text{m} = 5 \times 10^{-5}\text{ m}$, assuming a contact radius $R_{\text{base}} \approx 20\,\mu\text{m}$ and $\gamma_{\text{lv}} = 0.072\text{ N m}^{-1}$:
     $$F_{\text{cap}} \approx \pi (2 \times 10^{-5}\text{ m}) (0.072\text{ N m}^{-1}) \sin(60^\circ) \approx \mathbf{3.9 \times 10^{-6}\text{ N} = 3.9\,\mu\text{N}}$$
  2. *Solutal Marangoni force:*
     $$F_{\text{Mar}} \approx \oint_S \nabla_s \gamma_{\text{lv}} dS \approx \Delta\gamma_{\text{lv}} \cdot R_b$$
     What is the surface tension variation $\Delta\gamma_{\text{lv}} across a single bubble?
     - For dissolved $\text{H}_2$ in water, the solutal surface tension coefficient $\partial\gamma/\partial c_{\text{H}_2}$ is extremely small (on the order of $-10^{-4}\text{ N m}^{-1}\text{ M}^{-1}$). Even with a supersaturation gradient of $\Delta c_{\text{H}_2} \approx 10\text{ mM}$ across the bubble height, $\Delta\gamma_{\text{lv}} \approx 10^{-6}\text{ N m}^{-1}$.
     - This gives $F_{\text{Mar}} \approx (10^{-6}\text{ N m}^{-1})(5 \times 10^{-5}\text{ m}) \approx \mathbf{5 \times 10^{-11}\text{ N} = 0.05\text{ nN}}$.
     - Even if driven by KOH concentration gradients ($\partial\gamma/\partial c_{\text{KOH}} \approx +2.5\text{ mN m}^{-1}\text{ M}^{-1}$) with $\Delta c_{\text{KOH}} \approx 0.1\text{ M}$ across the bubble, $\Delta\gamma_{\text{lv}} \approx 2.5 \times 10^{-4}\text{ N m}^{-1}$, yielding $F_{\text{Mar}} \approx \mathbf{12.5\text{ nN}}$.
  3. *Force Ratio $\Lambda$:*
     $$\Lambda = \frac{|F_{\text{cap}}|}{|F_{\text{Mar}}|} \approx \frac{3900\text{ nN}}{12.5\text{ nN}} \approx \mathbf{300 \gg 1}$$
- **Auditor Conclusion on P3:**
  The solutal Marangoni force on a $50\text{--}100\,\mu\text{m}$ bubble is **2 to 4 orders of magnitude smaller** than the capillary pinning force.
  Therefore, the condition $\Lambda = 1$ is unreachable in standard macroscopic water electrolysis channels unless the contact angle is near zero ($\theta \to 0$, where $R_{\text{base}} \to 0$) or for sub-micron bubbles where capillary forces vanish.
  *Does the study still have a result if Marangoni is negligible everywhere?* **YES.** Demonstrating rigorously that $\Lambda \gg 1$ across $j = 10^2\text{--}10^4\text{ A m}^{-2}$ provides a definitive physical justification for why wettability engineering ($\theta$-control) remains the dominant physical lever for bubble detachment in industrial alkaline electrolysers. P3 is a win-win hypothesis: if a boundary exists, it bounds the closure; if $\Lambda \gg 1$ everywhere, it confirms wettability dominance.

---

### Q3 — The Vogt/Rox discrepancy

#### 3.1 Analysis of the Discrepancy
At $j = 500\text{ A m}^{-2}$ ($50\text{ mA cm}^{-2}$):
- **Vogt correlation (E21):** $\Theta = 0.023 \times (500)^{0.3} \approx \mathbf{0.148}$ (15% surface coverage).
- **Rox et al. (Anchor A1, arXiv:2209.11550):** Reports the electrode is *"nearly fully covered ($A_{\text{cov}} \approx 80\text{--}100\%$)"* in $< 0.1\text{ s}$.

#### 3.2 Is this a Measurand Mismatch or a Physical Disagreement?
The attribution to a **measurand mismatch** is physically correct and mathematically demonstrable, but must not be treated as a hand-waving dismissal. There are three distinct physical mechanisms causing this $5\times$ gap:

1. **Contact Area vs. Projected Cross-Sectional Area:**
   For a spherical cap bubble with contact angle $\theta$ (measured through liquid), the contact footprint area on the electrode is:
   $$A_{\text{contact}} = \pi R_{\text{base}}^2 = \pi R_b^2 \sin^2\theta$$
   The optical projected area (shadow seen from top view) is:
   $$A_{\text{projected}} = \pi R_b^2$$
   For a hydrophilic electrode with $\theta = 30^\circ$:
   $$\frac{A_{\text{contact}}}{A_{\text{projected}}} = \sin^2(30^\circ) = 0.25$$
   Thus, the optical coverage seen by a camera is automatically **$4\times$ higher** than the catalytic contact area screening the electrode!

2. **3D Expanded-Metal Porous Geometry vs. Planar Foil:**
   - Vogt's correlation is derived from planar, smooth electrodes where bubbles detach freely into the bulk.
   - Rox et al. used expanded-mesh porous nickel (EM_500). In a 3D mesh, bubbles nucleate within the internal struts and openings. The optical field of view integrates all bubbles across the entire 3D depth of the electrode, obscuring the line of sight.

3. **Plume Contamination (Detached Rising Bubbles):**
   Rox's top-view camera captures all detached bubbles rising in the boundary layer between the electrode and the optical window. At low flow velocities ($0\text{--}5\text{ ml/min}$), detached bubbles remain in the near-wall plume for several tenths of a second, occluding 100% of the light while having zero active-area shielding effect on the electrode.

```
                  OPTICAL TOP-VIEW (Rox A_cov)
                        │   │   │   │  (Illumination / Camera)
                        ▼   ▼   ▼   ▼
             ┌─────────────────────────────┐  Observation Window
             │   ◌    Detached rising      │
             │     ◌    bubbles in plume   │  ──> 100% Projected Shadow
             │  (●)  (●)  (●)  (●)  (●)    │
  ═══════════╧═══╧════╧════╧════╧════╧═════╧  Electrode Surface
                 ▲    ▲    ▲    ▲    ▲
              Catalytic Contact Footprints (Vogt Θ ≈ 15%)
```

#### 3.3 Specific Analysis to Settle the Discrepancy
To formally settle this in the manuscript, the study must execute the following protocol:
1. **Dual Extraction in VOF:** From the interface-resolved CFD, simultaneously extract:
   - $\Theta_{\text{adh}}(t) = \frac{\sum \pi R_{\text{base},i}^2}{A_{\text{geom}}}$ (catalytic contact coverage)
   - $A_{\text{cov,proj}}(t) = \frac{\text{Area}\left(\bigcup \text{Shadow}_i\right)}{A_{\text{geom}}}$ (synthetic top-view projected shadow)
2. **Plume Residence Time Integration:** Calculate the optical shadow contribution of rising bubbles based on terminal slip velocity $u_{\text{rise}} = \frac{2}{9}\frac{\rho_l g R_b^2}{\mu_l}$.
3. **Outcome:** Plotting both $\Theta_{\text{adh}}(j)$ and $A_{\text{cov,proj}}(j)$ on the same axis will show that a single underlying physical bubble population produces $\Theta \approx 0.15$ and $A_{\text{cov}} \approx 0.85$, fully reconciling Vogt with Rox.

---

### Q4 — Is the MD plan capable of delivering a usable contact angle?

#### 4.1 Force Field & Chemistry Realism
- **Water Model:** SPC/E with SHAKE constraints is appropriate for liquid-state properties, dielectric screening, and double-layer electrostatics.
- **Electrode Model:** Non-reactive Ni(111) with `fix electrode/conp` allows dynamically fluctuating Gaussian charges that maintain a strict equipotential surface.
- **Physical Limitation:** Classical MD cannot capture chemical reaction steps, covalent bond formation ($\text{Ni-H}_{\text{ads}}$), surface oxide/hydroxide formation ($\text{Ni(OH)}_2$), or specific ion chemisorption.
- **Auditor Assessment:** `fix electrode/conp` captures the **pure electrostatic double-layer electrowetting effect** ($\Delta \cos\theta \propto C_{\text{dl}} \Delta\Psi^2$). It does not capture chemisorption-induced wettability changes. This is acceptable provided it is explicitly declared as the *electrostatic component of potential-dependent wettability*.

#### 4.2 The Line-Tension Extrapolation Error (Cylindrical Cap Geometry)
The original design specified fitting:
$$\cos\theta(R) = \cos\theta_\infty - \frac{\tau}{\gamma_{\text{lv}} R}$$
using 3 base radii ($R = 3, 5, 8\text{ nm}$) on a cylindrical (quasi-2D) nanobubble.

*Physical Analysis:*
- The modified Young equation with line tension $\tau$ arises from the geodesic curvature of the triple contact line:
  $$\cos\theta = \cos\theta_\infty - \frac{\tau}{\gamma_{\text{lv}}} \kappa_{\text{line}}$$
- For a spherical droplet/bubble, the contact line is a circle of radius $r_c$, so $\kappa_{\text{line}} = 1/r_c = 1/(R \sin\theta)$.
- For a **cylindrical cap periodic along its cylinder axis**, the contact lines are **two parallel straight lines**. The contact line curvature is strictly:
  $$\kappa_{\text{line}} \equiv 0$$
- **Auditor Ruling:** In a periodic cylindrical cap, **line tension does not produce a $1/R$ contact angle dependence**. Cylindrical caps are specifically used in the literature to *eliminate* line tension effects. Attempting to fit a $1/R$ curve to cylindrical droplets of different sizes is a severe physical error that would mistake periodic boundary interactions and finite-size box confinement for physical line tension.
- **Mandatory Correction:** Eliminate the $1/R$ line-tension fit. Sizing the simulation box with adequate lateral and vertical dimensions ($L_x \ge 12\text{ nm}$, $L_z \ge 15\text{ nm}$) and verifying box-size convergence across $L_x \in \{8, 12, 16\}\text{ nm}$ provides the true macroscopic Young contact angle $\theta_Y(\Delta\Psi)$.

#### 4.3 Static Equilibrium Angle vs. Dynamic Advancing/Receding Angles
- **Continuum Requirement:** OpenFOAM VOF requires dynamic contact angle conditions (`dynamicAlphaContactAngle`) with advancing ($\theta_A$) and receding ($\theta_R$) angles to model contact line pinning and sliding under shear flow.
- **MD Capability:** Static MD of an atomistically smooth crystal produces only the equilibrium Young contact angle $\theta_{\text{eq}}(\Delta\Psi)$. MD cannot predict macroscopic contact angle hysteresis ($\Delta\theta = \theta_A - \theta_R$) caused by surface roughness and chemical heterogeneity.
- **Coupling Contract Specification:** MD provides the **equilibrium reference angle $\theta_{\text{eq}}(\Delta\Psi)$ and its potential derivative $\frac{d\theta}{d\Delta\Psi}$**. Dynamic contact angles in VOF must be constructed using established empirical hysteresis offsets anchored to literature (e.g., Han/Mutschke E15 for Ni in KOH):
  $$\theta_A(\Delta\Psi) = \theta_{\text{eq}}(\Delta\Psi) + \Delta\theta_A, \quad \theta_R(\Delta\Psi) = \theta_{\text{eq}}(\Delta\Psi) - \Delta\theta_R$$

---

### Q5 — Computational Budget Realism

#### 5.1 Analysis of Computational Bottlenecks
The project operates under strict constraints: WSL2, 16 physical CPU cores, 23 GB RAM, no GPU.

1. **MD Campaign Throughput:**
   - Single-rank conp throughput on 4006 atoms was measured at $132.8\text{ katom-step/s}$.
   - For a 25k-atom system on 1 rank:
     $$\text{Throughput} = \frac{132.8\text{ katom-step/s}}{25\text{ katom}} = 5.31\text{ steps/s} \approx 0.459\text{ M steps/day} = 0.918\text{ ns/day (at 2 fs)}$$
   - A $15\text{ ns}$ production run requires:
     $$t_{\text{wall}} = \frac{15\text{ ns}}{0.918\text{ ns/day}} \approx \mathbf{16.3\text{ days per case}}$$
   - Because MD state points are embarrassingly parallel, running **12 concurrent single-rank jobs** utilizes 12 cores simultaneously and finishes the entire 12-case matrix in **~16.3 days wall-clock time**.
   - Memory footprint for 12 jobs $\approx 12 \times 250\text{ MB} = 3.0\text{ GB} \ll 23\text{ GB}$.

2. **VOF Campaign Bottlenecks:**
   - In VOF, the physical bubble growth time scales inversely with current density: $t_{\text{growth}} \propto 1/j$.
   - At $j = 10^4\text{ A m}^{-2}$, growth to departure takes $\sim 50\text{ ms}$ ($\sim 1.5 \times 10^5$ steps, $\sim 4.9\text{ h}$).
   - At $j = 100\text{ A m}^{-2}$, growing a bubble from nucleation to $R_{\text{det}} \approx 120\,\mu\text{m}$ takes **$\sim 5.7\text{ seconds}$ of physical time**. At $\Delta t \approx 3.3 \times 10^{-7}\text{ s}$, this requires **$1.7 \times 10^7$ timesteps**, costing **$193.8\text{ hours}$ (~8 days) per case**.
   - The three $j = 100\text{ A m}^{-2}$ cases alone consume $3 \times 193.8\text{ h} = \mathbf{581.4\text{ h}}$ (33% of the entire project budget).

#### 5.2 Case Triage & Recommended Cuts
To guarantee completion within a realistic execution window, the following prioritization must be enforced:

| Priority | Cut Target | Computational Savings | Physics Justification |
|---|---|---|---|
| **Cut 1** | Full growth at $j = 100\text{ A m}^{-2}$ (`VOF-F-j100-*`) | **~500 core-hours** | At $100\text{ A m}^{-2}$, growth is purely quasi-static and diffusion-controlled. Replace unseeded $5.7\text{ s}$ runs with bubbles **seeded at $0.90 R_{\text{det}}$**, simulating only the final detachment phase ($< 0.1\text{ s}$). |
| **Cut 2** | Low-priority MD OFAT arms (`MD-4-c20-*`, `MD-5-T*`) | **~2800 core-hours** | P1 depends exclusively on the $\Delta\Psi$ axis at standard operating conditions ($30\text{ wt\% KOH}, 333\text{ K}$). The concentration and temperature sensitivity sweeps can be truncated without compromising the primary thesis. |
| **Cut 3** | Second 3D VOF case (`VOF3D-j2000-*`) | **72 core-hours** | Run one contrasting 3D corner ($j = 10^4\text{ A m}^{-2}, \theta = 150^\circ$) to bound axisymmetry. Defer the second 3D corner to post-submission maintenance. |

---

### Q6 — Standing questions

#### (a) What would a hostile Reviewer 2 attack first in this problem definition?

1. **The "Derived Coverage" Claim vs. Nucleation Site Density ($N_{\text{site}}$):**
   *Reviewer Attack:* "The authors claim to derive a bubble-coverage closure $\Theta(j, v, \theta)$ from interface-resolved simulations. However, macroscopic coverage is an ensemble property determined by active nucleation site density $N_{\text{site}}$, surface roughness, micro-cavity size distribution, and bubble-bubble coalescence. A single-bubble axisymmetric simulation cannot predict $N_{\text{site}}$. Because $N_{\text{site}}$ is supplied as an external empirical parameter, the closure is merely a single-bubble detachment volume multiplied by an empirical correlation, not an ab initio derived coverage closure."
   *Defense:* The manuscript must explicitly frame the deliverable as: *"deriving the wettability-dependent detachment volume and residence time factors of the closure, with nucleation site density explicitly declared as an external parameter."*

2. **Idealized Ni(111) vs. Real Operational Alkaline Cathodes:**
   *Reviewer Attack:* "The MD uses an atomically flat, unreactive Ni(111) single crystal with classical SPC/E water. In real alkaline water electrolysis at cathodic overpotentials, the nickel surface is covered with adsorbed hydrogen ($\text{Ni-H}_{\text{ads}}$) and operates in the presence of surface hydrides and electrolyte impurities. Classical MD with fixed Lennard-Jones parameters cannot capture the electrochemistry of the electrode."
   *Defense:* State transparently that MD isolates the *electrostatic double-layer electrowetting contribution* under clean, idealized conditions, establishing a baseline potential-response curve.

3. **Marangoni Effect Magnitude in Water Electrolysis:**
   *Reviewer Attack:* "The authors construct an elaborate 'applicability map' based on solutal Marangoni forces. But for electrolytic $\text{H}_2$ bubbles in aqueous KOH, $\partial\gamma/\partial c_{\text{H}_2}$ is negligible and capillary retention forces exceed Marangoni forces by $100\text{--}1000\times$. The claimed Marangoni-dominated regime is a theoretical fiction."
   *Defense:* Use the scaling analysis developed in Q2 to show that the applicability map is designed to *test and bound* this assertion, and that proving capillary dominance ($\Lambda \gg 1$) across the industrial envelope is a valuable, field-clarifying result.

---

#### (b) Which planned result is most likely to be an artefact of a numerical choice rather than physics?

1. **The Location of the Marangoni Applicability Boundary ($\Lambda = 1$):**
   In OpenFOAM VOF (`interIsoFoam`), implementing a solutal Marangoni stress requires computing tangential surface gradients $\nabla_s \gamma = \frac{\partial\gamma}{\partial c} \nabla_s c$ across a diffuse interface of width $2\text{--}3\Delta x$.
   - Numerical parasitic currents (spurious velocities) generated by the Continuum Surface Force (CSF) model at high surface tension gradients frequently reach velocities of $0.01\text{--}0.1\text{ m s}^{-1}$.
   - These spurious currents can artificially mimic or distort physical Marangoni circulation cells.
   - Any predicted numerical transition boundary $\Lambda(j, v) = 1$ is at severe risk of being an artefact of the mesh resolution $\Delta x$, the interface compression scheme, and the assumed value of $\partial\gamma/\partial c_{\text{H}_2}$.

2. **Axisymmetric Suppression of Asymmetric Departure Modes:**
   The axisymmetric 2D wedge geometry forces the bubble to grow and detach symmetrically along the central axis. In real 3D cross-flow, shear flow induces asymmetric contact-line depinning, vortex shedding, and bubble tilting, which cause departure at significantly smaller radii than predicted by 2D axisymmetric models.

---

#### (c) What is claimed more strongly than the evidence supports?

1. **"Deriving a bubble coverage closure from molecular dynamics":**
   *Evidence:* MD provides an equilibrium contact angle $\theta_{\text{eq}}(\Delta\Psi)$ on an idealized flat surface. It does not provide dynamic hysteresis, nucleation density, or bubble departure hydrodynamics.
   *Correction:* The study couples an MD-informed contact angle into a continuum VOF model to derive the *wettability-dependent departure mechanics*.

2. **"Resolving the Vogt vs. Rox discrepancy":**
   *Evidence:* Rox 2022 is an optical projected-area measurement on a porous 3D mesh electrode with $\pm 50\%$ timing error and a 20% resolution floor.
   *Correction:* The study demonstrates that geometric projection effects and plume retention explain why optical coverage ($A_{\text{cov}} \approx 0.8\text{--}1.0$) inherently departs from active catalytic contact coverage ($\Theta \approx 0.15$), rather than claiming to "refute" either experimental study.

3. **"Universal applicability map for wettability closures":**
   *Evidence:* The map is computed for a single bubble in clean KOH electrolyte without surfactants.
   *Correction:* The map must be explicitly scoped to clean, single-bubble alkaline electrolysis on smooth electrodes.

---

## Actionable Requirements for Subsequent Phases

1. **Phase 2 (Theory & VOF Setup):**
   - Implement the current-conserving Faradaic flux: $\dot{n}_{\text{H}_2,\text{exposed}} = \frac{j}{2F(1-\Theta)}$ in VOF.
   - Enforce box-size convergence for planar MD contact angles; remove all references to $1/R$ line-tension fitting for cylindrical caps.
   - Formally verify the solutal Marangoni implementation against an analytical thermocapillary benchmark (`VOF-000b-thermocap`) before executing the P3 campaign.
2. **Phase 3 (MD Production):**
   - Execute the 12 primary $\theta(\Delta\Psi)$ state points as concurrent 1-rank jobs on 12–16 physical cores.
   - Discard the low-priority concentration and temperature OFAT arms if runtime exceeds 18 days.
3. **Phase 4 (VOF Production & Closure):**
   - Seed the low-current cases ($j = 100\text{ A m}^{-2}$) at $0.90 R_{\text{det}}$ to avoid spending 580 core-hours on quasi-static bubble growth.
   - Extract and report both $\Theta_{\text{adh}}$ (catalytic contact area) and $A_{\text{cov,proj}}$ (optical projected area) to resolve the Rox/Vogt tension.
4. **Phase 5 (Cell Model & Manuscript):**
   - In `reactingMultiphaseEulerFoam`, ensure the near-wall boundary condition does not double-count adhering gas in $\sigma_{\text{eff}}$ and $\Theta$.
   - Scope all gap claims to *"within the open-source continuum modelling literature"*.

---
**Auditor Signature:** *AGY Physics & Modelling Auditor*  
**Status:** Report complete and logged to `/home/azan/research/T12_MD_wettability_closure/70_audit/AUDIT_RESPONSE_AGY_1.md`.
