import pandas as pd
import matplotlib.pyplot as plt

# Filler data for demonstration until real data is available
# X axis could be time periods, games, or sample indices
x = [1, 2, 3, 4, 5, 6]

# Team Performance Index (TPI) - solid line
tpi = [10, 12, 15, 14, 16, 18]

# Player Performance Index (PPI) - dashed line
ppi = [8, 9, 11, 13, 12, 14]

plt.figure(figsize=(8, 4.5))
plt.plot(x, tpi, 'b-', label='Team Performance Index (TPI)')
plt.plot(x, ppi, 'r--', label='Player Performance Index (PPI)')

plt.title("Microeconomy Impact Chart")
plt.xlabel("Sample Index")
plt.ylabel("Performance Index")
plt.grid(alpha=0.3)
plt.legend()

# Save to a file so running in headless environments doesn't block
output_path = 'impact_chart.png'
plt.tight_layout()
plt.savefig(output_path)
print(f"Saved impact chart to {output_path}")

# Optionally display interactively when running locally
plt.show()