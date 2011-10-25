from scipy import linspace, polyval, polyfit, sqrt, stats, randn, array
from pylab import plot, title, show , legend
import datetime
from stock_obj import stock

#Linear regression example
# This is a very simple example of using two scipy tools 
# for linear regression, polyfit and stats.linregress

sym = 'amzn'
st = stock(sym)
sd = st.get_hist()
sn = []
st = []
sx = []
for rec in sd:
    sn.append(float(sd.line_num))
    st.append(rec['Date'])
    sx.append(float(rec['Close']))

# print sn,st,sx
print len(sn), len(st), len(sx)

n=len(sn)
t = array(sn[::-1])
xn = array(sx)

#Linear regressison -polyfit - polyfit can be used other orders polys
(ar,br)=polyfit(t,xn,1)
xr=polyval([ar,br],t)
#compute the mean square error
err=sqrt(sum((xr-xn)**2)/n)

print('Linear regression using polyfit')
print('parameters: regression: a=%.2f b=%.2f, ms error= %.3f' % (ar,br,err))

#matplotlib ploting
title('Linear Regression Example')
plot(t,sx,'g-')
plot(t,xn,'k+')
plot(t,xr,'r-')
legend(['original',sym, 'regression'])

show()

#Linear regression using stats.linregress
(a_s,b_s,r,tt,stderr)=stats.linregress(t,xn)
print('Linear regression using stats.linregress')
print('parameters: regression: a=%.2f b=%.2f, std error= %.3f' % (a_s,b_s,stderr))
