import os
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX



def metrics(y_true, y_pred):
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': mean_squared_error(y_true, y_pred, squared=False)
    }


def select_sarimax_order(train, seasonal=1, max_p=2, max_q=2, max_P=1, max_Q=1):
    best_aic = np.inf
    best_cfg = None
    # small grid search over (p,d,q)(P,D,Q,s)
    # ensure datetime index for statsmodels forecasting
    try:
        if not isinstance(train.index, pd.DatetimeIndex):
            train = train.copy()
            train.index = pd.to_datetime(train.index.astype(str) + '-01-01')
            # set yearly freq
            try:
                train.index.freq = 'YS'
            except Exception:
                pass
    except Exception:
        pass
    for p in range(0, max_p + 1):
        for d in [0, 1]:
            for q in range(0, max_q + 1):
                for P in range(0, max_P + 1):
                    for D in [0, 1]:
                        for Q in range(0, max_Q + 1):
                            # seasonal period must be >0 to use seasonal terms
                            if seasonal <= 1 and (P != 0 or D != 0 or Q != 0):
                                continue
                            try:
                                order = (p, d, q)
                                seasonal_order = (P, D, Q, seasonal if seasonal > 1 else 0)
                                mod = SARIMAX(train, order=order, seasonal_order=seasonal_order,
                                              enforce_stationarity=False, enforce_invertibility=False)
                                res = mod.fit(disp=False)
                                if res.aic < best_aic:
                                    best_aic = res.aic
                                    best_cfg = (order, seasonal_order)
                            except Exception:
                                continue
    return best_cfg


def rolling_forecast_sarimax_grid(series, initial_train_frac=0.6, fh=1, seasonal=1):
    n = len(series)
    initial = int(n * initial_train_frac)
    preds = []
    trues = []
    for t in range(initial, n - fh + 1):
        train = series.iloc[:t]
        test = series.iloc[t:t + fh]
        # convert index to datetime for forecasting stability
        try:
            if not isinstance(train.index, pd.DatetimeIndex):
                train = train.copy()
                train.index = pd.to_datetime(train.index.astype(str) + '-01-01')
        except Exception:
            pass
        cfg = select_sarimax_order(train, seasonal=seasonal)
        if cfg is None:
            # fallback to simple order
            order = (1, 1, 1)
            seasonal_order = (0, 0, 0, 0)
        else:
            order, seasonal_order = cfg
        try:
            mod = SARIMAX(train, order=order, seasonal_order=seasonal_order,
                          enforce_stationarity=False, enforce_invertibility=False)
            res = mod.fit(disp=False)
            fc = res.get_forecast(steps=fh).predicted_mean
            preds.extend(fc.tolist())
            trues.extend(test.tolist())
        except Exception:
            # if fit fails, use last value as forecast
            preds.append(train.iloc[-1])
            trues.extend(test.tolist())
    return np.array(trues), np.array(preds)


def run_backtest_for_country(df_country, country_name, seasonality=1):
    series = df_country.set_index('year')['happiness_score'].sort_index()
    # if years are sparse, just use index-based rolling
    trues, preds = rolling_forecast_sarimax_grid(series, seasonal=seasonality)
    # naive baseline: repeat last seen value
    naive = []
    n = len(series)
    initial = int(n * 0.6)
    for t in range(initial, n):
        naive.append(series.iloc[t-1])
    naive = np.array(naive)
    res = {
        'country': country_name,
        **{f'sarimax_{k}': v for k, v in metrics(trues, preds).items()},
        **{f'naive_{k}': v for k, v in metrics(trues, naive).items()}
    }
    return res


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(root, 'dataset', 'dataset.csv')
    df = pd.read_csv(data_path)
    # pick latest year per country to ensure yearly series
    results = []
    total = df['country'].nunique()
    i = 0
    max_countries = 30
    c_iter = iter(df.groupby('country'))
    processed = 0
    for country, g in c_iter:
        if processed >= max_countries:
            break
        g_sorted = g.sort_values('year')
        if g_sorted['year'].nunique() < 8:
            # skip too-short series
            continue
        try:
            i += 1
            print(f"Processing {i}/{total}: {country}")
            # use grid-based sarimax backtest
            # adapt run_backtest_for_country to call rolling_forecast_sarimax_grid
            series = g_sorted.set_index('year')['happiness_score'].sort_index()
            trues, preds = rolling_forecast_sarimax_grid(series, seasonal=1)
            naive = []
            n = len(series)
            initial = int(n * 0.6)
            for t in range(initial, n):
                naive.append(series.iloc[t-1])
            naive = np.array(naive)
            r = {
                'country': country,
                **{f'sarimax_{k}': v for k, v in metrics(trues, preds).items()},
                **{f'naive_{k}': v for k, v in metrics(trues, naive).items()}
            }
            results.append(r)
            processed += 1
            # periodic flush
            if len(results) % 10 == 0:
                pd.DataFrame(results).to_csv(os.path.join(root, 'sarimax_backtest_summary_partial.csv'), index=False)
        except Exception as e:
            print('failed', country, repr(e))
            # continue to next country
            continue

    out = pd.DataFrame(results)
    if not out.empty and 'sarimax_RMSE' in out.columns:
        out = out.sort_values('sarimax_RMSE')
    out.to_csv(os.path.join(root, 'sarimax_backtest_summary.csv'), index=False)
    print('done — summary written to sarimax_backtest_summary.csv')


if __name__ == '__main__':
    main()
