monthly_counts = bicycle_thefts.groupby('Month').size()

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)

monthly_counts.plot(kind='line', ax=ax, color='red', marker='o')

ax.set_title('Bicycle Thefts by Month')
ax.set_ylabel('Total Incidents')

plt.show()
