monthly_counts = bicycle_thefts.groupby('Month').size()

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)

monthly_counts.plot(kind='line', ax=ax, color='red', marker='o')

ax.set_title('Bicycle Thefts by Month')
ax.set_ylabel('Total Incidents')

# Extra: Add labels
line = ax.lines[0]

for x_value, y_value in zip(line.get_xdata(), line.get_ydata()):
    ax.annotate(y_value,(x_value, y_value), xytext=(0, 20), 
        textcoords="offset points", ha='center', va='top')

# Extra: Custmize X-Axis labels
labels = []
for date in pd.to_datetime(monthly_counts.index):
  if date.month in [1, 6, 12]:
    labels.append(date.strftime('%Y-%m'))
  else:
    labels.append('')
ax.set_xticklabels(labels)  

ax.set_title('Total Crime by Month')
ax.set_ylabel('Total Incidents')

plt.tight_layout()
plt.show()
