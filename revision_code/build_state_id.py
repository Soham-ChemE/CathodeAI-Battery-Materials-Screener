"""Build repro_state_id.pkl: the identifier-level ML state used by the revised manuscript.
Run after repro_pipeline.py and analysis_ml.py (which writes df_id_merge.pkl)."""
import pickle, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
st = pickle.load(open("repro_state.pkl", "rb")); df_id = pd.read_pickle("df_id_merge.pkl")
comb = st["combined_features"]; target = "Energy Density (Wh/L)"
X3 = StandardScaler().fit(df_id[comb].values); Xs = X3.transform(df_id[comb].values); y = df_id[target].values
Xtr, Xte, ytr, yte = train_test_split(Xs, y, test_size=0.2, random_state=42)
rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(Xtr, ytr)
print(f"ID-level combined held-out test R2 {r2_score(yte, rf.predict(Xte)):.4f}, MAE {mean_absolute_error(yte, rf.predict(Xte)):.1f}, n={len(df_id)}")
df_id = df_id.copy(); df_id["n_polymorphs"] = 1  # each row carries its own discharge structure
st.update({"df_ml3": df_id, "X3scaler": X3, "rf_combined": rf, "y3_test": yte, "X3_test": Xte})
pickle.dump(st, open("repro_state_id.pkl", "wb")); print("Saved repro_state_id.pkl")
