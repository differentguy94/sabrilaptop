# مهارة dwg-to-pdf — دليل التثبيت والاستخدام (عربي)

## ما هي
مهارة لـ Claude Code تحوّل ملفات AutoCAD (DWG/DXF) إلى PDF متعدد الصفحات (كل كادر صفحة A2 بدقة فيكتور مع
الحفاظ على العربي)، وتولّد مخططات تخصصية جديدة (كهرباء، صحي، تكييف، غاز، شفط، كاميرات، سماعات، أرضيات،
إنارة، أسقف، جدران، أثاث، واجهة) على نسخ من المخطط العام للعميل بأسلوب ZWORKS، مع الأبعاد والجداول والكميات،
وتُخرج DWG قابلاً للتعديل.

## التثبيت على الكمبيوتر
1. انسخ مجلد `dwg-to-pdf` كاملاً إلى أحد المكانين:
   - داخل مشروعك: `<المشروع>/.claude/skills/dwg-to-pdf/`  (تعمل في هذا المشروع فقط)
   - أو عام لكل المشاريع: `~/.claude/skills/dwg-to-pdf/`  (ويندوز: `C:\Users\<اسمك>\.claude\skills\dwg-to-pdf\`)
2. افتح VS Code → Claude Code في مجلد المشروع. اكتب `/dwg-to-pdf` أو فقط ارفع ملف DWG واطلب PDF؛
   Claude سيقرأ `SKILL.md` تلقائياً.
3. الأدوات المطلوبة على لينكس/ماك (السكربت `scripts/setup.sh` يثبّتها): python3 + ezdxf + pymupdf +
   arabic-reshaper + python-bidi، libredwg (dwg2dxf) عبر micromamba، وODA File Converter لإخراج DWG.
   على ويندوز الأسهل تشغيلها داخل WSL.

## محتويات المجلد
- `SKILL.md` — التعليمات التي يقرأها Claude (المسار السريع + كل الأخطاء التي تم حلها + قواعد المهندس).
- `scripts/dwg2pdf_frames.py` — سكربت الطباعة: DWG/DXF ← PDF كل كادر صفحة.
- `scripts/make_fonts.py`, `scripts/setup.sh` — الخطوط العربية/الإنجليزية المدمجة وتثبيت الأدوات.
- `reference/sheet_framework/` — إطار توليد المخططات التخصصية (مشروع Einstein Burger كاملاً كمثال):
  `lib.py` (فئة Sheet والرموز)، `sitemodel.py` (إحداثيات المخطط)، `SPEC.md` (متطلبات كل تخصص)،
  `disc_*.py` (15 تخصصاً)، `build.py`، `furn_catalog.py` (ملحق الأثاث بالصور)، `finalize.sh`،
  `furn_img/` (صور الأثاث 3D من Nano Banana).
- `reference/flip_zworks_shop.txt` — قائمة النصوص التي يُعكس ترتيب كلماتها في ملفات ZWORKS.
- `LESSONS.md` + `reference/corrections/` — دفتر ملاحظاتك وملفاتك المصحّحة ليتعلم منها Claude.

## كيف يتعلم من تعديلاتك
اقرأ `LESSONS.md`: ضع ملفك المعدّل في `reference/corrections/`، اكتب الملاحظة، ثم اطلب من Claude المقارنة.
