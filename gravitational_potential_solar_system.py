import numpy as np
import matplotlib.pyplot as plt

G = 7.4 * 10**(-28)  # m/kg
M_sun = 1.989 * 10**30  # kg
R_sun = 7 * 10**8  # m


def get_phi(M,R,S):
    if S < R:
        return G*M*(S**2-3*(R**2))/(2*(R**3)) # we assume a uniform density inside body
    else:
        return -G*M/S


def restore_minor_ticks_log_plot(ax, n_subticks=9):
    """For axes with a logrithmic scale where the span (max-min) exceeds
    10 orders of magnitude, matplotlib will not set logarithmic minor ticks.
    If you don't like this, call this function to restore minor ticks.

    Args:
        ax:
        n_subticks: Number of Should be either 4 or 9.

    Returns:
        None
    """
    if ax is None:
        ax = plt.gca()
    # Method from SO user importanceofbeingernest at
    # https://stackoverflow.com/a/44079725/5972175
    from matplotlib import ticker
    locmaj = ticker.LogLocator(base=10, numticks=1000)
    ax.yaxis.set_major_locator(locmaj)
    locmin = ticker.LogLocator(
        base=10.0, subs=np.linspace(0, 1.0, n_subticks + 2)[1:-1], numticks=1000
    )
    ax.yaxis.set_minor_locator(locmin)
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())


def get_solar_system_data():
    # https://nssdc.gsfc.nasa.gov/planetary/factsheet/
    import requests, json
    fname = 'planetary_factsheet.json'
    try:
        with open(fname) as f:
            data = json.load(f)
    except:
        data = requests.get('https://raw.githubusercontent.com/sempostma/planetary-factsheet/master/data.json').json()
        with open(fname, 'w') as f:
            json.dump(data, f, indent=4)
    return data


def solar_system_gravitational_potential():
    all_data = get_solar_system_data()
    data = {
        name: {
                'M': planet.get('mass10_24Kg')*10**24,
                'S': planet.get('semimajorAxis10_6Km')*(10**9),
                'R': planet.get('volumetricMeanRadiusKm') * (10**3)
        } for name, planet in all_data.items()}
    data['sun'] = {
        'M': M_sun,
        'S': 0,
        'R': R_sun,
    }
    max_S = max(p['S'] for p in data.values())*1.2 # max S + 20%
    hearth = data['earth']
    AU = hearth.get('S')
    S_bin = max_S/1000
    base_S_range = np.arange(0, max_S, S_bin)
    phi = {}
    for name, p in data.items():
        phi[name] = []
        S_step = p['R']/100
        S_max = p['R']*100
        S_range = np.arange(0, S_max, S_step)
        for S in S_range:
            phi_value = -get_phi(p['M'], p['R'], S)
            phi[name].append((p['S']+S, phi_value))
            if p['S']-S > 0:
                phi[name].append((p['S']-S, phi_value))
        for S in base_S_range:
            phi_value = -get_phi(p['M'], p['R'], abs(p['S']-S))
            phi[name].append((S, phi_value))

    all_S_values = []
    for val_list in phi.values():
        all_S_values.extend([val[0] for val in val_list])
    phi['all'] = [(S, sum(-get_phi(p['M'], p['R'], abs(p['S']-S)) for p in data.values())) for S in sorted(all_S_values)]

    def translate(name):
        if name == 'all':
            return 'Total' # total, including sun
        elif name == 'sun':
            return 'Sun'
        elif name == 'earth':
            return 'Earth'
        elif name == 'mars':
            return 'Mars'
        elif name == 'pluto':
            return 'Pluto'
        elif name == 'mercury':
            return 'Mercury'
        elif name == 'venus':
            return 'Venus'
        elif name == 'jupiter':
            return 'Jupiter'
        elif name == 'saturn':
            return 'Saturn'
        elif name == 'uranus':
            return 'Uranus'
        elif name == 'neptune':
            return 'Neptune'

    f = plt.figure()
    ax = f.add_subplot(111)
    ax.set_yscale('log')
    restore_minor_ticks_log_plot(ax)
    ax.set_xticks(range(int(max_S/AU)), minor=True)
    ax.set_xticks(np.arange(0, int(max_S / AU), step=5))

    planets_by_distance = ['all']
    planets_by_distance.extend([name for name, p in sorted(data.items(), key=lambda x: x[1].get('S'))])
    for name in planets_by_distance:
        if name in []:#'sun',]:
            continue
        alpha = 1 if name == 'all' else 0.7
        line_width = 1.5 if name == 'all' else 1
        data = phi[name]
        data.sort(key=lambda x: x[0])
        ax.plot([d[0]/AU for d in data], [d[1] for d in data], '-', linewidth=line_width, label=translate(name), alpha=alpha)
    ax.set_xlabel(r'Distance $d$ from Sun in AU ($\sim 150$ million km)')
    ax.set_ylabel(r'Newtonian gravitational potential absolute value $|\phi(d)|=\frac{GM}{c^2d}$')
    ax.grid(True, which='both', alpha=0.2)
    ax.legend(loc='upper right')
    plt.show()


if __name__ == '__main__':
    solar_system_gravitational_potential()