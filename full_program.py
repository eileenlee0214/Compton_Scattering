Web VPython 3.2

scene.userzoom = False
scene.range = 15
scene.autoscale = False
scene.userspin = False

running = False
attached_vec = False

freq = 1.0

dl = 0.01
dt = 0.01

init_Ei = 0
init_iM = 0

DISPLAY_FREQ_MIN = 1
DISPLAY_FREQ_MAX = 20

#for modeling purposes and simplicity, these constants will be set to 1
c = 1 #speed of light
m = 1 #electron mass
h = 1 #planks constant
r = 1 # electron radius

b0_min = 0.00043;  b0_max = 0.00143 # infrared
b1_min = 0.00143;  b1_max = 0.00300 # visible
b2_min = 0.00300;  b2_max = 0.100 # ultraviolet
b3_min = 0.100;    b3_max = 100.0 # x ray
b4_min = 100.0;    b4_max = 30000.0 # gamma ray

## okay so i need to account for the photoelectric effect. 
# 13.6 eV for hydrogen atom

## pair production: 2.044 MeV
## add (M) eV displayer: hc / E = lambda for photons
            

def linear_to_log_freq(t):
    if t < 0.2:
        return b0_min * pow(b0_max / b0_min, t / 0.2)
    elif t < 0.4:
        return b1_min * pow(b1_max / b1_min, (t - 0.2) / 0.2)
    elif t < 0.6:
        return b2_min * pow(b2_max / b2_min, (t - 0.4) / 0.2)
    elif t < 0.8:
        return b3_min * pow(b3_max / b3_min, (t - 0.6) / 0.2)
    else:
        return b4_min * pow(b4_max / b4_min, (t - 0.8) / 0.2)

def log_to_linear_freq(f):
    if f >= b0_min and f <= b0_max:
        return 0.2 * log(f / b0_min) / log(b0_max / b0_min)
    elif f > b0_max and f <= b1_max:
        return 0.2 + 0.2 * log(f / b1_min) / log(b1_max / b1_min)
    elif f > b1_max and f <= b2_max:
        return 0.4 + 0.2 * log(f / b2_min) / log(b2_max / b2_min)
    elif f > b2_max and f <= b3_max:
        return 0.6 + 0.2 * log(f / b3_min) / log(b3_max / b3_min)
    else:
        return 0.8 + 0.2 * log(f / b4_min) / log(b4_max / b4_min)

def physical_to_display_freq(f):
    t = log_to_linear_freq(f)
    return DISPLAY_FREQ_MIN + t * (DISPLAY_FREQ_MAX - DISPLAY_FREQ_MIN)

NM_SCALE = 1

GAMMA_THRESHOLD = 0.01
XRAY_THRESHOLD = 10.0
UV_THRESHOLD = 400.0
VIS_THRESHOLD = 700.0

def classify_photon(wl_nm):
    if wl_nm < GAMMA_THRESHOLD:
        return 'Gamma Ray'
    elif wl_nm < XRAY_THRESHOLD:
        return 'X-Ray'
    elif wl_nm < UV_THRESHOLD:
        return 'Ultraviolet'
    elif wl_nm < VIS_THRESHOLD:
        return 'Visible'
    else:
        return 'Infrared'

def freq_to_color(f):
    t = log_to_linear_freq(f)
    if t < 0.2:
        s = t / 0.2
        return vec(0.6, s * 0.2, 0)
    elif t < 0.4:
        s = (t - 0.2) / 0.2
        return vec(1-s, 0, s)
    elif t < 0.6:
        s = (t - 0.4) / 0.2
        return vec(0.5 - s * 0.5, 0, 1)
    elif t < 0.8:
        s = (t - 0.6) / 0.2
        return vec(s, s, 1)
    else:
        s = (t - 0.8) / 0.2
        return vec(1, 1, 1)

energy_graph = graph(
    title = 'Conservation of Energy (E = hf)',
    xtitle = 'Bar Graphs',
    ytitle = 'Energy (hf)',
    width = 400,
    height = 300,
    xmin = 0, xmax = 4.5,
    ymin = 0, ymax = 7,
    align = 'right'
)



