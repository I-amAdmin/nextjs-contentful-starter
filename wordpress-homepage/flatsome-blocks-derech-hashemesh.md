# דרך השמש — עמוד בית מכירתי 2026 · בלוקים לפלאטסום (Flatsome UX Builder)

## איך מטמיעים
1. בוורדפרס: **UX Blocks ← Add New** — צרו בלוק לכל מקטע (שם הבלוק מופיע בכותרת של כל קטע כאן), והדביקו את הקוד בעורך הטקסט (Text mode) של הבלוק.
2. בעמוד הבית: הוסיפו את הבלוקים לפי הסדר עם `[block id="..."]`, או הדביקו כל מקטע ישירות בעמוד דרך UX Builder ← Edit as Text.
3. **צבעים**: הוסיפו פעם אחת את ה־CSS שבבלוק 0 ב־**Flatsome ← Advanced ← Custom CSS**. כל הצבעים מרוכזים שם — עדכנו את קודי ה־HEX לפי צבעי הלוגו המדויקים שלכם ואל תיגעו בשאר.
4. **לוגו והדר/פוטר**: נשארים ההדר והפוטר הקיימים של האתר — הבלוקים כאן הם גוף העמוד בלבד.
5. החליפו את כתובות התמונות (`[IMG-...]`) בתמונות מספריית המדיה, ואת `ids=""` ב־ID של המוצרים האמיתיים.

---

## בלוק 0 — CSS מותג (Flatsome → Advanced → Custom CSS)

```css
:root{
  --ds-sun:#E09A2D;      /* ענבר-שמש — עדכנו לפי הלוגו */
  --ds-sun-deep:#C77F14; /* ענבר כהה — hover */
  --ds-roast:#33241A;    /* חום קלוי — טקסט/רקע כהה */
  --ds-cream:#FAF4EA;    /* קרם — רקע */
  --ds-cream2:#F2E7D5;   /* קרם כהה — הפרדות */
  --ds-olive:#75713F;    /* זית — אקצנט */
}
.ds-kicker{color:var(--ds-sun-deep);font-weight:700;letter-spacing:.12em;font-size:14px}
.ds-btn-main{background:var(--ds-sun)!important;color:var(--ds-roast)!important;border-radius:99px!important;border:0!important;font-weight:700}
.ds-btn-main:hover{background:var(--ds-sun-deep)!important;color:#fff!important}
.ds-btn-ghost{background:transparent!important;color:var(--ds-roast)!important;border:2px solid var(--ds-roast)!important;border-radius:99px!important;font-weight:700}
.ds-btn-ghost:hover{background:var(--ds-roast)!important;color:var(--ds-cream)!important}
.ds-card{background:#fff;border:1px solid var(--ds-cream2);border-radius:20px;padding:36px 28px;height:100%}
.ds-num{font-size:44px;font-weight:900;color:var(--ds-sun);line-height:1;margin-bottom:12px}
.ds-quote{background:#fff;border:1px solid var(--ds-cream2);border-radius:20px;padding:32px;height:100%}
.ds-stars{color:var(--ds-sun);letter-spacing:3px;font-size:18px}
.ds-stat b{display:block;font-size:36px;font-weight:900;color:var(--ds-sun)}
.ds-trust strong{color:var(--ds-sun)}
```

---

## בלוק 1 — HERO (שם בלוק: `home-hero`)

```
[section bg_color="#FAF4EA" padding="90px" padding__sm="50px"]
  [row v_align="middle"]
    [col span="7" span__sm="12"]
      [ux_text]
        <p class="ds-kicker">קלייה במקום · כל יום · כפר סבא</p>
        <h1 style="font-size:56px;font-weight:900;line-height:1.15;">פיצוחים שנקלים <span style="color:#C77F14;">הבוקר</span>,<br>מגיעים אליכם <span style="color:#C77F14;">היום</span>.</h1>
        <p style="font-size:18px;max-width:600px;">בדרך השמש אנחנו קולים פקאנים, אגוזים ופיצוחים במקום מדי יום — בלי מחסנים, בלי "יושב על המדף". טריות שמרגישים בביס הראשון, עם משלוח חינם עד הבית בכפר סבא ואורנית.</p>
      [/ux_text]
      [gap height="20px"]
      [button text="להזמנה עם משלוח מהיום להיום" class="ds-btn-main" size="large" link="/shop/"]
      [button text="לצפייה בכל המוצרים" class="ds-btn-ghost" size="large" link="/shop/"]
    [/col]
    [col span="5" span__sm="12"]
      [ux_image id="[IMG-HERO]" image_size="large" style="border-radius:20px;overflow:hidden;"]
    [/col]
  [/row]
[/section]
```

