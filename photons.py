Web VPython 3.2

scene.range = 10
photon = curve(color=color.yellow)
scene.autoscale = False

dl = 0.01
v = 4
dt = 0.001
init_d = 10
    
for i in range(400):
    dx = (i - 200) * dl
    photon.append(pos=vector(dx-init_d,exp(-((dx)**2))*sin(2*pi*dx), 0))

def photon_step(n):
    for i in range(photon.npoints):
        dx = (i - 200) * dl
        photon.modify(i, pos = vec(dx - init_d + n * v * dt, exp(-((dx)**2))*sin(2*pi*(dx - n * dt)),0))

n = 0        
while True:
    rate(1000)
    photon_step(n)
    n+=1
