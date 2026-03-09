# 書籍『SAR衛星データ解析入門』サポートページ

本書をご利用いただきありがとうございます。

## 付録

付録の章である**フーリエ変換と相関処理**については、[Github](../book/appendix.pdf)から無料で配布しております。

## 正誤表

現時点で判明している誤記・修正点を以下にまとめました。
正誤表にない誤りや不具合、疑問点がありましたら、GitHubのIssueにてご連絡ください。

- Issue: https://github.com/syu-tan/sar-python-book/issues
- 可能であれば「ページ番号」「図/表/コードの位置」「該当箇所の文言」を添えて下さると助かります。

最終更新日：2026年2月11日

### 初版 / 第１刷

| ページ | 正しい | 誤り |
| --- | --- | --- |
| P.13 | **図1.1.25** 下から二番目の図 凡例: `Peak` | **図1.1.25** 下から二番目の図 凡例: `Peck` |
| P.13 | **図1.1.25** 一番下の図 縦軸: `Spectrum` | 図1.1.25 一番下の図 縦軸: `Spectum` |
| P.81 | **図1.4.40** 左から二番目の図 タイトル: `Ambiguity Distance from Real Object [m]` | **図1.4.40** 左から二番目の図 タイトル: `Ambiguity Distnace from Real Object [m]` |
| P.148 | **図1.5.85** 凡例: `Observation` | **図1.5.85** 凡例: `Obsevation` |
| P.149 | **図1.5.88** 凡例: `Observation` | **図1.5.88** 凡例: `Obsevation` |
| P.150 | **図1.5.89** 凡例: `Observation` | **図1.5.89** 凡例: `Obsevation` |
| P.152 | **図1.5.91** 凡例: `Terrain` | **図1.5.91** 凡例: `Terran` |
| P.287 | **図3.4.20**（左）（右） タイトル: Interferogram Phase & Intensity | **図3.4.20**（左）（右） タイトル: Interferogrum Phase & Intency |
| P.302 | **図3.4.50** 凡例: `Descending Difference Vector` | **図3.4.50** 凡例: `Dsscending Difference Vector` |
| P.302 | **図3.4.51** 凡例: `Descending Difference Vector`, `Ascending Difference Vector Normal` | **図3.4.50** 凡例: `Dsscending Difference Vector`, `Ascending Difference Vector Notmal` |
| P.302 | **図3.4.53** 凡例: `Descending Difference Vector`, `Ascending Difference Vector Normal`, `Quasi North-South Vector` | `Dsscending Difference Vector`, `Ascending Difference Vector Notmal`, `Quasi North-Sputh Vector` |

### コードブロック

P.221 の不正確なインデント

#### 正しい

```python
window = rio.windows.Window(col_off=2040, row_off=4100, width=230, height=220)
transform = rio.windows.transform(window, src.transform)
out_meta.update({
    "driver": "GTiff",
    "height": window.height,
    "width": window.width,
    "transform": transform,
    "dtype": "float32"})
img_clip = sigma[window.row_off:window.row_off+window.height, window.col_off:
window.col_off+window.width]
```

#### 誤り
```python
window = rio.windows.Window(col_off=2040, row_off=4100, width=230, height=220)
    transform = rio.windows.transform(window, src.transform)
    out_meta.update({
        "driver": "GTiff",
        "height": window.height,
        "width": window.width,
        "transform": transform,
        "dtype": "float32"})
    img_clip = sigma[window.row_off:window.row_off+window.height, window.col_off:
window.col_off+window.width]
```


