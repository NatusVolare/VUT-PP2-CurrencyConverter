import os
import requests
from tkinter import Tk, Label, StringVar, OptionMenu, Entry, Button, Frame, Toplevel, Text, filedialog, ttk, DoubleVar
from datetime import datetime, timedelta
from PIL import Image, ImageTk, ImageGrab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import NavigationToolbar2
import threading
from tkcalendar import Calendar
from tkinter.ttk import Progressbar
import queue
import random
import time

# Frankfurter API Configuration
API_URL = "https://api.frankfurter.app/latest"

# Top 22 most popular world currencies (including PLN and CZK)
currencies = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD",
    "SEK", "KRW", "SGD", "NOK", "INR", "MXN", "RUB", "ZAR", "TRY", "BRL",
    "PLN", "CZK"
]

# Mapping of currency codes to flag image file names (ISO country codes for flags)
currency_to_flag = {
    "USD": "us", "EUR": "eu", "GBP": "gb", "JPY": "jp", "AUD": "au",
    "CAD": "ca", "CHF": "ch", "CNY": "cn", "HKD": "hk", "NZD": "nz",
    "SEK": "se", "KRW": "kr", "SGD": "sg", "NOK": "no", "INR": "in",
    "MXN": "mx", "RUB": "ru", "ZAR": "za", "TRY": "tr", "BRL": "br",
    "PLN": "pl", "CZK": "cz"
}

# Get the directory of the current script
base_folder = os.path.dirname(__file__)

# Get the directory of the current script
base_folder = os.path.dirname(__file__)

# Updated paths to use relative paths in the 'icons' subfolder
icons_folder = os.path.join(base_folder, "icons")

flag_folder = os.path.join(base_folder, "flag_folder_png")
convert_button_image_path = os.path.join(icons_folder, "convert.png")
price_history_button_image_path = os.path.join(icons_folder, "price_history.png")
conversion_history_button_image_path = os.path.join(icons_folder, "conversion_history.png")
save_icon_path = os.path.join(icons_folder, "save_icon.png")
reset_icon_path = os.path.join(icons_folder, "reset.png")
flip_icon_path = os.path.join(icons_folder, "flip.png")
calendar_icon_path = os.path.join(icons_folder, "calendar.png")


# A list to store the conversion history
conversion_history = []

# Function to fetch exchange rates from the FreeCurrency API
def fetch_exchange_rates():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        if "rates" in data:
            return data.get("rates", {})
        else:
            print("Error fetching exchange rates:", data)
            return {}
    else:
        print("API request failed with status code:", response.status_code)
        return {}

