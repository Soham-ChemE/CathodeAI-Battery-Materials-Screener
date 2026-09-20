import pickle, json, numpy as np, shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
st=pickle.load(open("repro_state_id.pkl","rb")); df=st["df_ml3"]; comb=st["combined_features"]
X3s=StandardScaler().fit_transform(df[comb].values); y=df["Energy Density (Wh/L)"].values
rf=RandomForestRegressor(n_estimators=200, random_state=42).fit(X3s,y)
sv=shap.TreeExplainer(rf).shap_values(X3s); msv=np.abs(sv).mean(0)
out={f:{"mean_abs_shap":float(v),"rf_importance":float(i)} for f,v,i in zip(comb,msv,rf.feature_importances_)}
json.dump(out,open("shap_id.json","w"),indent=1); np.savez("shap_values_id.npz", sv=sv, X=df[comb].values, y=y, features=np.array(comb))
fe=df["Formation Energy (eV/atom)"].values; fs=sv[:,comb.index("Formation Energy (eV/atom)")]
bins=np.linspace(fe.min(),fe.max(),25); mids=0.5*(bins[1:]+bins[:-1]); bm=[fs[(fe>=a)&(fe<b)].mean() if ((fe>=a)&(fe<b)).sum()>5 else np.nan for a,b in zip(bins[:-1],bins[1:])]
print("SHAP done"); print({f:round(v["mean_abs_shap"],2) for f,v in out.items()}); print("FE bins:", [(round(m,2),round(v,1)) for m,v in zip(mids,bm) if not np.isnan(v)])
