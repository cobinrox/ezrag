# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from CSV file
df = pd.read_csv("your_data.csv")

# Set up the plot
plt.figure(figsize=(8, 6))
sns.boxplot(data=df, x='DistType', y='SearchScore', palette="Set3")

# Label the axes and title
plt.xlabel("Distance Type")
plt.ylabel("Search Score")
plt.title("Variation of Search Scores by Distance Type")
plt.grid(True)

# Show plot
plt.show()