# Function to perform the currency conversion
def convert_currency():
    from_currency = from_currency_var.get()  # Get the selected source currency
    to_currency = to_currency_var.get()  # Get the selected target currency
    amount = amount_var.get()  # Get the entered amount

    # Check if the source and target currencies are the same
    if from_currency == to_currency:
        result_label.config(text="Currencies Cannot Be The Same")  # Custom error message
        return
    
    # Replace comma with a period for proper float conversion
    amount = amount.replace(',', '.')
    try:
        amount = float(amount)  # Convert the string to a float
    except ValueError:
        result_label.config(text="Please Enter a Valid Number!")  # Handle invalid input
        return

    # Fetch conversion from Frankfurter API
    conversion_url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
    response = requests.get(conversion_url)

    if response.status_code == 200:
        data = response.json()
        if to_currency in data["rates"]:
            converted_amount = data["rates"][to_currency]
            result_label.config(text=f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")

            # Record the conversion in the history
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conversion_history.append(f"{current_time}: {amount} {from_currency} to {converted_amount:.2f} {to_currency}")

            # Update history window if it's open
            if hasattr(root, "history_window") and root.history_window.winfo_exists():
                update_history_text(root.history_window)
        else:
            result_label.config(text="Exchange rate not available.")
    else:
        result_label.config(text="API request failed.")

# Function to update the flag image based on the selected currency
def update_flag_image(currency, label):
    """Display flag image for the selected currency."""
    country_code = currency_to_flag.get(currency, "").lower()
    flag_path = os.path.join(flag_folder, f"{country_code}.png")
    print(f"Loading flag for {currency} ({country_code}): {flag_path}")  # Debugging print statement
    try:
        img = Image.open(flag_path)  # Open the flag image
        img = img.resize((30, 20), Image.Resampling.LANCZOS)  # Resize the image to fit the label
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        label.image = photo  # Keep a reference to prevent garbage collection
    except Exception as e:
        print(f"Error loading flag for {currency}: {e}")

def reset_history():
    """Clear the conversion history and update the text widget if open."""
    global conversion_history
    conversion_history = []  # Clear the history
    if hasattr(root, "history_window") and root.history_window.winfo_exists():
        update_history_text(root.history_window)  # Update the text widget if the history window is open

# Function to display the conversion history in a new window
def show_history():
    # Check if the history window already exists
    if hasattr(root, "history_window") and root.history_window.winfo_exists():
        # If the history window exists, bring it to the front and update its content
        root.history_window.lift()
        update_history_text(root.history_window)
        return

    # Create a new history window
    root.history_window = Toplevel(root)
    root.history_window.title("Conversion History")
    root.history_window.geometry("400x350")
    root.history_window.resizable(False, False)  # Make the window non-resizable

    # Create a text widget to display the history
    text_widget = Text(root.history_window, wrap="word", width=50, height=15)
    text_widget.pack(pady=10, padx=10)

    # Store a reference to the text widget for later updates
    root.history_window.text_widget = text_widget

    # Frame to hold buttons horizontally
    button_frame = Frame(root.history_window)
    button_frame.pack(pady=10)

    # Add the Save to File button with the save icon
    try:
        save_icon_path = os.path.join(os.path.dirname(conversion_history_button_image_path), "save_icon.png")
        save_icon_img = Image.open(save_icon_path)
        save_icon_img = save_icon_img.resize((30, 30), Image.Resampling.LANCZOS)  # Resize the image
        save_icon_photo = ImageTk.PhotoImage(save_icon_img)
        save_button = Button(button_frame, image=save_icon_photo, command=save_history_to_file, bg="#FEFCAF", activebackground="blue", borderwidth=2)
        save_button.image = save_icon_photo  # Keep a reference to prevent garbage collection
    except Exception as e:
        print(f"Error loading save icon: {e}")
        save_button = Button(button_frame, text="Save to File", command=save_history_to_file, bg="#FEFCAF", fg="white", borderwidth=2)

    save_button.grid(row=0, column=0, padx=5)

    # Add the Reset History button with the reset icon
    try:
        reset_icon_path = os.path.join(os.path.dirname(conversion_history_button_image_path), "reset.png")
        reset_icon_img = Image.open(reset_icon_path)
        reset_icon_img = reset_icon_img.resize((30, 30), Image.Resampling.LANCZOS)  # Resize the image
        reset_icon_photo = ImageTk.PhotoImage(reset_icon_img)
        reset_button = Button(button_frame, image=reset_icon_photo, command=reset_history, bg="#88B7D8", activebackground="red", borderwidth=2)
        reset_button.image = reset_icon_photo  # Keep a reference to prevent garbage collection
    except Exception as e:
        print(f"Error loading reset icon: {e}")
        reset_button = Button(button_frame, text="Reset History", command=reset_history, bg="#88B7D8", fg="white", borderwidth=2)

    reset_button.grid(row=0, column=1, padx=5)

    # Update the text widget with the current history content
    update_history_text(root.history_window)

# Function to update the history text widget
def update_history_text(history_window):
    text_widget = history_window.text_widget
    text_widget.delete("1.0", "end")  # Clear the current content

    if conversion_history:
        for entry in conversion_history:
            text_widget.insert("end", entry + "\n")
    else:
        text_widget.insert("end", "No conversion history available.")

# Function to save the conversion history to a file
def save_history_to_file():
    if conversion_history:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")],
                                                 title="Save Conversion History")
        if file_path:
            with open(file_path, "w") as file:
                for entry in conversion_history:
                    file.write(entry + "\n")
    else:
        print("No conversion history to save.")

