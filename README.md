# AutoTrade Optimizer (MVP)

画像仕様の要点（自動売買最適化・バックテスト・リスク管理）に合わせ、まず動く最小実装を用意しました。

## できること
- 価格系列に対するSMAクロス戦略のバックテスト
- パラメータグリッド探索による戦略最適化
- リスク率とストップ幅ベースのポジションサイズ計算
- CSV入力 or モックデータでCLI実行

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 実行
```bash
autotrade-opt --points 365
# or
autotrade-opt --csv ./prices.csv
```

CSVは以下カラムを想定:
- `timestamp`
- `close`

## テスト
```bash
pytest
```

## 構成
- `src/autotrade_optimizer/data.py`: データ入出力
- `src/autotrade_optimizer/risk.py`: リスク管理
- `src/autotrade_optimizer/engine.py`: バックテスト・最適化
- `src/autotrade_optimizer/cli.py`: CLI
