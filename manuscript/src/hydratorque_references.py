# -*- coding: utf-8 -*-
"""Numbered reference library (Springer / numbered style). Every journal, proceedings and book-chapter entry was checked against Crossref (title, authors, volume, pages, DOI) on 4 November 2026;
the three patents were checked against the Google Patents record; standards are cited by designation and were not checked against the publishers' catalogs.
key: full entry (numbering follows order of first citation in the text)"""
LIB = {
    'Ghidaoui2005': 'M.S. Ghidaoui, M. Zhao, D.A. McInnis, D.H. Axworthy, A Review of Water Hammer Theory and Practice, Applied Mechanics Reviews 58 (2005) 49–76. https://doi.org/10.1115/1.1828050',
    'Benfer2016': 'M.E. Benfer, E. Forssell, J. Scheffey, Determination of Fire Hose Friction Loss Characteristics, Fire Technology 53 (2016) 1059–1075. https://doi.org/10.1007/s10694-016-0617-z',
    'Drago2017': 'J. Drago, W. Evans, Gauging the Force Effects of Valve Stem Packing on Valve Stem Actuation, ASME/NRC 2017 13th Pump and Valve Symposium (2017), paper PVS2017-3518. https://doi.org/10.1115/pvs2017-3518',
    'Majdic2019': 'F. Majdič, Influences on the Efficiency of a Water-Hydraulic Motor, Proceedings of the International Conference Fluid Power 2019, University of Maribor Press (2019) 89–96. https://doi.org/10.18690/978-961-286-300-5.7',
    'Majdic2021': 'F. Majdič, Research on the water hydraulic pressure relief valve, Proceedings of the International Conference Fluid Power 2021, University of Maribor Press (2021) 29–40. https://doi.org/10.18690/978-961-286-513-9.3',
    'Yang2015': 'L. Yang, S. Nie, S. Yin, J. Zhao, F. Yin, Numerical and experimental investigation on torque characteristics of seawater hydraulic axial piston motor for underwater tool system, Ocean Engineering 104 (2015) 168–184. https://doi.org/10.1016/j.oceaneng.2015.05.003',
    'Seabrook1994': 'C. Seabrook, C.R. Burrows, Water Hydraulics: Some Design Challenges, Fluid Power Systems and Technology, ASME IMECE 1994, pp. 59–63. https://doi.org/10.1115/imece1994-0683',
    'Nolan2017': 'D.P. Nolan, Sources of Firewater Pump Supply, Fire Pump Arrangements at Industrial Facilities (2017) 29–44. https://doi.org/10.1016/b978-0-12-813043-8.00005-1',
    'McKay1979': 'M.D. McKay, R.J. Beckman, W.J. Conover, Comparison of Three Methods for Selecting Values of Input Variables in the Analysis of Output from a Computer Code, Technometrics 21 (1979) 239–245. https://doi.org/10.1080/00401706.1979.10489755',
    'Helton2003': 'J. Helton, F. Davis, Latin hypercube sampling and the propagation of uncertainty in analyses of complex systems, Reliability Engineering & System Safety 81 (2003) 23–69. https://doi.org/10.1016/s0951-8320(03)00058-9',
    'Iman1982': 'R.L. Iman, W.J. Conover, A distribution-free approach to inducing rank correlation among input variables, Communications in Statistics - Simulation and Computation 11 (1982) 311–334. https://doi.org/10.1080/03610918208812265',
    'Saltelli2010': 'A. Saltelli, P. Annoni, I. Azzini, F. Campolongo, M. Ratto, S. Tarantola, Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index, Computer Physics Communications 181 (2010) 259–270. https://doi.org/10.1016/j.cpc.2009.09.018',
    'Oberkampf2002': 'W.L. Oberkampf, T.G. Trucano, Verification and validation in computational fluid dynamics, Progress in Aerospace Sciences 38 (2002) 209–272. https://doi.org/10.1016/s0376-0421(02)00005-2',
    'Deb2002': 'K. Deb, A. Pratap, S. Agarwal, T. Meyarivan, A fast and elitist multiobjective genetic algorithm: NSGA-II, IEEE Transactions on Evolutionary Computation 6 (2002) 182–197. https://doi.org/10.1109/4235.996017',
    'Marler2004': 'R. Marler, J. Arora, Survey of multi-objective optimization methods for engineering, Structural and Multidisciplinary Optimization 26 (2004) 369–395. https://doi.org/10.1007/s00158-003-0368-6',
    'Beyer2007': 'H.G. Beyer, B. Sendhoff, Robust optimization – A comprehensive survey, Computer Methods in Applied Mechanics and Engineering 196 (2007) 3190–3218. https://doi.org/10.1016/j.cma.2007.03.003',
    'Glasserman1992': 'P. Glasserman, D.D. Yao, Some Guidelines and Guarantees for Common Random Numbers, Management Science 38 (1992) 884–908. https://doi.org/10.1287/mnsc.38.6.884',
    'Olsen2024': 'A.A. Olsen, Manual Valve Operation, Access, Location and Orientation, Applying Physical Ergonomics to Modern Ship Design (2024) 45–54. https://doi.org/10.1007/978-3-031-57974-5_7',
    'Ahmad2016': 'B. Ahmad, N. Abdul Wahab, A. Abdul Rahman, Emergency shutdown valve reliability function test by automated partial stroke testing system, Jurnal Teknologi 78 (2016). https://doi.org/10.11113/jt.v78.9418',
    'Jackman1985': 'W. Jackman, Remote fire hydrant actuator, US Patent 4,561,459, published 31 December 1985. https://patents.google.com/patent/US4561459A/en',
    'Kolacz2014': 'D.J. Kolacz, S.G. McMillan, S.W. Akins, T.S. Miller, Portable remote controlled valve, US Patent 8,733,387 B2, Task Force Tips LLC, granted 27 May 2014. https://patents.google.com/patent/US8733387B2/en',
    'Leete1992': 'B.C. Leete, Rotary actuator and valve control system, US Patent 5,101,862, published 7 April 1992. https://patents.google.com/patent/US5101862A/en',
    'YPF2026': 'Wazoku (InnoCentive), A portable device for valve operations that require high torque (scouting challenge for YPF), https://www.innocentive.com/challenges/a-portable-device-for-valve-operations-that-require-high-torque/, accessed 4 November 2026.',
    'ISO12100': 'ISO 12100:2010, Safety of machinery — General principles for design — Risk assessment and risk reduction, International Organization for Standardization, Geneva, 2010.',
    'ISO5210': 'ISO 5210:2017, Industrial valves — Multi-turn valve actuator attachments, International Organization for Standardization, Geneva, 2017.',
    'ISO80079': 'ISO 80079-36:2016, Explosive atmospheres — Part 36: Non-electrical equipment for explosive atmospheres — Basic method and requirements, International Organization for Standardization, Geneva, 2016.',
    'NFPA291': 'NFPA 291, Recommended Practice for Fire Flow Testing and Marking of Hydrants, National Fire Protection Association, Quincy, MA (current edition).',
    'ASMEB1634': 'ASME B16.34, Valves — Flanged, Threaded, and Welding End, American Society of Mechanical Engineers, New York (current edition).',
}