bar_Ei   = gvbars(graph=energy_graph, delta=0.5, color=color.magenta, label='initial energy of photon')
bar_Ef   = gvbars(graph=energy_graph, delta=0.5, color=color.purple,  label='final energy of photon')
bar_Ke   = gvbars(graph=energy_graph, delta=0.5, color=color.cyan,    label='kinetic energy of electron')
bar_Etot = gvbars(graph=energy_graph, delta=0.5, color=color.blue,    label='check')

def update_energy_graph(E_i, E_f, K):
    bar_Ei.plot(1, E_i)
    bar_Ef.plot(2, E_f)
    bar_Ke.plot(3, K)
    bar_Etot.plot(4, E_f + K) # should be equal to E_i ?
    energy_graph.ymax = max(E_i, E_f, K, E_f + K) * 1.7

update_energy_graph(h * freq, 0, 0)

#===== momentum graph
## do i also add y dir momentum ?
momenta_graph = graph(
    title = 'Momentum',
    xtitle = 'Bar Graphs',
    ytitle = 'x-direction momenta',
    width = 400,
    height = 300,
    xmin = 0, xmax = 5,
    ymin = -2, ymax = 2,
    align = 'right'
)

bar_iM   = gvbars(graph=momenta_graph, delta=0.5, color=color.magenta, label='initial momentum of photon')
bar_fM   = gvbars(graph=momenta_graph, delta=0.5, color=color.purple,  label='final momentum of photon')
bar_eM   = gvbars(graph=momenta_graph, delta=0.5, color=color.cyan,    label='momentum of electron after collision')
bar_Mtot = gvbars(graph=momenta_graph, delta=0.5, color=color.blue,    label='check')

def update_momenta_graph(iM, fM, eM):
    bar_iM.plot(1, iM)
    bar_fM.plot(2, fM)
    bar_eM.plot(3, eM)
    bar_Mtot.plot(4, fM + eM) # should be equal to iM ?
    top = max(abs(iM), abs(fM), abs(eM), abs(fM + eM)) * 1.7
    momenta_graph.ymax = top
    momenta_graph.ymin = 0

update_momenta_graph(h * freq, 0, 0)

# ======end

def update_wl_label(wl_sim):
    wl_nm = wl_sim * NM_SCALE
    name = classify_photon(wl_nm)
    wl_label.text = f'  lambda = {wl_nm:.3f} nm  [{name}]\n'
    
# ======histogram
dx = 10
bins = [(i*10 + 5) for i in range(17)]
hist_freq = [0] * len(bins)

histogram = graph(
    title = 'Angle Distribution',
    xtitle = 'Angle',
    ytitle = 'Frequency',
    width = 400,
    height = 300,
    xmin = 0, xmax = 180,
    ymin = 0, ymax = 10,
    align = 'right'
    )
    
hist_bars = gvbars(graph=histogram, color = color.red, delta = dx)
    
def update_histogram(angle):
    global hist_bars, hist_freq
    angle = angle * 180 / pi
    bin_index = int(angle / 10)
    hist_freq[bin_index] += 1
    data = []
    for i in range(len(hist_freq)):
        data.append([bins[i],hist_freq[i]])
        hist_bars.data = data

#====Photon math and class

#wave packet form
def dsine(x, freq, phase, dis):
    return exp(-(x**2)) * sin(freq * (x - dis + phase))


def kn_rejacc(Ei): #rejection acceptance method since the pdf from klein nishina is univertible
    g = Ei / (m*c**2) #photon energy per electron rest mass
    def diff_cross(x):
        l_ratio = 1 / (1 + g * (1 - x))#x = cos (theta), change of variables for simplicity, l_ratio is the ration of the incident and outgoing photon wavelengths
        f = (
            0.5 * r**2 * l_ratio**2 *
            (l_ratio + 1 / l_ratio - (1 - x**2))
            )
        return f

    def get_max(): #finding the maximum value of the distribution for the envelope
        domain = [(i - 50) / 50 for i in range(101)]
        maximum = 0
        for i in domain:
            if diff_cross(i) > maximum:
                maximum = diff_cross(i)
        return maximum

    env = get_max() * 1.2 #envelope to bound distribution
    samplex = random() * 2 - 1
    sampley = random()
    while sampley > diff_cross(samplex) / env:
        samplex = random() * 2 - 1
        sampley = random()
    if random() > 0.5:
        return -acos(samplex)
    else: 
        return acos(samplex)
        
