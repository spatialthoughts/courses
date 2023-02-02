fig, ax = plt.subplots()
fig.set_size_inches(20,10)


df.plot(ax=ax,
        title='Max Monthly Temperature at Bangalore',
        x='month',
        ylabel='Temperature (C)',
        kind='line',
		color='red')
plt.tight_layout()