# Function to fetch historical exchange rates from Frankfurter API
def fetch_historical_exchange_rates_with_progress(from_currency, to_currency, start_date, end_date, loading_label, progress_bar, progress_percentage):
    """Fetch historical exchange rates from the Frankfurter API with progress updates."""
    # Initialize variables
    historical_data = {}
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end_date_obj - start_date_obj).days + 1
    processed_days = 0  # Initialize outside the loop

    current_date_obj = start_date_obj
    while current_date_obj <= end_date_obj:
        current_date = current_date_obj.strftime("%Y-%m-%d")
        url = f"https://api.frankfurter.app/{current_date}?from={from_currency}&to={to_currency}"

        # API request
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "rates" in data and to_currency in data["rates"]:
                historical_data[current_date] = data["rates"][to_currency]
            else:
                print(f"No rates available for {current_date}")
        else:
            error_message = f"API request failed for {current_date} (Status: {response.status_code})"
            print(error_message)
            loading_label.config(text=error_message, fg="red")
            return None

        # Update progress
        processed_days += 1
        progress = int((processed_days / total_days) * 100)
        progress_bar['value'] = progress
        progress_percentage.config(text=f"{progress}%")
        loading_label.update()

        # Move to the next day
        current_date_obj += timedelta(days=1)

    return historical_data

# Function to fetch and plot historical price data using Frankfurter API
def fetch_and_plot_price_history():
    from_currency_history_var = StringVar()
    from_currency_history_var.set(from_currency_var.get())
    to_currency_history_var = StringVar()
    to_currency_history_var.set(to_currency_var.get())

    # Create a new window for price history
    price_history_window = Toplevel(root)
    price_history_window.title("Price History")
    price_history_window.geometry("250x225")
    price_history_window.resizable(False, False)

    # Dropdowns for selecting currencies
    Label(price_history_window, text="From Currency:").grid(row=0, column=0, padx=5, pady=5)
    OptionMenu(price_history_window, from_currency_history_var, *currencies).grid(row=0, column=1, padx=5, pady=5)

    Label(price_history_window, text="To Currency:").grid(row=1, column=0, padx=5, pady=5)
    OptionMenu(price_history_window, to_currency_history_var, *currencies).grid(row=1, column=1, padx=5, pady=5)

    # Default dates
    today = datetime.now()
    prior_30_days = today - timedelta(days=30)

    # Start date selection
    Label(price_history_window, text="Start Date:").grid(row=2, column=0, padx=5, pady=5)
    start_date_var = StringVar(value=prior_30_days.strftime("%Y-%m-%d"))
    start_date_entry = Entry(price_history_window, textvariable=start_date_var, width=15)
    start_date_entry.grid(row=2, column=1, padx=5, pady=5)

    def select_start_date():
        def set_date():
            start_date_var.set(calendar.get_date())
            calendar_window.destroy()

        calendar_window = Toplevel(price_history_window)
        calendar_window.title("Select Start Date")
        calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
        calendar.pack(pady=10)
        Button(calendar_window, text="Set Date", command=set_date).pack(pady=10)

    # Load the calendar icon for the start date button
    try:
        calendar_icon_path = os.path.join(os.path.dirname(conversion_history_button_image_path), "calendar.png")
        calendar_icon_img = Image.open(calendar_icon_path)
        calendar_icon_img = calendar_icon_img.resize((20, 20), Image.Resampling.LANCZOS)
        start_calendar_icon = ImageTk.PhotoImage(calendar_icon_img)
        start_date_button = Button(price_history_window, image=start_calendar_icon, command=select_start_date)
        start_date_button.image = start_calendar_icon  # Keep a reference
    except Exception as e:
        print(f"Error loading calendar icon: {e}")
        start_date_button = Button(price_history_window, text="Select Date", command=select_start_date)

    start_date_button.grid(row=2, column=2, padx=5, pady=5)

    # End date selection
    Label(price_history_window, text="End Date:").grid(row=3, column=0, padx=5, pady=5)
    end_date_var = StringVar(value=today.strftime("%Y-%m-%d"))
    end_date_entry = Entry(price_history_window, textvariable=end_date_var, width=15)
    end_date_entry.grid(row=3, column=1, padx=5, pady=5)

    def select_end_date():
        def set_date():
            end_date_var.set(calendar.get_date())
            calendar_window.destroy()

        calendar_window = Toplevel(price_history_window)
        calendar_window.title("Select End Date")
        calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
        calendar.pack(pady=10)
        Button(calendar_window, text="Set Date", command=set_date).pack(pady=10)

    # Load the calendar icon for the end date button
    try:
        end_calendar_icon = ImageTk.PhotoImage(calendar_icon_img)
        end_date_button = Button(price_history_window, image=end_calendar_icon, command=select_end_date)
        end_date_button.image = end_calendar_icon  # Keep a reference
    except Exception as e:
        print(f"Error loading calendar icon: {e}")
        end_date_button = Button(price_history_window, text="Select Date", command=select_end_date)

    end_date_button.grid(row=3, column=2, padx=5, pady=5)

    # Show Price History button
    def show_price_history():
        start_date = start_date_var.get()
        end_date = end_date_var.get()
        plot_price_history(from_currency_history_var.get(), to_currency_history_var.get(), start_date, end_date)

    Button(price_history_window, text="Show Price History", command=show_price_history, bg="green", fg="white").grid(row=4, column=0, columnspan=3, pady=10)