class photon:
    def __init__(self, wlength, ipos, theta):
        self.wlength = wlength
        self.theta = theta #initial angle from positive x-axis
        self.ipos = ipos #initial position
        self.localtime = 0 #since photons travel in a straight line from initial position, local time must be reset after every collision
        self.freq = c / wlength
        self.display_freq = physical_to_display_freq(self.freq)
        self.color = freq_to_color(self.freq)
        self.dir = rotate(vec(1,0,0), angle = self.theta, axis = vec(0,0,1))
        self.E_i = h * self.freq
        self.sign = 1
        
        self.iM = h / self.wlength
        self.sum_K = 0
        self.sum_eM_x = 0
        self.sum_M_curr_x = 0
        self.init_Ei_set = False
        self.init_iM_set = False
        self.init_Ei = 0
        self.init_iM = 0

    def create_photon(self): #create photons based on initial angle and displacement
        self.curv = curve(color=self.color)
        for i in range(400):
            dx = (i - 200) * dl
            y = dsine(dx, self.display_freq, 0, self.ipos.x)
            rotated = rotate(vec(dx, y, 0), angle = self.sign * diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1))
            self.curv.append(pos = rotated + self.ipos)
        self.pos = vec(self.ipos.x, self.ipos.y, 0)

    def photon_step(self):
        for i in range(self.curv.npoints):
            self.curv.color = self.color
            dx = (i - 200) * dl
            t = self.localtime * c
            y = dsine(dx, self.display_freq, t, 0)
            rotated = rotate(vec(dx + t, y, 0), angle = self.sign * diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1))
            self.curv.modify(i, pos = rotated + self.ipos)
        self.localtime += dt
        self.pos += rotate(vec(1,0,0), angle = self.sign * diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) * dt
        if mag(self.pos) > 40:
            self.curv.clear()
            photons.remove(self)

    def collision(self): #calculating energy and updating frequency and electron velocity from conservation of energy and momentum
        self.E_f = self.E_i / (1 + (self.E_i / (m * c**2)) * (1-cos(self.theta)))
        self.K = self.E_i - self.E_f
        self.wlength += h /(m*c) * (1 - cos(self.theta))
        self.freq = c / self.wlength
        self.display_freq = physical_to_display_freq(self.freq)
        self.color = freq_to_color(self.freq)
        self.M = h / (self.wlength)
        self.dir = rotate(self.dir, angle = self.theta, axis = vec(0,0,1))
        self.localtime = 0
        
#=====BOHR MODEL

bohr = False

# Hydrogen atom: single shell (n=1)
a0 = 2.0 # in reality: 5.292 * pow(10, -11)

def bohr_radius(n):
    return a0 * n * n

def orbital_speed(n):
    return 0.1 / n # inaccurate but whatever, figure out later

class bohr_model:
    def __init__(self):
        pass
    
    def create_nucleus(self):
        self.nucleus = nucleus = sphere(pos=vec(0,0,0), radius=0.4, color=color.red, emissive=True)
        
    def create_rings(self,radius):
        pts = []
        n_pts = 100
        for k in range(n_pts + 1):
            angle_k = 2 * pi * k / n_pts
            pts.append(vec(radius * cos(angle_k), radius * sin(angle_k), 0))
        self.c_ring = curve(color=vec(0.3, 0.3, 0.3))
        for pt in pts:
            self.c_ring.append(pos=pt)

