# Intelligent Irrigation System - Kakira, Uganda

An Arduino-based smart irrigation system with Python Django dashboard, deployed on a 1/4 acre farm in Jinja, Uganda. The system automates watering based on real-time soil moisture data, reducing water waste and preventing crop drying.

## Key Features

- **Real-time soil monitoring** using 2 capacitive moisture sensors
- **Automated irrigation control** via 2 relays (pump + valve)
- **Remote monitoring** through Django web dashboard (computer + mobile)
- **SMS alerts** via SIM800L GSM module for system status
- **Historical data logging** for analysis and optimization

## Tech Stack


Hardware: ESP32, SIM800L, 2x moisture sensors, 2x relays, pump, valve
Backend: Python Django
Frontend: HTML/CSS/JavaScript (Bootstrap - mobile responsive)
Database: SQLite/PostgreSQL
Communication: Serial (Arduino-Django), GSM (SMS alerts)


## Quick Start

### Hardware Setup
1. Connect moisture sensors to ESP32 analog pins
2. Connect relays to digital pins (pump: pin 8, valve: pin 9)
3. Wire SIM800L for GSM communication

The current system already collects the foundational data needed for these AI models. Each irrigation decision, sensor reading, and crop outcome is logged, creating a dataset suitable for training predictive algorithms.

## Why This Matters for AI in Agriculture

Smallholder farms in Uganda face water uncertainty. This project demonstrates:
1. IoT infrastructure can be built with affordable components
2.Data collection at farm level is feasible and valuable
3. AI readiness - the system generates the structured data needed for machine learning
4. Scalable model - similar setups could network farms for regional water optimization


Nduwayo Morris - nduwayomorris@gmail.com
Kyambogo University