# Custom toolbar class inheriting from NavigationToolbar2Tk
class CustomToolbar(NavigationToolbar2Tk):
    # Override the default methods to include only the Save button
    toolitems = [
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
    ]

def animate_loading(loading_label, dots=0, stop_event=None):
    """Animate the loading label with dots cycling."""
    if stop_event and stop_event.is_set():
        return  # Stop animation when event is set
    new_text = f"Fetching data, please wait{'.' * dots}"
    loading_label.config(text=new_text)
    loading_label.update()  # Ensure the label updates on the screen
    next_dots = (dots + 1) % 4  # Cycle through 0, 1, 2, 3
    loading_label.after(500, animate_loading, loading_label, next_dots, stop_event)

# Function to plot the price history using daily data for the past 30 days
def plot_price_history(from_currency, to_currency, start_date, end_date):
    # Convert the dates to string in "YYYY-MM-DD" format
    start_date_str = start_date
    end_date_str = end_date

    # Create a new window for displaying loading and results
    loading_window = Toplevel(root)
    loading_window.title("Loading Data")

    # Set the loading window size and make it non-resizable
    loading_window.geometry("300x150")  # Set the size of the loading window
    loading_window.resizable(False, False)  # Make the window non-resizable

    # Existing loading label
    loading_label = Label(loading_window, text="Fetching data, please wait")
    loading_label.pack(pady=10)

    # Add another line in bold
    note_label = Label(loading_window, text="Note: This process can take a while!", font=("Arial", 10, "bold"))
    note_label.pack(pady=5)

    # Event to stop the animation
    stop_event = threading.Event()

    # Progress bar
    progress_bar = Progressbar(loading_window, orient="horizontal", length=200, mode="determinate")
    progress_bar.pack(pady=10)

    # Another label to show percentage
    progress_percentage = Label(loading_window, text="0%")
    progress_percentage.pack(pady=5)

    # Start the animation
    animate_loading(loading_label, stop_event=stop_event)

    # Create a queue to communicate between threads
    result_queue = queue.Queue()

    def fetch_data():
        try:
            # Fetch data
            historical_data = fetch_historical_exchange_rates_with_progress(
                from_currency, to_currency, start_date_str, end_date_str, loading_label, progress_bar, progress_percentage
            )
            # Place the result in the queue
            result_queue.put(historical_data)
        except Exception as e:
            # Place the error in the queue
            result_queue.put(e)
        finally:
            stop_event.set()  # Stop the animation

    # Check the queue periodically and update the UI
    def check_queue():
        try:
            result = result_queue.get_nowait()  # Get the result from the queue
        except queue.Empty:
            loading_window.after(100, check_queue)  # Check again after 100ms
            return

        # Stop the loading animation and close the loading window
        stop_event.set()
        loading_window.destroy()

        # Handle the result
        if isinstance(result, Exception):
            # Display the error message
            error_window = Toplevel(root)
            error_window.title("Error")
            Label(error_window, text=f"Error: {str(result)}", fg="red").pack(pady=10)
        elif result:
            # Process and display the fetched data
            display_results(result, from_currency, to_currency)
        else:
            # No data available
            error_window = Toplevel(root)
            error_window.title("No Data")
            Label(error_window, text="No historical data available.", fg="red").pack(pady=10)

    def display_results(historical_data, from_currency, to_currency):
        # Extract dates and rates from the historical data
        dates = []
        rates = []
        for date, rate in sorted(historical_data.items()):
            dates.append(datetime.strptime(date, "%Y-%m-%d"))
            rates.append(rate)

        # Calculate and display the maximum, minimum, and average rates
        max_rate = max(rates)
        min_rate = min(rates)
        avg_rate = sum(rates) / len(rates)

        # Find dates for min and max rates
        max_date = dates[rates.index(max_rate)].strftime("%Y-%m-%d")
        min_date = dates[rates.index(min_rate)].strftime("%Y-%m-%d")

        # Create a result window to display the max, min, and average rates with their dates
        result_window = Toplevel(root)
        result_window.title("Price History Results")
        result_window.geometry("300x100")
        result_window.lift()  # Bring the result window to the front
        result_window.resizable(False, False)  # Make the window non-resizable
        result_window.focus_force()  # Ensure the result window gets focus initially

        Label(result_window, text=f"Max Rate: {max_rate:.2f} on {max_date}").pack(pady=5)
        Label(result_window, text=f"Min Rate: {min_rate:.2f} on {min_date}").pack(pady=5)
        Label(result_window, text=f"Avg Rate: {avg_rate:.2f}").pack(pady=5)

        # Create a new window for the graph
        graph_window = Toplevel(root)
        graph_window.title("Currency Price History Graph")
        graph_window.geometry("900x600")
        graph_window.resizable(False, False)  # Make the window non-resizable

        # Plot the rate history
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dates, rates, label=f"{from_currency} to {to_currency}")
        ax.set_xlabel('Date')
        ax.set_ylabel('Exchange Rate')
        ax.set_title(f'Price History for {from_currency} to {to_currency} ({start_date} to {end_date})')
        ax.legend()
        ax.grid(True)  # Add gridlines to the graph
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Embed the figure into the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        # Add custom toolbar with limited functionality
        toolbar_frame = Frame(graph_window)
        toolbar_frame.pack(side='bottom', fill='x')
        toolbar = CustomToolbar(canvas, graph_window)
        toolbar.pack(side='bottom', fill='x')
        toolbar.update()

    # Start data fetching in a separate thread
    threading.Thread(target=fetch_data, daemon=True).start()
    # Start checking the queue
    loading_window.after(100, check_queue)

