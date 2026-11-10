"""Распределение 12 задач фазы 3 UrbanFlow (MILP).
Запуск: python solve.py (из папки фазы 2)
Зависимости: scipy, numpy, openpyxl.
"""
from pathlib import Path
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from openpyxl import load_workbook

path=Path(__file__).with_name("phase-2.xlsx")
wb=load_workbook(path)
t=wb["Задачи"]; pr=wb["Предпочтения"]; params=wb["Параметры"]
n=t.max_row-1; m=4
h=np.array([float(t.cell(i+2,4).value) for i in range(n)])
p=np.array([[float(pr.cell(i+2,j+3).value) for j in range(m)] for i in range(n)])
delta=float(params["B2"].value); kmin=int(params["B3"].value)
def solve(d):
 A=[];lo=[];hi=[]
 def add(r,l,u): A.append(r);lo.append(l);hi.append(u)
 for i in range(n):
  r=np.zeros((n,m));r[i,:]=1;add(r.ravel(),1,1)
 for j in range(m):
  r=np.zeros((n,m));r[:,j]=h;add(r.ravel(),h.sum()/m-d,h.sum()/m+d)
  r=np.zeros((n,m));r[:,j]=1;add(r.ravel(),kmin,n)
  r=np.zeros((n,m));r[4,j]=1;r[5,j]=-1;add(r.ravel(),0,0)
 result=milp(-p.ravel(),integrality=np.ones(n*m),bounds=Bounds(0,1),constraints=LinearConstraint(np.array(A),lo,hi))
 if not result.success:return None,None
 return np.rint(result.x).astype(int).reshape(n,m),-result.fun
x,objective=solve(delta)
if x is None:raise SystemExit("Нет решения при выбранном допуске")
ws=wb["Распределение"]; names=[pr.cell(1,j+3).value for j in range(m)]
for i in range(n):
 j=int(np.argmax(x[i]));
 for jj in range(m):ws.cell(i+2,jj+3,int(x[i,jj]))
 ws.cell(i+2,7,names[j]);ws.cell(i+2,8,float(h[i]));ws.cell(i+2,9,float(p[i,j]))
for j in range(m):
 ws2=wb["Итоги"];ws2.cell(j+2,2,float(h@x[:,j]));ws2.cell(j+2,3,int(x[:,j].sum()));ws2.cell(j+2,4,float((p*x)[:,j].sum()))
wb["Итоги"]["B6"]=float(h.sum());wb["Итоги"]["C6"]=n;wb["Итоги"]["D6"]=float(objective)
for r,d in enumerate([.5,.75,1,1.5,3,1e6],2):
 xx,score=solve(d);s=wb["Чувствительность"];s.cell(r,1,"Без ограничения" if d>100 else d);s.cell(r,2,None if xx is None else float(score));s.cell(r,3,"нет решения" if xx is None else ", ".join(f"{v:g}" for v in h@xx))
wb.save(path)
print("Цель:",objective,"Нагрузки:",h@x)
