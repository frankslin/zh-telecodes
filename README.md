# 中文電報碼查詢 · 中國大陸 / 台灣 / 港澳

中文電報碼（中文商用電碼，Chinese Commercial Code, CCC）的網頁版檢索工具。它把三張碼表並列對照：中國大陸《標準電碼本》（1983）、台灣中文電碼，以及港澳銀行業使用的 SWIFT e-CCC 第二版。

## 功能

- **漢字 → 電碼**：輸入姓名或任意文字（如 `陳大文`），逐字列出三張表的電碼，並給出可複製的電碼串，例如 `7115 1129 2429`。
  - 某地碼表沒有這個字形時，先經繁簡或異體對應查得該地寫法，例如「國」在中國大陸為「国」0948，結果中標「轉換結果」。
  - 繁簡資料也對不上時，列出其他表所給碼位上該地的字，例如「鑱」7016 在中國大陸為「𰾠」，結果中標「同碼」。
- **電碼 → 漢字**：輸入四位一組的電碼，用空格分隔或直接連寫（`711511292429`）都可以，逐碼列出三張表在該碼位上的字。
- **統一碼**：支持 `U+9648` 格式。
- **碼位瀏覽**：0000–9999 全部碼位無限滾動。每個碼位按兩岸關係分為同字、繁簡對應、兩岸異字、僅中國大陸、僅台灣、非漢字六類，可按類篩選。
- **背景說明**：頁面底部是一篇連續的背景文章，含電碼本源流、兩岸四地（中國大陸、台灣、香港、澳門）現況、SWIFT 碼表、實例和參考資料。
- 頁面為繁體中文。簡體字用文津明體，繁體字用全字庫正宋體，缺字時互相回退。字號可調，支持深淺色主題，檢索狀態可以通過 URL hash 分享。
- 所有轉換均在瀏覽器本地執行，輸入內容不會上傳。

## 資料

| 碼表 | 來源 | 碼位數 |
|---|---|---|
| 中國大陸 | Unicode 18.0 Unihan `kMainlandTelegraph`，加上 NJStar 碼表中的非漢字碼 | 7,078 漢字 + 210 非漢字 |
| 台灣 | Unicode 18.0 Unihan `kTaiwanTelegraph`，加上 NJStar 碼表中的非漢字碼 | 9,026 漢字 + 93 非漢字 |
| SWIFT e-CCC v2 | SWIFT《Chinese Commercial Code》第二版 xlsx（2014 年起由 CCC Maintenance Group 維護） | 9,395 |
| hkhc/ccc（民間） | [hkhc/ccc](https://github.com/hkhc/ccc) `data/ccc-source-v2.txt`（@920846e，Apache-2.0） | 9,718 碼位、13,012 字 |

- NJStar 碼表由 Unicode 14.0 生成。其中的漢字碼與 Unihan 18.0 逐一比對，完全一致，所以只取它的非漢字碼（月份、注音、字母、標點等），這部分由 Jaemin Chung 整理。
- 繁簡對應綜合三處來源：Unihan 的 `kSimplifiedVariant` / `kTraditionalVariant`，OpenCC 的 `STCharacters` / `TSCharacters` / `TWVariants` / `HKVariants`，以及 SWIFT 表的繁簡配對。

### 香港

**香港沒有公開的官方電碼表。** 身份證上的電碼由入境事務處內部維護。根據數字政策辦公室 CSTF Paper 2003/01（`sources/person_name_cstf_200301.pdf`）及 Person Chinese Name 通用資料綱要（`sources/person_chinese_name_v1_0.xsd`）：

- 每個字是「4 位數字 + 1 位可選擴展位」，擴展位用來區分字形，身份證上只印前 4 位；
- [Person Chinese Name 通用資料綱要](https://www.digitalpolicy.gov.hk/en/our_work/data_governance/policies_standards/interoperability_framework/common_schemas/person_chinese_name/index.html)的「Related Code Lists」一項為「Nil」，即不附碼表。

常見姓氏的碼與台灣碼相同。網上的「香港身份證電碼」查詢站所用資料多為 Unihan 台灣碼。

同一綱要的示例 XML 演示了擴展位：「陳旻旼」編為 7115、2479、2479＋擴展位 2。但台灣碼 2479 是「旡」、「旼」是 8512，中國大陸「旻」是 2549，hkhc/ccc 的 2479 是「旡」「曆」，各表都對不上，未能確證入境處的實際碼位。

民間碼表 hkhc/ccc 每字帶來源層標記：無標記的基本層 7,567 字（7,435 字與台灣碼相同），另有 old、s1／s2／s3、china1／china2 各層。原作未說明各層含義；頁面上的解讀（old＝舊碼原字、s 層＝同碼位的另一寫法、china 層＝中國大陸簡化字及改填字）是逐碼比對後的推測。

SWIFT 表由中國大陸 1983 版與香港商務印書館 1972 版彙編而成，但以中國大陸版為對齊基準，所以它的繁體欄並不等於 1972 年香港版的原貌。頁面上把它標作「SWIFT（港澳）」，沒有標作「香港官方」。

### 澳門

澳門有正式公佈的官方電碼表：1985 年《澳門政府公報》第 40 期刊登的第 88/85/M 號法令，附件為《附有密碼及廣州音譯音之字音表》，其中「依電碼次序檢字」部分按 0000–9999 列出字形、電碼和葡式粵語拼音。法令至今有效。附件是沒有文字層的手寫掃描件（[PDF](https://images.bo.dsaj.gov.mo//bo/i/85/40/dl-88-1985-an.pdf)），本項目尚未把它數字化。

### 文件

```
index.html                 整個應用（HTML + CSS + 原生 JS，無需構建）
data.js                    window.TELECODE，由 scripts/gen_data.py 生成
scripts/gen_data.py        python3 scripts/gen_data.py（需要 openpyxl）
sources/
  Unihan_Telegraph.txt     Unihan_OtherMappings.txt 中的兩個電碼字段
  Unihan_STVariants.txt    Unihan_Variants.txt 中的繁簡變體字段
  njstar-*-codebook.html   NJStar 中國大陸 / 台灣碼表頁面
  njstar-telecode-history-*.html  電碼本沿革（中、英）
  swift_eccc_v2.xlsx       SWIFT e-CCC 第二版
  swift_ccc_mpg.pdf        PMPG Market Practice Guidelines (2025)
  person_name_cstf_200301.pdf, person_chinese_name_v1_0.xsd  香港特區政府姓名資料標準
  hkhc-ccc-source-v2.txt   hkhc/ccc 民間碼表
  opencc/                  OpenCC 單字字表
```

## 運行

純靜態單頁應用：先運行 `python3 -m http.server`，再打開 `index.html`。所有查詢都在瀏覽器本地完成，只有網絡字體需要聯網。