---

## בלוק 2 — פס אמון (שם בלוק: `home-trust-bar`)

```
[section bg_color="#33241A" padding="24px" class="ds-trust"]
  [row h_align="center"]
    [col span="3" span__sm="6" align="center"][ux_text][p style="color:#FAF4EA;margin:0;"]<strong>קלייה טרייה במקום</strong> מדי יום[/p][/ux_text][/col]
    [col span="3" span__sm="6" align="center"][ux_text][p style="color:#FAF4EA;margin:0;"]<strong>משלוח חינם</strong> כפר סבא ואורנית — מהיום להיום[/p][/ux_text][/col]
    [col span="3" span__sm="6" align="center"][ux_text][p style="color:#FAF4EA;margin:0;"]<strong>כשרות בד״צ</strong> על כל המוצרים[/p][/ux_text][/col]
    [col span="3" span__sm="6" align="center"][ux_text][p style="color:#FAF4EA;margin:0;"]<strong>מאז 2016</strong> — ויצמן 121, כפר סבא[/p][/ux_text][/col]
  [/row]
[/section]
```

---

## בלוק 3 — למה דרך השמש (שם בלוק: `home-why-us`) — טיפוגרפי, ללא אייקונים

```
[section bg_color="#FAF4EA" padding="80px"]
  [row]
    [col span="12"]
      [ux_text]
        <p class="ds-kicker">למה דרך השמש</p>
        <h2 style="font-size:40px;font-weight:900;">ההבדל בין "פיצוחים" לפיצוחים טריים באמת</h2>
      [/ux_text]
    [/col]
  [/row]
  [row]
    [col span="3" span__sm="12"][ux_text][div class="ds-card"]<div class="ds-num">01</div><h3>נקלה כאן. לא במפעל.</h3><p>הקלייה מתבצעת בחנות עצמה, בכמויות קטנות — כך כל שקית יוצאת בשיא הטריות והפריכות.</p>[/div][/ux_text][/col]
    [col span="3" span__sm="12"][ux_text][div class="ds-card"]<div class="ds-num">02</div><h3>מהקולה — לדלת שלכם</h3><p>הזמנתם עד הצהריים? המשלוח יוצא אליכם עוד היום, חינם, לכפר סבא ואורנית.</p>[/div][/ux_text][/col]
    [col span="3" span__sm="12"][ux_text][div class="ds-card"]<div class="ds-num">03</div><h3>איכות שאפשר לטעום</h3><p>אנחנו בוררים ידנית את הפקאנים והאגוזים, וקולים בטמפרטורה מדויקת שמוציאה את מלוא הטעם.</p>[/div][/ux_text][/col]
    [col span="3" span__sm="12"][ux_text][div class="ds-card"]<div class="ds-num">04</div><h3>עסק משפחתי, שירות אישי</h3><p>מאז 2016 הלקוחות חוזרים כי מכירים אותם בשם. מתלבטים? מתקשרים ואנחנו מרכיבים לכם הזמנה.</p>[/div][/ux_text][/col]
  [/row]
[/section]
```

---

## בלוק 4 — קטגוריות (שם בלוק: `home-categories`)

```
[section bg_color="#F2E7D5" padding="80px"]
  [row]
    [col span="12"]
      [ux_text]
        <p class="ds-kicker">החנות שלנו</p>
        <h2 style="font-size:40px;font-weight:900;">מה בא לכם היום?</h2>
        <p>כל קטגוריה — במלאי טרי שמתחדש כל בוקר.</p>
      [/ux_text]
    [/col]
  [/row]
  [row]
    [col span="4" span__sm="12"][ux_banner height="280px" bg="[IMG-CAT-1]" hover="zoom" link="/product-category/pitzuchim/"][text_box position_x="50" position_y="90"][ux_text]<h3 style="color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);">פיצוחים ואגוזים</h3>[/ux_text][/text_box][/ux_banner][/col]
    [col span="4" span__sm="12"][ux_banner height="280px" bg="[IMG-CAT-2]" hover="zoom" link="/product-category/dried-fruits/"][text_box position_x="50" position_y="90"][ux_text]<h3 style="color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);">פירות יבשים</h3>[/ux_text][/text_box][/ux_banner][/col]
    [col span="4" span__sm="12"][ux_banner height="280px" bg="[IMG-CAT-3]" hover="zoom" link="/product-category/gifts/"][text_box position_x="50" position_y="90"][ux_text]<h3 style="color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);">מארזים ומתנות</h3>[/ux_text][/text_box][/ux_banner][/col]
    [col span="4" span__sm="12"][ux_banner height="280px" bg="[IMG-CAT-4]" hover="zoom" link="/product-category/spices/"][text_box position_x="50" position_y="90"][ux_text]<h3 style="color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);">תבלינים</h3>[/ux_text][/text_box][/ux_banner][/col]
    [col span="4" span__sm="12"][ux_banner height="280px" bg="[IMG-CAT-5]" hover="zoom" link="/product-category/legumes/"][text_box position_x="50" position_y="90"][ux_text]<h3 style="color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);">קטניות ובריאות</h3>[/ux_text][/text_box][/ux_banner][/col]
    [col span="4" span__sm="12"][ux_banner height="280px" bg="[IMG-CAT-6]" hover="zoom" link="/product-category/sale/"][text_box position_x="50" position_y="90"][ux_text]<h3 style="color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);">מבצעי השבוע</h3>[/ux_text][/text_box][/ux_banner][/col]
  [/row]
[/section]
```