class orbital_electron:
    def __init__(self, shell):
        self.shell = shell
        self.angle = 0
        self.radius = bohr_radius(shell)
        self.speed = orbital_speed(shell)
        self.p = vec(0, 0, 0)
        self.active = True
        x = self.radius * cos(self.angle)
        y = self.radius * sin(self.angle)
        self.sphere = sphere(pos=vec(x, y, 0), radius=0.3, color=color.cyan)

    def electron_step(self):
        if self.active:
            self.angle += self.speed * dt
            x = self.radius * cos(self.angle)
            y = self.radius * sin(self.angle)
            self.sphere.pos = vec(x, y, 0)
        else:
            if mag(self.p) != 0:
                self.sphere.pos += mag(self.p) * c**2 / sqrt((mag(self.p) * c)**2 + (m*c**2)**2) * dt * norm(self.p)

    def collision(self, in_dir, out_dir, E_i, E_f):
        p_i = E_i / c * norm(in_dir)
        p_f = E_f / c * norm(out_dir)
        p_e = p_i - p_f
        self.p += p_e
        self.active = False
        self.sphere.color = color.yellow

    def elec_collision(self, other):
        n = norm(self.sphere.pos - other.sphere.pos)
        p_self_n = dot(self.p, n)
        p_other_n = dot(other.p, n)
        J = 0.5 * 2 * (m * p_self_n - m * p_other_n) / (m + m) * n
        self.p -= J
        other.p += J

class electron:
    def __init__(self, position):
        self.position = position
        self.p = vec(0,0,0) #initial momentum

    def create_electron(self):
        self.sphere = sphere(pos=self.position, radius=1, color=color.cyan, momentum = (mag(self.p)**0.07)*norm(self.p))
        self.momentum_arrow = attach_arrow(self.sphere, 'momentum', scale = 2, shaftwidth = self.sphere.radius / 3)#momentum vectors!
        if attached_vec:
            self.momentum_arrow.start()
        else: 
            self.momentum_arrow.stop()

    def electron_step(self):
        if mag(self.p) != 0:
            self.sphere.pos += mag(self.p) * c**2 / sqrt((mag(self.p) * c)**2 + (m*c**2)**2) * dt * norm(self.p)
        if mag(self.sphere.pos) > 40:
            self.sphere.visible = False
            self.momentum_arrow.stop()
            electrons.remove(self)
            

    def collision(self, in_dir, out_dir, E_i, E_f): #electron direction from conservation of momentum
        p_i = E_i / c * norm(in_dir)
        p_f = E_f / c * norm(out_dir)
        p_e = p_i - p_f
        self.p += p_e
        self.sphere.momentum = (mag(self.p)**0.07)*norm(self.p)
        if attached_vec: 
            self.momentum_arrow.start()

    def elec_collision(self, other):
        n = norm(self.sphere.pos - other.sphere.pos) #normal vector
        p_self_n = dot(self.p, n)
        p_other_n = dot(other.p, n)
        J = 0.5 * 2 * (m * p_self_n - m * p_other_n) / (m + m) * n #impulse along normal vector, divided by two since double counted (SHOULD FIX)
        self.p -= J
        other.p += J
        self.sphere.momentum = self.p
        if attached_vec: 
            self.momentum_arrow.start()
        
class positron:
    def __init__(self, position):
        self.position = position
        self.p = vec(0,0,0) #initial momentum

    def create_positron(self):
        self.sphere = sphere(pos=self.position, radius=1, color=color.red, momentum = self.p)
        self.momentum_arrow = attach_arrow(self.sphere, 'momentum', scale = 0.5, shaftwidth = self.sphere.radius / 3)#momentum vectors!
        if attached_vec:
            self.momentum_arrow.start()
        else: 
            self.momentum_arrow.stop()

    def positron_step(self):
        self.sphere.momentum = self.p
        if mag(self.p) != 0:
            self.sphere.pos += mag(self.p) * c**2 / sqrt((mag(self.p) * c)**2 + (m*c**2)**2) * dt * norm(self.p)
        if mag(self.sphere.pos) > 40:
            self.sphere.visible = False
            self.momentum_arrow.stop()
            positrons.remove(self)

    def collision(self, in_dir, out_dir, E_i, E_f): #positron direction from conservation of momentum
        p_i = E_i / c * norm(in_dir)
        p_f = E_f / c * norm(out_dir)
        p_e = p_i - p_f
        self.p += p_e
        if attached_vec: 
            self.momentum_arrow.start()

    def posi_collision(self, other):
        n = norm(self.sphere.pos - other.sphere.pos) #normal vector
        p_self_n = dot(self.p, n)
        p_other_n = dot(other.p, n)
        J = 0.5 * 2 * (m * p_self_n - m * p_other_n) / (m + m) * n #impulse along normal vector, divided by two since double counted (SHOULD FIX)
        self.p -= J
        other.p += J
        if attached_vec: 
            self.momentum_arrow.start()

