"""Seed script for chemical database - 30+ chemicals"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.orm import Session
from src.database import Base, engine, SessionLocal
from src.models.chemical import Chemical

CHEMICALS = [
    # 1. Sulfuric Acid
    {"cas_number": "7664-93-9", "name": "Sulfuric Acid", "formula": "H2SO4", "molecular_weight": 98.079,
     "boiling_point_c": 337.0, "liquid_density_kg_m3": 1840.0, "gas_density_ratio": 2.29,
     "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "8 (Corrosive)", "un_number": "UN1830",
     "erpg_1_ppm": 2.0, "erpg_2_ppm": 20.0, "erpg_3_ppm": 200.0,
     "idlh_ppm": 30.0, "pel_ppm": 1.0},

    # 2. Ammonia
    {"cas_number": "7664-41-7", "name": "Ammonia", "formula": "NH3", "molecular_weight": 17.031,
     "boiling_point_c": -33.34, "gas_density_kg_m3": 0.73, "gas_density_ratio": 0.597,
     "state_at_ambient": "gas", "is_heavier_than_air": False,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1005",
     "erpg_1_ppm": 25.0, "erpg_2_ppm": 200.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 300.0, "pel_ppm": 50.0,
     "lel_percent": 15.0, "uel_percent": 28.0},

    # 3. Hydrogen Chloride
    {"cas_number": "7647-01-0", "name": "Hydrogen Chloride", "formula": "HCl", "molecular_weight": 36.461,
     "boiling_point_c": -85.05, "gas_density_kg_m3": 1.49, "gas_density_ratio": 1.22,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "8 (Corrosive)", "un_number": "UN1050",
     "erpg_1_ppm": 3.0, "erpg_2_ppm": 20.0, "erpg_3_ppm": 100.0,
     "idlh_ppm": 50.0, "pel_ppm": 5.0},

    # 4. Chlorine
    {"cas_number": "7782-50-5", "name": "Chlorine", "formula": "Cl2", "molecular_weight": 70.906,
     "boiling_point_c": -34.0, "gas_density_kg_m3": 2.95, "gas_density_ratio": 2.41,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1017",
     "erpg_1_ppm": 1.0, "erpg_2_ppm": 3.0, "erpg_3_ppm": 20.0,
     "idlh_ppm": 10.0, "pel_ppm": 1.0, "tlv_twa_ppm": 0.5,
     "aegl_1_10min_ppm": 0.5, "aegl_1_60min_ppm": 0.5,
     "aegl_2_10min_ppm": 2.0, "aegl_2_60min_ppm": 1.0,
     "aegl_3_10min_ppm": 10.0, "aegl_3_60min_ppm": 5.0},

    # 5. Formaldehyde
    {"cas_number": "50-00-0", "name": "Formaldehyde", "formula": "CH2O", "molecular_weight": 30.026,
     "boiling_point_c": -19.0, "gas_density_kg_m3": 1.08, "gas_density_ratio": 1.04,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1198",
     "erpg_1_ppm": 1.0, "erpg_2_ppm": 10.0, "erpg_3_ppm": 78.0,
     "idlh_ppm": 20.0, "pel_ppm": 0.75,
     "lel_percent": 7.0, "uel_percent": 73.0},

    # 6. Hydrogen Fluoride
    {"cas_number": "7664-39-3", "name": "Hydrogen Fluoride", "formula": "HF", "molecular_weight": 20.006,
     "boiling_point_c": 19.5, "gas_density_kg_m3": 0.878, "gas_density_ratio": 0.708,
     "state_at_ambient": "gas", "is_heavier_than_air": False,
     "hazard_class": "8 (Corrosive)", "un_number": "UN1052",
     "erpg_1_ppm": 2.0, "erpg_2_ppm": 20.0, "erpg_3_ppm": 50.0,
     "idlh_ppm": 30.0, "pel_ppm": 3.0,
     "aegl_1_10min_ppm": 1.0, "aegl_1_60min_ppm": 1.0,
     "aegl_2_10min_ppm": 20.0, "aegl_2_60min_ppm": 7.0,
     "aegl_3_10min_ppm": 50.0, "aegl_3_60min_ppm": 20.0},

    # 7. Hydrogen Sulfide
    {"cas_number": "7783-06-4", "name": "Hydrogen Sulfide", "formula": "H2S", "molecular_weight": 34.08,
     "boiling_point_c": -60.0, "gas_density_kg_m3": 1.36, "gas_density_ratio": 1.17,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1053",
     "erpg_1_ppm": 0.1, "erpg_2_ppm": 30.0, "erpg_3_ppm": 100.0,
     "idlh_ppm": 50.0, "pel_ppm": 20.0,
     "lel_percent": 4.3, "uel_percent": 46.0},

    # 8. Phosgene
    {"cas_number": "75-44-5", "name": "Phosgene", "formula": "COCl2", "molecular_weight": 98.916,
     "boiling_point_c": 8.3, "gas_density_kg_m3": 3.93, "gas_density_ratio": 3.35,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1076",
     "erpg_1_ppm": 0.2, "erpg_2_ppm": 0.5, "erpg_3_ppm": 1.5,
     "idlh_ppm": 2.0, "pel_ppm": 0.1,
     "aegl_1_10min_ppm": 0.2, "aegl_1_60min_ppm": 0.2,
     "aegl_2_10min_ppm": 0.5, "aegl_2_60min_ppm": 0.4,
     "aegl_3_10min_ppm": 1.5, "aegl_3_60min_ppm": 0.8},

    # 9. Benzene
    {"cas_number": "71-43-2", "name": "Benzene", "formula": "C6H6", "molecular_weight": 78.114,
     "boiling_point_c": 80.1, "liquid_density_kg_m3": 876.5, "vapor_pressure_kpa": 10.0,
     "gas_density_ratio": 2.7, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1114",
     "erpg_1_ppm": 50.0, "erpg_2_ppm": 150.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 500.0, "pel_ppm": 1.0, "tlv_twa_ppm": 0.5,
     "lel_percent": 1.2, "uel_percent": 7.8},

    # 10. Toluene
    {"cas_number": "108-88-3", "name": "Toluene", "formula": "C7H8", "molecular_weight": 92.141,
     "boiling_point_c": 110.6, "liquid_density_kg_m3": 866.9, "vapor_pressure_kpa": 3.8,
     "gas_density_ratio": 3.18, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1294",
     "erpg_1_ppm": 50.0, "erpg_2_ppm": 300.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 2000.0, "pel_ppm": 200.0,
     "lel_percent": 1.2, "uel_percent": 7.1},

    # 11. Methanol
    {"cas_number": "67-56-1", "name": "Methanol", "formula": "CH3OH", "molecular_weight": 32.042,
     "boiling_point_c": 64.7, "liquid_density_kg_m3": 791.0, "vapor_pressure_kpa": 13.0,
     "gas_density_ratio": 1.11, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1230",
     "erpg_1_ppm": 200.0, "erpg_2_ppm": 1000.0, "erpg_3_ppm": 5000.0,
     "idlh_ppm": 6000.0, "pel_ppm": 200.0,
     "lel_percent": 6.0, "uel_percent": 36.0},

    # 12. Ethylene Oxide
    {"cas_number": "75-21-8", "name": "Ethylene Oxide", "formula": "C2H4O", "molecular_weight": 44.053,
     "boiling_point_c": 10.7, "gas_density_kg_m3": 1.52, "gas_density_ratio": 1.49,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1040",
     "erpg_1_ppm": 20.0, "erpg_2_ppm": 50.0, "erpg_3_ppm": 500.0,
     "idlh_ppm": 800.0, "pel_ppm": 1.0,
     "lel_percent": 3.0, "uel_percent": 100.0},

    # 13. Methyl Isocyanate
    {"cas_number": "624-83-9", "name": "Methyl Isocyanate", "formula": "C2H3NO", "molecular_weight": 57.051,
     "boiling_point_c": 39.1, "liquid_density_kg_m3": 923.0, "vapor_pressure_kpa": 48.0,
     "gas_density_ratio": 1.95, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid), 6.1 (Toxic)", "un_number": "UN2480",
     "erpg_1_ppm": 0.025, "erpg_2_ppm": 0.5, "erpg_3_ppm": 5.0,
     "idlh_ppm": 3.0, "pel_ppm": 0.02,
     "lel_percent": 5.3, "uel_percent": 26.0},

    # 14. Acrylonitrile
    {"cas_number": "107-13-1", "name": "Acrylonitrile", "formula": "C3H3N", "molecular_weight": 53.063,
     "boiling_point_c": 77.0, "liquid_density_kg_m3": 806.0, "vapor_pressure_kpa": 11.0,
     "gas_density_ratio": 1.83, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid), 6.1 (Toxic)", "un_number": "UN1093",
     "erpg_1_ppm": 10.0, "erpg_2_ppm": 35.0, "erpg_3_ppm": 150.0,
     "idlh_ppm": 85.0, "pel_ppm": 2.0,
     "lel_percent": 3.0, "uel_percent": 17.0},

    # 15. Vinyl Chloride
    {"cas_number": "75-01-4", "name": "Vinyl Chloride", "formula": "C2H3Cl", "molecular_weight": 62.498,
     "boiling_point_c": -13.4, "gas_density_kg_m3": 2.15, "gas_density_ratio": 2.15,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.1 (Flammable Gas)", "un_number": "UN1086",
     "erpg_1_ppm": 500.0, "erpg_2_ppm": 5000.0, "erpg_3_ppm": 20000.0,
     "idlh_ppm": 150.0, "pel_ppm": 1.0,
     "lel_percent": 3.6, "uel_percent": 33.0},

    # 16. Carbon Monoxide
    {"cas_number": "630-08-0", "name": "Carbon Monoxide", "formula": "CO", "molecular_weight": 28.01,
     "boiling_point_c": -191.5, "gas_density_kg_m3": 1.15, "gas_density_ratio": 0.94,
     "state_at_ambient": "gas", "is_heavier_than_air": False,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1016",
     "erpg_1_ppm": 50.0, "erpg_2_ppm": 200.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 1200.0, "pel_ppm": 50.0,
     "lel_percent": 12.5, "uel_percent": 74.0},

    # 17. Sulfur Dioxide
    {"cas_number": "7446-09-5", "name": "Sulfur Dioxide", "formula": "SO2", "molecular_weight": 64.066,
     "boiling_point_c": -10.0, "gas_density_kg_m3": 2.62, "gas_density_ratio": 2.22,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1079",
     "erpg_1_ppm": 0.2, "erpg_2_ppm": 3.0, "erpg_3_ppm": 15.0,
     "idlh_ppm": 100.0, "pel_ppm": 5.0,
     "aegl_1_10min_ppm": 0.2, "aegl_1_60min_ppm": 0.2,
     "aegl_2_10min_ppm": 0.75, "aegl_2_60min_ppm": 0.5,
     "aegl_3_10min_ppm": 15.0, "aegl_3_60min_ppm": 7.0},

    # 18. Nitrogen Dioxide
    {"cas_number": "10102-44-0", "name": "Nitrogen Dioxide", "formula": "NO2", "molecular_weight": 46.006,
     "boiling_point_c": 21.2, "gas_density_kg_m3": 1.88, "gas_density_ratio": 1.58,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN1067",
     "erpg_1_ppm": 1.0, "erpg_2_ppm": 10.0, "erpg_3_ppm": 30.0,
     "idlh_ppm": 20.0, "pel_ppm": 5.0,
     "aegl_1_10min_ppm": 1.0, "aegl_1_60min_ppm": 0.5,
     "aegl_2_10min_ppm": 10.0, "aegl_2_60min_ppm": 5.0,
     "aegl_3_10min_ppm": 30.0, "aegl_3_60min_ppm": 17.0},

    # 19. Ethylene
    {"cas_number": "74-85-1", "name": "Ethylene", "formula": "C2H4", "molecular_weight": 28.054,
     "boiling_point_c": -103.7, "gas_density_kg_m3": 1.15, "gas_density_ratio": 0.97,
     "state_at_ambient": "gas", "is_heavier_than_air": False,
     "hazard_class": "2.1 (Flammable Gas)", "un_number": "UN1962",
     "erpg_1_ppm": 1000.0, "erpg_2_ppm": 5000.0, "erpg_3_ppm": 10000.0,
     "lel_percent": 2.7, "uel_percent": 36.0},

    # 20. Propylene
    {"cas_number": "115-07-1", "name": "Propylene", "formula": "C3H6", "molecular_weight": 42.081,
     "boiling_point_c": -47.6, "gas_density_kg_m3": 1.74, "gas_density_ratio": 1.42,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.1 (Flammable Gas)", "un_number": "UN1077",
     "erpg_1_ppm": 5000.0, "erpg_2_ppm": 10000.0, "erpg_3_ppm": 20000.0,
     "lel_percent": 2.0, "uel_percent": 11.0},

    # 21. n-Butane
    {"cas_number": "106-97-8", "name": "n-Butane", "formula": "C4H10", "molecular_weight": 58.124,
     "boiling_point_c": -0.5, "gas_density_kg_m3": 2.48, "gas_density_ratio": 2.03,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.1 (Flammable Gas)", "un_number": "UN1011",
     "erpg_1_ppm": 16000.0, "erpg_2_ppm": 40000.0, "erpg_3_ppm": 100000.0,
     "lel_percent": 1.8, "uel_percent": 8.4},

    # 22. Propane
    {"cas_number": "74-98-6", "name": "Propane", "formula": "C3H8", "molecular_weight": 44.097,
     "boiling_point_c": -42.0, "gas_density_kg_m3": 1.8, "gas_density_ratio": 1.47,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.1 (Flammable Gas)", "un_number": "UN1978",
     "erpg_1_ppm": 8000.0, "erpg_2_ppm": 16000.0, "erpg_3_ppm": 40000.0,
     "lel_percent": 2.1, "uel_percent": 9.5},

    # 23. Hydrogen Cyanide
    {"cas_number": "74-90-8", "name": "Hydrogen Cyanide", "formula": "HCN", "molecular_weight": 27.026,
     "boiling_point_c": 25.6, "gas_density_kg_m3": 0.94, "gas_density_ratio": 0.94,
     "state_at_ambient": "gas", "is_heavier_than_air": False,
     "hazard_class": "3 (Flammable Liquid), 6.1 (Toxic)", "un_number": "UN1051",
     "erpg_1_ppm": 2.5, "erpg_2_ppm": 10.0, "erpg_3_ppm": 25.0,
     "idlh_ppm": 50.0, "pel_ppm": 10.0,
     "lel_percent": 5.6, "uel_percent": 40.0},

    # 24. Anhydrous Ammonia (duplicate handled by CAS - skip, Ammonia already covers)
    # Use Methylamine instead
    {"cas_number": "74-89-5", "name": "Methylamine", "formula": "CH3NH2", "molecular_weight": 31.057,
     "boiling_point_c": -6.3, "gas_density_kg_m3": 1.03, "gas_density_ratio": 1.07,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.1 (Flammable Gas)", "un_number": "UN1061",
     "erpg_1_ppm": 10.0, "erpg_2_ppm": 100.0, "erpg_3_ppm": 500.0,
     "idlh_ppm": 100.0, "pel_ppm": 10.0,
     "lel_percent": 4.9, "uel_percent": 20.8},

    # 25. Dimethyl Sulfide
    {"cas_number": "75-18-3", "name": "Dimethyl Sulfide", "formula": "C2H6S", "molecular_weight": 62.134,
     "boiling_point_c": 37.0, "liquid_density_kg_m3": 846.0, "vapor_pressure_kpa": 53.0,
     "gas_density_ratio": 2.14, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1164",
     "erpg_1_ppm": 0.5, "erpg_2_ppm": 100.0, "erpg_3_ppm": 500.0,
     "lel_percent": 2.2, "uel_percent": 19.7},

    # 26. n-Hexane
    {"cas_number": "110-54-3", "name": "n-Hexane", "formula": "C6H14", "molecular_weight": 86.178,
     "boiling_point_c": 68.7, "liquid_density_kg_m3": 655.0, "vapor_pressure_kpa": 17.0,
     "gas_density_ratio": 2.97, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1208",
     "erpg_1_ppm": 500.0, "erpg_2_ppm": 2500.0, "erpg_3_ppm": 16000.0,
     "idlh_ppm": 5000.0, "pel_ppm": 500.0,
     "lel_percent": 1.1, "uel_percent": 7.5},

    # 27. Xylene
    {"cas_number": "1330-20-7", "name": "Xylene (Mixed)", "formula": "C8H10", "molecular_weight": 106.165,
     "boiling_point_c": 140.0, "liquid_density_kg_m3": 870.0, "vapor_pressure_kpa": 1.1,
     "gas_density_ratio": 3.66, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1307",
     "erpg_1_ppm": 100.0, "erpg_2_ppm": 300.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 900.0, "pel_ppm": 100.0,
     "lel_percent": 1.0, "uel_percent": 7.0},

    # 28. Styrene
    {"cas_number": "100-42-5", "name": "Styrene", "formula": "C8H8", "molecular_weight": 104.149,
     "boiling_point_c": 145.0, "liquid_density_kg_m3": 909.0, "vapor_pressure_kpa": 0.85,
     "gas_density_ratio": 3.59, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN2055",
     "erpg_1_ppm": 50.0, "erpg_2_ppm": 250.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 700.0, "pel_ppm": 100.0,
     "lel_percent": 0.9, "uel_percent": 6.8},

    # 29. Epichlorohydrin
    {"cas_number": "106-89-8", "name": "Epichlorohydrin", "formula": "C3H5ClO", "molecular_weight": 92.517,
     "boiling_point_c": 118.0, "liquid_density_kg_m3": 1179.0, "vapor_pressure_kpa": 2.1,
     "gas_density_ratio": 3.19, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid), 6.1 (Toxic)", "un_number": "UN2023",
     "erpg_1_ppm": 2.0, "erpg_2_ppm": 20.0, "erpg_3_ppm": 100.0,
     "idlh_ppm": 75.0, "pel_ppm": 5.0},

    # 30. Chlorobenzene
    {"cas_number": "108-90-7", "name": "Chlorobenzene", "formula": "C6H5Cl", "molecular_weight": 112.558,
     "boiling_point_c": 131.0, "liquid_density_kg_m3": 1106.0, "vapor_pressure_kpa": 1.2,
     "gas_density_ratio": 3.88, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1134",
     "erpg_1_ppm": 50.0, "erpg_2_ppm": 200.0, "erpg_3_ppm": 1000.0,
     "pel_ppm": 75.0, "lel_percent": 1.3, "uel_percent": 9.6},

    # 31. Ethylbenzene
    {"cas_number": "100-41-4", "name": "Ethylbenzene", "formula": "C8H10", "molecular_weight": 106.165,
     "boiling_point_c": 136.2, "liquid_density_kg_m3": 867.0, "vapor_pressure_kpa": 1.33,
     "gas_density_ratio": 3.66, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "3 (Flammable Liquid)", "un_number": "UN1175",
     "erpg_1_ppm": 50.0, "erpg_2_ppm": 200.0, "erpg_3_ppm": 1000.0,
     "idlh_ppm": 800.0, "pel_ppm": 100.0,
     "lel_percent": 0.8, "uel_percent": 6.7},

    # 32. Nitric Acid
    {"cas_number": "7697-37-2", "name": "Nitric Acid", "formula": "HNO3", "molecular_weight": 63.012,
     "boiling_point_c": 83.0, "liquid_density_kg_m3": 1512.0, "gas_density_ratio": 2.17,
     "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "8 (Corrosive), 5.1 (Oxidizer)", "un_number": "UN2031",
     "erpg_1_ppm": 1.0, "erpg_2_ppm": 6.0, "erpg_3_ppm": 78.0,
     "idlh_ppm": 25.0, "pel_ppm": 2.0},

    # 33. Phosphine
    {"cas_number": "7803-51-2", "name": "Phosphine", "formula": "PH3", "molecular_weight": 33.998,
     "boiling_point_c": -87.7, "gas_density_kg_m3": 1.38, "gas_density_ratio": 1.17,
     "state_at_ambient": "gas", "is_heavier_than_air": True,
     "hazard_class": "2.3 (Toxic Gas)", "un_number": "UN2199",
     "erpg_1_ppm": 0.5, "erpg_2_ppm": 3.0, "erpg_3_ppm": 10.0,
     "idlh_ppm": 50.0, "pel_ppm": 0.3,
     "lel_percent": 1.8, "uel_percent": 98.0},

    # 34. Bromine
    {"cas_number": "7726-95-6", "name": "Bromine", "formula": "Br2", "molecular_weight": 159.808,
     "boiling_point_c": 58.8, "liquid_density_kg_m3": 3102.0, "vapor_pressure_kpa": 28.0,
     "gas_density_ratio": 5.51, "state_at_ambient": "liquid", "is_heavier_than_air": True,
     "hazard_class": "8 (Corrosive)", "un_number": "UN1744",
     "erpg_1_ppm": 0.1, "erpg_2_ppm": 0.5, "erpg_3_ppm": 5.0,
     "idlh_ppm": 3.0, "pel_ppm": 0.1},
]


def seed_chemicals(db: Session) -> int:
    """Seed chemicals into database"""
    count = 0
    for chem_data in CHEMICALS:
        existing = db.query(Chemical).filter(Chemical.cas_number == chem_data["cas_number"]).first()
        if existing:
            continue
        chemical = Chemical(**chem_data)
        db.add(chemical)
        count += 1
    db.commit()
    return count


def main():
    """Main seeding function"""
    print("ToxZone Chemical Database Seeding")
    print("=" * 40)

    from src.database import init_db
    init_db()

    db = SessionLocal()
    try:
        count = seed_chemicals(db)
        print(f"Added {count} chemicals (total: {db.query(Chemical).count()})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