def flip_currencies():
    """Swap the selected currencies in the dropdowns."""
    from_currency = from_currency_var.get()
    to_currency = to_currency_var.get()
    from_currency_var.set(to_currency)
    to_currency_var.set(from_currency)

# Fetch exchange rates at the start
exchange_rates = fetch_exchange_rates()

# Set up the main application window
root = Tk()
root.title("Currency Converter")
root.geometry("300x325")  # Set fixed size for the window
root.resizable(False, False)  # Prevent resizing

# Decorative bar at the top
decorative_bar = Label(root, bg="purple", height=1)
decorative_bar.pack(fill="x")

# Frame for currency input options
frame = Frame(root)
frame.pack(pady=10)

# Dropdown for selecting the source currency
from_currency_var = StringVar()
from_currency_var.set("USD")  # Default option
from_currency_label = Label(frame, text="From Currency:")
from_currency_label.grid(row=0, column=0, padx=5, pady=5)

from_currency_dropdown = OptionMenu(frame, from_currency_var, *currencies)
from_currency_dropdown.grid(row=0, column=1, padx=5, pady=5)

from_currency_flag_label = Label(frame)
from_currency_flag_label.grid(row=0, column=2, padx=5, pady=5)
update_flag_image(from_currency_var.get(), from_currency_flag_label)  # Update flag image for the selected currency
from_currency_var.trace("w", lambda *args: update_flag_image(from_currency_var.get(), from_currency_flag_label))

# Flip button to swap currencies
try:
    flip_icon_path = os.path.join(os.path.dirname(conversion_history_button_image_path), "flip.png")
    flip_icon_img = Image.open(flip_icon_path)
    flip_icon_img = flip_icon_img.resize((30, 30), Image.Resampling.LANCZOS)  # Resize the image
    flip_icon_photo = ImageTk.PhotoImage(flip_icon_img)
    flip_button = Button(frame, image=flip_icon_photo, command=flip_currencies, bg="lightblue", activebackground="blue", borderwidth=2)
    flip_button.image = flip_icon_photo  # Keep a reference to prevent garbage collection