#making electrons, photons, and positrons
electrons = []
positrons = []
photons = []
atom =  None
orbit_e = None
scene.bind('click', click_electron)

def click_electron(evt):
    for elect in electrons:
        if mag(vec(evt.pos.x, evt.pos.y, 0) - elect.sphere.pos) < elect.sphere.radius and not running:
            elect.sphere.visible = False
            elect.momentum_arrow.stop()
    keys = keysdown()
    if running or 'e' not in keysdown() or bohr:
        return None
    inside = False
    for elect in electrons:
        if mag(vec(evt.pos.x, evt.pos.y, 0) - elect.sphere.pos) < 1.8 * elect.sphere.radius and not running:
            inside = True
    if inside == False:
        e = electron(vec(evt.pos.x, evt.pos.y, 0))
        e.create_electron()
        electrons.append(e)
        
scene.bind('click', click_photon)

def click_photon(evt):
    for phot in photons:
        if mag(vec(evt.pos.x, evt.pos.y, 0) - phot.pos) < 1 and not running:
            phot.curv.clear()
    if running:
        return None
    keys = keysdown()
    if 'p' in keys:
        p = photon(c/freq, vec(evt.pos.x, evt.pos.y, 0), 0)
        p.create_photon()
        photons.append(p) 

# widgets
runSim = button(bind = change_running, text = 'Run')
reset = button(bind = reset, text = 'reset')
wtext(text='   Bohr Model')
bohr_check = checkbox(bind = bohr_sim)
spacer = wtext(text='\n')
frequency = slider(bind = change_freq, min = 0, max = 1, step = 0.0001, value = log_to_linear_freq(freq))
frequency_text = wtext(text = f'Frequency: {freq:.4f}\n')
wl_label = wtext(text='')
click_text = wtext(text='Hold down e and click on the canvas to place electrons.\nHold down p and click to place photons. \nThen run. Objects cannot be placed while running.\n')
update_wl_label(c/freq)
wtext(text = 'Attach Momentum Vectors')
attach_vec_checkbox = checkbox(bind = attach_vec) 

# checkbox, set model

def change_freq(evt):
    global freq
    freq = linear_to_log_freq(evt.value)
    frequency_text.text = f'Frequency: {freq:.4f}\n'
    update_wl_label(c/freq)

def reset():
    global running, photons, electrons, init_Ei, init_iM, orbit_e, atom
    running = False
    runSim.text = 'Run'
    for phot in photons:
        phot.curv.clear()
    photons.clear()
    for elect in electrons:
        elect.sphere.visible = False
        elect.momentum_arrow.stop()
    electrons.clear()
    atom.nucleus.visible = False
    atom.c_ring.clear()
    
    if bohr:
        atom = bohr_model()
        atom.create_nucleus()
        atom.create_rings(bohr_radius(1))
        orbit_e = orbital_electron(1)
        electrons.append(orbit_e)
        

    init_Ei = 0
    init_iM = 0

    bar_Ei.data   = []
    bar_Ef.data   = []
    bar_Ke.data   = []
    bar_Etot.data = []
    update_energy_graph(h * freq, 0, 0)

    bar_iM.data   = []
    bar_fM.data   = []
    bar_eM.data   = []
    bar_Mtot.data = []
    update_momenta_graph(h * freq, 0, 0)
    update_wl_label(c/freq)
    
    hist_bars.data = []

def change_running(evt):
    global running
    if running:
        running = False
        runSim.text = 'Start'
    else: 
        running = True
        runSim.text = 'Stop'
    
def attach_vec(evt):
    global attached_vec
    global electrons
    if evt.checked:
        attached_vec = True
        for electron in electrons:
            electron.momentum_arrow.start()
    else: 
        attached_vec = False 
        for electron in electrons:
            electron.momentum_arrow.stop()
            
