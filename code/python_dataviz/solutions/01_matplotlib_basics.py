fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
ax.plot(point1[0], point1[1], color='green', marker='^')
ax.plot(point2[0], point2[1], color='red', marker='o')

plt.xlim([0, 5])
plt.ylim([0, 5])
plt.show()
