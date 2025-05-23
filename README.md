# Currency Exchange Rate Calculator

**Version:** 1.0.0  
**Author:** Jeffrey R. Dotson  
**Email:** jeffreyrdotson@vt.edu   
**GitHub Repository:** [https://github.com/Jeffrey214/VUT-PP2-CurrencyConverter](https://github.com/Jeffrey214/VUT-PP2-CurrencyConverter)

## Overview

The **Currency Exchange Rate Calculator** is a Python application developed for the Winter 2024 semester, providing real-time and historical currency conversion using data from the [Frankfurter API](https://www.frankfurter.app/). It includes a user-friendly GUI built with Tkinter, graphical displays of historical exchange rates, and persistent conversion history.

## Features

- **Real-Time Currency Conversion:**  
  Instantly converts currency using live data.

- **Historical Exchange Rates:**  
  Retrieves historical data, displaying minimum, maximum, and average rates.

- **Interactive Graphs:**  
  Visualizes historical exchange rates with Matplotlib graphs.

- **Persistent Conversion History:**  
  Saves conversion details, with options to export history to a file or reset it.

- **User-Friendly GUI:**  
  Interactive interface with dropdown currency selectors, integrated calendar for date selection, and clear visual indicators.

- **Visual Enhancements:**  
  Displays national flags corresponding to selected currencies for enhanced usability.

## Installation

### Prerequisites

- Python 3.6 or newer
- Pip

### Install Dependencies

```bash
pip install requests Pillow matplotlib tkcalendar
```

### Package Installation

Alternatively, install directly from the provided `setup.py`:

```bash
pip install .
```

## Project Structure

Ensure the project directory structure matches:

```
your_project/
├── icons/
│   ├── convert.png
│   ├── price_history.png
│   ├── conversion_history.png
│   ├── currency-conversion.ico
│   ├── currency-conversion.png
│   ├── save_icon.png
│   ├── reset.png
│   ├── flip.png
│   └── calendar.png
├── flag_folder_png/
│   ├── us.png
│   ├── eu.png
│   └── ... (other flag images)
├── main.py
├── README.md
└── setup.py
```

## Usage

### Launch the Application

Run from the command line:

```bash
currency_converter
```

or

```bash
python currency_converter.py
```

### Currency Conversion

1. Select currencies and enter the amount.
2. Click the convert button.
3. View results immediately and saved in history.

### View Conversion History

- Click on the history icon to access past conversions.
- Options provided for saving or resetting the history.

### Historical Price Data

1. Click the price history icon.
2. Select date range and currencies.
3. Click **Show Price History** for results and graphical view.

## Technical Details

- **API Integration:** Frankfurter API for accurate exchange rate data.
- **GUI Components:** Tkinter-based interface enhanced by Pillow for image handling.
- **Multithreading:** Efficient data fetching with progress indicators.
- **Data Management:** Persistent storage of conversion history.

## Contributing

Contributions are encouraged! Fork the repository and submit pull requests for improvements or fixes.

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Frankfurter API:** Reliable source of currency data.
- **Tkinter, Pillow, Matplotlib, tkcalendar:** Robust libraries for GUI and visualization.
- **Prosymbols Premium:** Icon design ([Currency icons by Prosymbols Premium - Flaticon](https://www.flaticon.com/free-icons/currency)).
