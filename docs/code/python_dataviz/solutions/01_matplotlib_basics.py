import matplotlib.pyplot as plt

point1 = (4, 1)
point2 = (3, 4)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)

ax.plot(point1[0], point1[1], color='green', marker='^',linestyle='None', label='point1')
ax.plot(point2[0], point2[1], color='red', marker='o', linestyle='None',label='point2')
ax.set_xlim([0, 5])
ax.set_ylim([0, 5])
plt.legend()
plt.show()
