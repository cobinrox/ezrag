import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV data
data = pd.read_csv("your_data.csv")

# Create a box plot
sns.boxplot(x="DistType", y="SearchScore", data=data)
plt.title("Search Score Distribution by Distance Type")
plt.xlabel("Distance Type")
plt.ylabel("Search Score")
plt.show()