def bohr_sim(evt):
    global bohr, atom, orbit_e
    if evt.checked:
        bohr = True
        atom = bohr_model()
        atom.create_nucleus()
        atom.create_rings(bohr_radius(1))
        orbit_e = orbital_electron(1)
        electrons.append(orbit_e)
    else: 
        bohr = False
        atom.nucleus.visible = False
        orbit_e.sphere.visible = False
        atom.c_ring.clear()
        electrons.remove(orbit_e)

while True:
    rate(1000)
    if running and not bohr:
        for phot in photons:
            phot.photon_step()
            for elect in electrons:
                distance_front = mag(phot.pos + phot.dir - elect.sphere.pos)  # detect a little in front of photon
                if distance_front < elect.sphere.radius: #detect collision with electron

                    #store incoming direction, change angle based on distribution,
                    #store outgoing direction and update energy and wavelength
                    in_dir = phot.dir

                    if not phot.init_Ei_set:    # keep track of initial photon Ei if its first
                        phot.init_Ei = phot.E_i
                        phot.init_iM = phot.iM
                        phot.init_Ei_set = True
                        phot.init_iM_set = True

                    pre_collision_M = h / phot.wlength
                    pre_collision_dir = vec(phot.dir.x, phot.dir.y, 0)

                    phot.theta = kn_rejacc(phot.E_i)
                    phot.sign = sign(phot.theta)
                    phot.collision()
                    out_dir = phot.dir

                    phot.sum_K += phot.K

                    p_i_vec = pre_collision_M * norm(pre_collision_dir)
                    p_f_vec = phot.M * norm(out_dir)
                    p_e_vec = p_i_vec - p_f_vec

                    phot.sum_eM_x += p_e_vec.x
                    phot.sum_M_curr_x = p_f_vec.x # keep track of all affected electrons

                    update_energy_graph(phot.init_Ei, phot.E_f, phot.sum_K)
                    update_momenta_graph(phot.init_iM, phot.sum_M_curr_x, phot.sum_eM_x)
                    update_wl_label(phot.wlength)
                    update_histogram(phot.theta)

                    #calculate electrons momentum from photon's momentum
                    #then update the photon's internal time and initial position
                    elect.collision(in_dir, out_dir, phot.E_i, phot.E_f)
                    phot.ipos = elect.sphere.pos + phot.dir # so we don't get repeated collisions we start it a little forward
                    phot.pos = vec(phot.ipos.x, phot.ipos.y, 0)
                    phot.E_i = h * phot.freq
        for self in electrons:
            for other in electrons:
                if other is not self:
                    if mag(other.sphere.pos - self.sphere.pos) < self.sphere.radius:
                        self.elec_collision(other)
            self.electron_step()
    if running and bohr:
        for phot in photons:
            phot.photon_step()
            for elec in electrons:
                if not elec.active:
                    continue
                distance_front = mag(phot.pos + phot.dir - elec.sphere.pos)
                if distance_front < 2 * elec.sphere.radius:

                    in_dir = phot.dir

                    if not phot.init_Ei_set:
                        phot.init_Ei = phot.E_i
                        phot.init_iM = phot.iM
                        phot.init_Ei_set = True
                        phot.init_iM_set = True

                    pre_collision_M = h / phot.wlength
                    pre_collision_dir = vec(phot.dir.x, phot.dir.y, 0)

                    phot.theta = kn_rejacc(phot.E_i)
                    phot.collision()
                    out_dir = phot.dir

                    phot.sum_K += phot.K

                    p_i_vec = pre_collision_M * norm(pre_collision_dir)
                    p_f_vec = phot.M * norm(out_dir)
                    p_e_vec = p_i_vec - p_f_vec

                    phot.sum_eM_x += p_e_vec.x
                    phot.sum_M_curr_x = p_f_vec.x

                    update_energy_graph(phot.init_Ei, phot.E_f, phot.sum_K)
                    update_momenta_graph(phot.init_iM, phot.sum_M_curr_x, phot.sum_eM_x)
                    update_wl_label(phot.wlength)

                    elec.collision(in_dir, out_dir, phot.E_i, phot.E_f)
                    phot.ipos = elec.sphere.pos + phot.dir
                    phot.pos = vec(phot.ipos.x, phot.ipos.y, 0)
                    phot.E_i = h * phot.freq

        for elec in electrons:
            elec.electron_step()
