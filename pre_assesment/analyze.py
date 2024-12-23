import pandas as pd
import matplotlib.pyplot as plt

import os
import sys

# loop over the results directory and get all csv the files in the directory
for file in os.listdir('./results'):
    if file.endswith('.csv'):
        file_name = file.split('.')[0]

        # Create a DataFrame
        df = pd.read_csv(f'./results/{file_name}.csv')

        # Define bins for average
        average_bins = [1, 2, 3, 4, 5]

        # Get all unique values in the 'std_dev' column for exact matching
        std_dev_bins = sorted(df['std_dev'].unique())

        # Bin the data for averages
        average_counts = pd.cut(df['average'], bins=average_bins).value_counts().sort_index()

        # Count exact occurrences for standard deviation
        std_dev_counts = df['std_dev'].value_counts().sort_index()

        # Plotting
        plt.figure(figsize=(12, 6))

        # Plot for averages
        plt.subplot(1, 2, 1)
        average_counts.plot(kind='bar', edgecolor='black')
        plt.title('Number of Claims by Average Range')
        plt.xlabel('Average Range')
        plt.ylabel('Number of Claims')
        plt.xticks(rotation=45)

        # Plot for standard deviations
        plt.subplot(1, 2, 2)
        std_dev_counts.plot(kind='bar', color='orange', edgecolor='black')
        plt.title('Number of Claims by Standard Deviation (Exact Values)')
        plt.xlabel('Standard Deviation')
        plt.ylabel('Number of Claims')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(f'./results/{file_name}.png')

