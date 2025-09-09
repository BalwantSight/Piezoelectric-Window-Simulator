# Piezoelectric Window Simulator

## A Digital Lab for Urban Wind Energy Harvesting

This project is an interactive simulator that explores a conceptual prototype of a piezoelectric panel designed for building windows. Inspired by biomimicry, it models how wind-induced vibrations, typically seen as an engineering problem, can be harnessed as a source of clean, complementary energy in urban environments.

![Simulator Screenshot](https://i.ibb.co/4nFZhkd3/Captura-de-pantalla-2025-09-09-a-la-s-12-44-03-p-m.png)

## Key Features

-   **Interactive Physics Engine:** Adjust physical parameters like mass, stiffness, and damping in real-time to see their effect on energy generation.
-   **Realistic Vibration Model:** Utilizes a forced, damped harmonic oscillator model, including quadratic air resistance and dynamic electrical damping.
-   **Real-Time Data Visualization:** A live graph displays instantaneous power output, while a data panel shows key metrics like displacement, resonant frequency, and accumulated energy.
-   **Energy Storage Simulation:** Models a central battery that accumulates energy from a system of 100 windows and includes a constant discharge rate to simulate a load.
-   **System Failure Modeling:** The simulation includes a fail-safe that stops the process if the panel's physical displacement exceeds its structural limits.

## Tech Stack

-   **Core Language:** Python 3.x
-   **Simulation & UI:** [Pygame](https://www.pygame.org/)
-   **Physics & Numerics:** [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/)

## Setup and Installation

Follow these steps to set up and run the simulation on your local machine.

### 1. Prerequisites
Make sure you have **Python 3** installed on your system.

### 2. Open a Terminal
Navigate to the project's root directory (the folder containing `main.py`) in your terminal or command prompt.

### 3. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment. Run the following commands:

```bash
# Create the virtual environment
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Create and Activate a Virtual Environment
```bash
pip install -r requirements.txt
```

## 5. How to Run the Simulator

Once the setup is complete, run the simulator with the following command:
```bash
python main.py
```

##Project Vision

This project explores a paradigm shift in civil engineering: instead of fighting wind-induced vibrations, what if we harnessed them? Inspired by how trees flexibly sway to dissipate wind energy, this simulator provides a digital lab to test how piezoelectric materials can turn this "problem" into a sustainable power source for smart buildings.