except Exception as e:
    print(f"Error loading flip icon: {e}")
    flip_button = Button(frame, text="Flip", command=flip_currencies, bg="lightblue", fg="white", borderwidth=2)

flip_button.grid(row=1, column=1, pady=5)

# Dropdown for selecting the target currency
to_currency_var = StringVar()
to_currency_var.set("EUR")  # Default option
to_currency_label = Label(frame, text="To Currency:")
to_currency_label.grid(row=2, column=0, padx=5, pady=5)

to_currency_dropdown = OptionMenu(frame, to_currency_var, *currencies)
to_currency_dropdown.grid(row=2, column=1, padx=5, pady=5)

to_currency_flag_label = Label(frame)
to_currency_flag_label.grid(row=2, column=2, padx=5, pady=5)
update_flag_image(to_currency_var.get(), to_currency_flag_label)  # Update flag image for the target currency
to_currency_var.trace("w", lambda *args: update_flag_image(to_currency_var.get(), to_currency_flag_label))

# Entry field for the amount to convert
amount_label = Label(frame, text="Amount:")
amount_label.grid(row=3, column=0, padx=5, pady=5)

amount_var = StringVar()
amount_entry = Entry(frame, textvariable=amount_var, width=10)
amount_entry.grid(row=3, column=1, padx=5, pady=5)

# Frame to hold the buttons horizontally
buttons_frame = Frame(root)
buttons_frame.pack(pady=0)  # Add some vertical padding

# Button for performing the conversion
try:
    convert_img = Image.open(convert_button_image_path)
    convert_img = convert_img.resize((30, 30), Image.Resampling.LANCZOS)  # Resize button image
    convert_button_img = ImageTk.PhotoImage(convert_img)
    convert_button = Button(buttons_frame, image=convert_button_img, command=convert_currency, borderwidth=2, bg="#C1FD95", activebackground="green")
    convert_button.grid(row=0, column=0, padx=5)  # Add horizontal padding
except Exception as e:
    print(f"Error loading convert button image: {e}")
    convert_button = Button(buttons_frame, text="Convert", command=convert_currency, bg="#C1FD95", fg="white", borderwidth=2)
    convert_button.grid(row=0, column=0, padx=5)

# Button to show price history
try:
    price_history_img = Image.open(price_history_button_image_path)
    price_history_img = price_history_img.resize((30, 30), Image.Resampling.LANCZOS)  # Resize the image
    price_history_button_img = ImageTk.PhotoImage(price_history_img)
    price_history_button = Button(buttons_frame, image=price_history_button_img, command=fetch_and_plot_price_history, borderwidth=2, bg="#D8863B", activebackground="orange")
    price_history_button.grid(row=0, column=1, padx=5)
except Exception as e:
    print(f"Error loading price history button image: {e}")
    price_history_button = Button(buttons_frame, text="Price History", command=fetch_and_plot_price_history, bg="#D8863B", fg="white", borderwidth=2)
    price_history_button.grid(row=0, column=1, padx=5)

# Button to show conversion history
try:
    conversion_history_img = Image.open(conversion_history_button_image_path)
    conversion_history_img = conversion_history_img.resize((30, 30), Image.Resampling.LANCZOS)  # Resize the image
    conversion_history_button_img = ImageTk.PhotoImage(conversion_history_img)
    history_button = Button(buttons_frame, image=conversion_history_button_img, command=show_history, borderwidth=2, bg="#E5989E", activebackground="blue")
    history_button.grid(row=0, column=2, padx=5)
except Exception as e:
    print(f"Error loading conversion history button image: {e}")
    history_button = Button(buttons_frame, text="Conversion History", command=show_history, bg="#E5989E", fg="white", borderwidth=2)
    history_button.grid(row=0, column=2, padx=5)

# Frame to hold the output box with a border
output_frame = Frame(root, bg="lightgray", bd=0.5, relief="groove")
output_frame.pack(pady=10, padx=10)  # Add padding for spacing

# Label to display the result of the conversion inside the bordered frame
result_label = Label(output_frame, text="", font=("Arial", 12), bg="white", width=35, height=2)
result_label.pack(padx=5, pady=5)  # Padding inside the frame for the label

# Start the Tkinter main loop to run the application
root.mainloop()
