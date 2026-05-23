Web VPython 3.2

scene.range = 10
scene.autoscale = False


c = 1
dl = 0.01
v = 5
dt = 0.001
init_d = 10
freq = 3 * pi
def cot(x):
    return 1 / tan(x)

#compton scattering constants and equations
m = 1
h = 1
E_i = h * freq


theta = 67 * 3.14 / 180
theta_current = theta

def find_phi(theta):
    if theta == 0 or theta == 3.14:
        return 0
    else:
        def f(phi):
            return cot(phi) - (1 + E_i / (m*c**2)) * (sin(theta) / (1 + cos(theta)))
        phi = 1.0
        
        #newtons method
        for i in range(20):
            h = 0.0001
            df = (f(phi + h) - f(phi - h)) / (2*h)
            phi -= f(phi)/df
        return phi

phi = find_phi(theta)
phi_current = phi

E_f = E_i / (1 + (E_i / (m * c**2)) * (1-cos(theta)))
K = E_i - E_f
v_e = c * sqrt(1 - 1/(1 + K/(m*c**2)**2))
v_e_current = 5 * v_e
lambda_i = 1/freq
lambda_f = h /(m*c) * (1 - cos(theta)) + lambda_i
freq_def = 1/lambda_f

# changing the angle 
def change_angle(evt):
    global phi, theta, E_f, K, v_e, lambda_f, freq_def
    theta = evt.value * 3.14 / 180
    phi = find_phi(theta)
    E_f = E_i / (1 + (E_i / (m * c**2)) * (1-cos(theta)))
    K = E_i - E_f
    v_e = sqrt(2 * K / m)
    lambda_f = h /(m*c) * (1 - cos(theta)) + lambda_i
    freq_def = 1/lambda_f
    angle_text.text = f'angle:{evt.value}'
    
angle_slider = slider(bind = change_angle, min = 0, max = 180, value = theta * 180 / 3.14, step = 1)
angle_text = wtext(text=f'Angle:{theta * 180 / 3.14}')

#creating particles
photon = curve(color=vec(1,0,0))

for i in range(400):
    dx = (i - 200) * dl
    photon.append(pos=vector(dx-init_d,exp(-((dx)**2)) * sin(freq * dx), 0))
    
electron = sphere(pos=vector(0,0,0), radius=0.5, color=color.cyan)

def photon_step(n):
    for i in range(photon.npoints):
        dx = (i - 200) * dl
        photon.modify(i, pos = vec(dx - init_d + n * v * dt, exp(-((dx)**2)) * sin(freq * (dx - init_d + n * v * dt)),0))
        
def electron_deflection():
        electron.pos += vec(abs(cos(phi_current)), - abs(sin(phi_current)),0) * v_e_current * dt 

n = 0        
while True:
    rate(1000)
    photon_step(n)
    n+=1
    if photon.point(photon.npoints-1).pos.x - electron.pos.x + electron.radius - 100 * dl > 0:
        photon.clear()
        phi_current = phi
        theta_current = theta
        v_e_current = v_e
        break

for i in range(400):
    dx = (i - 200) * dl
    photon.append(pos = rotate(vector(dx + electron.radius + 100 * dl, exp(-((dx)**2)) * sin(freq_def * dx), 0), angle = theta_current, axis = vec(0,0,1)))

def def_photon_step(n):
    for i in range(photon.npoints):
        dx = (i - 200) * dl
        photon.modify(i, pos = rotate(vec(dx + 100 * dl + electron.radius + n * v * dt, exp(-((dx)**2)) * sin(freq_def * (dx - init_d + n * v * dt)),0), angle = theta_current, axis = vec(0,0,1)))

n=0
while True:
    rate(1000)
    electron_deflection()
    def_photon_step(n)
    n+=1