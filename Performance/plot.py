import pandas as pd
import matplotlib.pyplot as plt

# Load the data file
data_file = "download_times.txt"
columns = ["Username", "Filename", "DownloadTime"]

try:
    df = pd.read_csv(data_file, names=columns, skip_blank_lines=True)
    print(df.head())  # Debugging: Print first few rows
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Convert 'DownloadTime' to float
df["DownloadTime"] = pd.to_numeric(
    df["DownloadTime"].str.extract(r"([0-9]+\.[0-9]+)")[0], errors="coerce"
)

# Check if data was read correctly
print("\nData Types:\n", df.dtypes)
print("\nUnique Filenames:\n", df["Filename"].unique())
print("\nUnique Usernames:\n", df["Username"].unique())

# Ensure no NaN values in DownloadTime
df = df.dropna()

# Boxplot: Distribution of Download Times by File
plt.figure(figsize=(10, 5))
df.boxplot(column="DownloadTime", by="Filename")
plt.title("Download Time Distribution by File")
plt.xlabel("File Name")
plt.ylabel("Time (s)")
plt.suptitle("")  # Remove default Pandas title
plt.grid()
plt.show(block=False)  # Prevent blocking execution

# Group data by Username and plot average download time
avg_times = df.groupby("Username")["DownloadTime"].mean()
print("\nAverage Download Times per User:\n", avg_times)  # Debugging output

# Check if avg_times is empty before plotting
if not avg_times.empty:
    plt.figure(figsize=(10, 5))
    avg_times.plot(kind="bar", color="blue")
    plt.title("Average Download Time per User")
    plt.xlabel("User")
    plt.ylabel("Average Time (s)")
    plt.xticks(rotation=45)
    plt.grid(axis="y")

    plt.show(block=True)  # Ensure the plot is shown
else:
    print("\nNo valid data to plot for average download times.")

# Save the plot as an image
plt.savefig("average_download_time.png")
print("\nPlots saved as 'average_download_time.png'")