---

## בלוק 5 — הנמכרים ביותר (שם בלוק: `home-bestsellers`) — מוצרי WooCommerce אמיתיים

```
[section bg_color="#FAF4EA" padding="80px"]
  [row]
    [col span="12"]
      [ux_text]
        <p class="ds-kicker">הנמכרים ביותר</p>
        <h2 style="font-size:40px;font-weight:900;">אלה שנגמרים ראשונים</h2>
        <p>ארבעת המוצרים שהלקוחות שלנו מזמינים שוב ושוב.</p>
      [/ux_text]
    [/col]
  [/row]
  [row]
    [col span="12"]
      [ux_products style="normal" columns="4" ids="[ID-פקאן-קלוי],[ID-פקאן-מקורמל],[ID-פקאן-אוראו],[ID-פקאן-בקליפה]" image_hover="zoom" text_align="right"]
    [/col]
  [/row]
  [row]
    [col span="12" align="center"]
      [button text="לכל המוצרים בחנות" class="ds-btn-ghost" size="large" link="/shop/"]
    [/col]
  [/row]
[/section]
```
> טיפ: אפשר במקום `ids` להשתמש ב־`orderby="sales" order="desc"` כדי שהבלוק יתעדכן אוטומטית לפי המכירות בפועל.

---

## בלוק 6 — הסיפור שלנו (שם בלוק: `home-story`)

```
[section bg_color="#33241A" padding="90px" dark="true"]
  [row v_align="middle"]
    [col span="5" span__sm="12"]
      [ux_image id="[IMG-STORY]" image_size="large" style="border-radius:20px;overflow:hidden;"]
    [/col]
    [col span="7" span__sm="12"]
      [ux_text]
        <p class="ds-kicker" style="color:#E09A2D;">הסיפור שלנו</p>
        <h2 style="color:#FAF4EA;font-size:40px;font-weight:900;">התחלנו מקולה אחת קטנה בכפר סבא</h2>
        <p style="color:#D9C9B4;font-size:17px;">ב־2016 פתח איתמר שמש את החנות הראשונה מתוך אהבה אחת פשוטה: פקאן שנקלה נכון. מאז, דרך השמש הפכה לכתובת של אלפי משפחות באזור — אותם עקרונות, אותה קולה, אותה קפדנות על כל שקית שיוצאת מהדלת.</p>
      [/ux_text]
      [gap height="20px"]
      [row_inner]
        [col_inner span="4" span__sm="4"][ux_text][div class="ds-stat"]<b>10</b><span style="color:#D9C9B4;">שנות קלייה יומית</span>[/div][/ux_text][/col_inner]
        [col_inner span="4" span__sm="4"][ux_text][div class="ds-stat"]<b>1000+</b><span style="color:#D9C9B4;">משפחות שחוזרות</span>[/div][/ux_text][/col_inner]
        [col_inner span="4" span__sm="4"][ux_text][div class="ds-stat"]<b>100%</b><span style="color:#D9C9B4;">קלייה במקום</span>[/div][/ux_text][/col_inner]
      [/row_inner]
    [/col]
  [/row]
[/section]
```

---

## בלוק 7 — לקוחות מספרים (שם בלוק: `home-testimonials`)

