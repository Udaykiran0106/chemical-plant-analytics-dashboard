import matplotlib
matplotlib.use("Agg")

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# FOLDER

os.makedirs("dashboard", exist_ok=True)

# DATABASE CONNECTION

conn = sqlite3.connect("data/chemical_plant.db")

kpi = pd.read_sql("""
SELECT
    SUM(production_tons) AS total_production,
    ROUND(AVG(yield_percent), 2) AS avg_yield,
    ROUND(AVG(energy_kwh / production_tons), 2) AS avg_energy
FROM Production;
""", conn)

downtime_kpi = pd.read_sql("""
SELECT ROUND(SUM(downtime_hours), 1) AS total_downtime
FROM Downtime;
""", conn)

production_by_unit = pd.read_sql("""
SELECT u.unit_name, SUM(p.production_tons) AS production
FROM Production p
JOIN Units u ON p.unit_id = u.unit_id
GROUP BY u.unit_name;
""", conn)

energy_by_unit = pd.read_sql("""
SELECT u.unit_name,
       ROUND(AVG(p.energy_kwh / p.production_tons), 2) AS energy
FROM Production p
JOIN Units u ON p.unit_id = u.unit_id
GROUP BY u.unit_name;
""", conn)

downtime_by_unit = pd.read_sql("""
SELECT u.unit_name, SUM(d.downtime_hours) AS downtime
FROM Downtime d
JOIN Units u ON d.unit_id = u.unit_id
GROUP BY u.unit_name;
""", conn)

monthly_production = pd.read_sql("""
SELECT substr(date,1,7) AS month,
       SUM(production_tons) AS production
FROM Production
GROUP BY month;
""", conn)

quality_status = pd.read_sql("""
SELECT status, COUNT(*) AS count
FROM Quality
GROUP BY status;
""", conn)

conn.close()

# DASHBOARD SETUP

fig = plt.figure(figsize=(20, 12))
fig.suptitle(
    "Chemical Plant Operations Analytics Dashboard",
    fontsize=22, fontweight="bold"
)

# KPI TEXT

kpi_titles = ["Total Production (tons)", "Average Yield (%)",
              "Avg Energy (kWh/ton)", "Total Downtime (hrs)"]
kpi_values = [
    int(kpi["total_production"][0]),
    kpi["avg_yield"][0],
    kpi["avg_energy"][0],
    downtime_kpi["total_downtime"][0]
]

for i in range(4):
    ax = plt.subplot(3, 4, i + 1)
    ax.axis("off")
    ax.text(0.5, 0.55, kpi_values[i],
            fontsize=20, ha="center", va="center")
    ax.text(0.5, 0.30, kpi_titles[i],
            fontsize=11, ha="center", va="center")

# PRODUCTION BY UNIT

ax5 = plt.subplot(3, 4, 5)
ax5.bar(production_by_unit["unit_name"],
        production_by_unit["production"],
        color="#4C72B0")
ax5.set_title("Production by Unit", fontsize=11)
ax5.set_ylabel("Tons", fontsize=10)
ax5.tick_params(axis="x", labelrotation=15, labelsize=9)

# ENERGY BY UNIT

ax6 = plt.subplot(3, 4, 6)
ax6.bar(energy_by_unit["unit_name"],
        energy_by_unit["energy"],
        color="#55A868")
ax6.set_title("Energy Consumption by Unit", fontsize=11)
ax6.set_ylabel("kWh/ton", fontsize=10)
ax6.tick_params(axis="x", labelrotation=15, labelsize=9)

# DOWNTIME BY UNIT

ax7 = plt.subplot(3, 4, 7)
ax7.bar(downtime_by_unit["unit_name"],
        downtime_by_unit["downtime"],
        color="#C44E52")
ax7.set_title("Downtime by Unit", fontsize=11)
ax7.set_ylabel("Hours", fontsize=10)
ax7.tick_params(axis="x", labelrotation=15, labelsize=9)

# QUALITY STATUS

ax8 = plt.subplot(3, 4, 8)
ax8.pie(
    quality_status["count"],
    labels=quality_status["status"],
    autopct="%1.1f%%",
    startangle=90,
    textprops={"fontsize": 10}
)
ax8.set_title("Quality Status", fontsize=11)

# MONTHLY PRODUCTION TREND

ax9 = plt.subplot(3, 1, 3)
ax9.plot(
    monthly_production["month"],
    monthly_production["production"],
    marker="o", linewidth=2
)
ax9.set_title("Monthly Production Trend", fontsize=12)
ax9.set_xlabel("Month", fontsize=10)
ax9.set_ylabel("Production (tons)", fontsize=10)
ax9.tick_params(axis="x", labelsize=9)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("dashboard/chemical_plant_dashboard.png", dpi=200)
plt.close()


