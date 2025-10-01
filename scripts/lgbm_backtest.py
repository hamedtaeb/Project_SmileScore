import os
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from lightgbm import LGBMRegressor
except Exception:
    LGBMRegressor = None


def metrics(y_true, y_pred):
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': mean_squared_error(y_true, y_pred, squared=False)
    }


def make_lag_features(series, lags=(1,2,3)):
    df = pd.DataFrame({'y': series.copy()})
    for lag in lags:
        df[f'lag_{lag}'] = df['y'].shift(lag)
    df = df.dropna()
    return df


def rolling_forecast_lgbm(series, lags=(1,2,3), initial_frac=0.6, fh=1):
    # series: pd.Series indexed by year or datetime
    df = make_lag_features(series, lags=lags).reset_index(drop=True)
    S = len(series)
    offset = max(lags)
    initial = int(S * initial_frac)
    preds = []
    trues = []
    # For a given t (index in original series), the corresponding row in df starts at position 0 -> series index offset
    # So the df row that corresponds to series position t is (t - offset)
    for t in range(initial, S - fh + 1):
        train_end = t - offset  # number of rows in df to use for training
        test_start = train_end
        test_end = test_start + fh
        if train_end <= 0 or test_end > len(df):
            continue
        train = df.iloc[0:train_end].copy()
        test = df.iloc[test_start:test_end].copy()
        if train.empty or test.empty:
            continue
        X_train = train.drop(columns=['y']).values
        y_train = train['y'].values
        X_test = test.drop(columns=['y']).values
        # fit model
        if LGBMRegressor is None:
            # fallback: mean predictor
            y_pred = np.repeat(y_train.mean(), fh)
        else:
            model = LGBMRegressor(n_estimators=200, random_state=7)
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            except Exception:
                y_pred = np.repeat(y_train.mean(), fh)
        preds.extend(y_pred.tolist())
        trues.extend(test['y'].tolist())
    return np.array(trues), np.array(preds)


def run_backtest(df, max_countries=30):
    results = []
    total = df['country'].nunique()
    processed = 0
    for i, (country, g) in enumerate(df.groupby('country')):
        if processed >= max_countries:
            break
        g_sorted = g.sort_values('year')
        if g_sorted['year'].nunique() < 8:
            continue
        try:
            print(f'[{processed+1}/{min(max_countries,total)}] Processing {country}')
            series = g_sorted.set_index('year')['happiness_score'].sort_index()
            trues, preds = rolling_forecast_lgbm(series, lags=(1,2,3), initial_frac=0.6)
            if len(trues) == 0:
                continue
            # naive baseline
            naive = []
            n = len(series)
            initial = int(n * 0.6)
            for t in range(initial, n):
                naive.append(series.iloc[t-1])
            naive = np.array(naive[:len(trues)])
            r = {
                'country': country,
                **{f'lgbm_{k}': v for k, v in metrics(trues, preds).items()},
                **{f'naive_{k}': v for k, v in metrics(trues, naive).items()}
            }
            results.append(r)
            processed += 1
        except Exception as e:
            print('failed', country, repr(e))
            continue
    return pd.DataFrame(results)


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(root, 'dataset', 'dataset.csv')
    df = pd.read_csv(data_path)
    out = run_backtest(df, max_countries=30)
    out.to_csv(os.path.join(root, 'lgbm_backtest_summary.csv'), index=False)
    print('wrote lgbm_backtest_summary.csv with', len(out), 'rows')

    # merge with sarimax summary if present
    sarimax_path = os.path.join(root, 'sarimax_backtest_summary.csv')
    if os.path.exists(sarimax_path):
        sar = pd.read_csv(sarimax_path)
        merged = sar.merge(out, on='country', how='outer')
        merged.to_csv(os.path.join(root, 'model_comparison.csv'), index=False)
        print('wrote model_comparison.csv')


if __name__ == '__main__':
    main()