```
[section bg_color="#FAF4EA" padding="80px"]
  [row]
    [col span="12"]
      [ux_text]
        <p class="ds-kicker">לקוחות מספרים</p>
        <h2 style="font-size:40px;font-weight:900;">אל תאמינו לנו. תאמינו להם.</h2>
      [/ux_text]
    [/col]
  [/row]
  [row]
    [col span="4" span__sm="12"][ux_text][div class="ds-quote"]<div class="ds-stars">★★★★★</div><p>"הפקאן המקורמל הזה גמר לנו את הערב. הזמנתי בבוקר — בצהריים זה היה אצלי בדלת. טרי ברמה שלא הכרתי."</p><strong style="color:#75713F;">מיכל · כפר סבא</strong>[/div][/ux_text][/col]
    [col span="4" span__sm="12"][ux_text][div class="ds-quote"]<div class="ds-stars">★★★★★</div><p>"קונים אצלם מארזים לכל החגים והאירועים. תמיד מקבלים בדיוק מה שהבטיחו, ותמיד טרי מהקלייה של אותו יום."</p><strong style="color:#75713F;">אבי · אורנית</strong>[/div][/ux_text][/col]
    [col span="4" span__sm="12"][ux_text][div class="ds-quote"]<div class="ds-stars">★★★★★</div><p>"שירות של פעם: התקשרתי, התייעצתי, הרכיבו לי הזמנה לפי הטעם של הילדים. ככה נראית חנות שאכפת לה."</p><strong style="color:#75713F;">רונית · הוד השרון</strong>[/div][/ux_text][/col]
  [/row]
[/section]
```
> חשוב: החליפו את הציטוטים לביקורות אמיתיות של לקוחות (מגוגל/פייסבוק) — אלה נוסחו כדוגמה בלבד.

---

## בלוק 8 — מארזים ומתנות (שם בלוק: `home-gifts`)

```
[section bg_color="#F2E7D5" padding="90px"]
  [row v_align="middle"]
    [col span="7" span__sm="12"]
      [ux_text]
        <p class="ds-kicker">מארזים ומתנות</p>
        <h2 style="font-size:40px;font-weight:900;">מתנה שנגמרת עד סוף הערב</h2>
        <p style="font-size:17px;">מארחים? מפנקים עובדים? צריכים מתנה שתמיד עובדת? המארזים שלנו מורכבים ביום המשלוח עצמו — פקאנים, אגוזים ופירות יבשים בשיא הטריות, באריזה מכובדת שמוכנה להגשה.</p>
      [/ux_text]
      [gap height="14px"]
      [button text="להרכבת מארז" class="ds-btn-main" size="large" link="/product-category/gifts/"]
    [/col]
    [col span="5" span__sm="12"]
      [ux_image id="[IMG-GIFT]" image_size="large" style="border-radius:20px;overflow:hidden;"]
    [/col]
  [/row]
[/section]
```

---

## בלוק 9 — פס סגירה CTA (שם בלוק: `home-cta-band`)

```
[section padding="72px" class="ds-band" bg_color="#E09A2D"]
  [row h_align="center"]
    [col span="9" span__sm="12" align="center"]
      [ux_text]
        <h2 style="font-size:38px;font-weight:900;color:#33241A;">הקלייה של מחר בבוקר כבר מחכה לכם</h2>
        <p style="font-size:18px;color:#33241A;max-width:560px;margin:10px auto 8px;">הזמינו עכשיו וקבלו משלוח חינם מהיום להיום בכפר סבא ואורנית. מעדיפים לדבר? אנחנו כאן.</p>
      [/ux_text]
      [gap height="14px"]
      [button text="להזמנה באתר" style="shade" size="large" link="/shop/" color="#33241A"]
      [ux_text]
        <p style="margin-top:16px;"><a href="tel:0542473153" style="font-weight:900;font-size:22px;color:#33241A;">054-2473153</a></p>
      [/ux_text]
    [/col]
  [/row]
[/section]
```

---

## סדר ההרכבה בעמוד הבית

```
[block id="home-hero"]
[block id="home-trust-bar"]
[block id="home-why-us"]
[block id="home-categories"]
[block id="home-bestsellers"]
[block id="home-story"]
[block id="home-testimonials"]
[block id="home-gifts"]
[block id="home-cta-band"]
```

## צ׳ק־ליסט לפני עלייה לאוויר
- [ ] לעדכן קודי HEX בבלוק 0 לפי צבעי הלוגו המדויקים (Flatsome → Advanced → Custom CSS)
- [ ] להחליף את כל `[IMG-...]` בתמונות אמיתיות מספריית המדיה (תמונות מוצר/חנות אמיתיות ימכרו הכי טוב)
- [ ] להזין `ids` אמיתיים של מוצרים בבלוק 5 (או orderby="sales")
- [ ] לוודא שהקישורים לקטגוריות תואמים לסלאגים באתר
- [ ] להחליף ציטוטים לביקורות אמיתיות (בלוק 7)
- [ ] לבדוק תצוגת מובייל ב־UX Builder (span__sm כבר מוגדר בכל העמודות)
