
import numpy as np
import matplotlib.pyplot as plt


#with plt.xkcd():
data = np.genfromtxt('spectrum.txt', delimiter='\t', skip_header=1, names=['x', 'y'])

x = data["x"]
y = data["y"]


fig, ax = plt.subplots()


ax.set(xlabel='f (Hz)', ylabel='magnitude (dB)',
   title='Spectrum of Preamble')

ax.annotate('17.1kHz', xy=(17100, -15), xytext=(1500, -25),
            arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
            )

ax.annotate('21.7kHz', xy=(21700, -25), xytext=(50000, -25),
            arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=-0.2", arrowstyle='->'),
            )

ax.semilogx(x, y)
ax.grid(True, zorder=5)


plt.show()
