from scipy import linspace, polyval, polyfit, sqrt, stats, randn, array, fftpack 
from pylab import plot, title, show , legend, bar, axis, grid

import datetime
from stock_obj import stock

#Linear regression example
# This is a very simple example of using two scipy tools 
# for linear regression, polyfit and stats.linregress

sym = 'ge'
st = stock(sym)
sd = st.get_hist()
sn = []
st = []
sc = []
sl = []
sh = []
i=0
for rec in sd:
#    sn.append(float(sd.line_num))
    sn.append(float(i))
    i += 1
    st.append(rec['Date'])
    sc.append(float(rec['Close']))
    sl.append(float(rec['Low']))
    sh.append(float(rec['High']))

# print sn,st,sx
print len(sn), len(st), len(sc)

n=len(sn)
t = array(sn[::-1])
xc = array(sc)

#Linear regressison -polyfit - polyfit can be used other orders polys
(ar,br)=polyfit(t,xc,1)
lc=polyval([ar,br],t)
#compute the mean square error
err=sqrt(sum((lc-xc)**2)/n)

print('Linear regression using polyfit')
print('parameters: regression: a=%.2f b=%.2f, ms error= %.3f' % (ar,br,err))

xl = array(sl)
#Linear regressison -polyfit - polyfit can be used other orders polys
(ar,br)=polyfit(t,xl,1)
ll=polyval([ar,br],t)

xh = array(sh)

#Linear regressison -polyfit - polyfit can be used other orders polys
(ar,br)=polyfit(t,xh,1)
lh=polyval([ar,br],t)

#matplotlib ploting
title('Linear Regression Example')
plot(t,lc,'b-')
plot(t,xc,'k+')
plot(t,ll,'r-')
plot(t,lh,'g-')
legend(['original',sym, 'regression'])

show()

#Linear regression using stats.linregress
(a_s,b_s,r,tt,stderr)=stats.linregress(t,xc)
print('Linear regression using stats.linregress')
print('parameters: regression: a=%.2f b=%.2f, std error= %.3f' % (a_s,b_s,stderr))

fs = fftpack.rfft(xc)

afs = abs(fs)
aafs = afs.argsort()
#       print aafs[i],afs[i]
fss = fftpack.rfft(xc)
k=0
for i in aafs[::-1]:
    if k > 8:
        fss[i] = 0
    else:
        k += 1

#matplotlib ploting
title('fft Example')
plot(t,fs,'r-')
plot(t,fss,'g-')
bar(t, fss, width=0.5, bottom=0)
axis([len(xc+10), 0, -50, 50])
grid(True)
legend(['fft coeffs','fft coeffs after',sym])

show()

#n, bins, patches = hist(fs, len(fs), facecolor='blue')
#bar(t, fs, width=0.5, bottom=0)
#axis([0, 300, -500, 500])

#show()


fis = fftpack.irfft(fss)
#matplotlib ploting
title('ifft Example')
plot(t,fis,'g-')
plot(t,xc,'k+')
legend(['ifft from fft coeffs',sym])

show()

from matplotlib.mlab import specgram
ps, spc, spt = specgram(xc, NFFT=len(xc), Fs=len(xc))
print type(spc), len(spc), type(xc), len(xc), type(t), len(t)
#matplotlib ploting
title('Spectrum Example')
plot(t[0:142],spc,'r-')
#plot(t,xc,'k+')
legend(['spectrum',sym])

show()
