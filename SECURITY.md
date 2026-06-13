# Security & Privacy — GestureDJ

GestureDJ kamerangizdan foydalanadi, shuning uchun maxfiylik birinchi
o'rinda turadi. Quyida ilova nima qilishi va **nima qilmasligi** aniq
yozilgan.

## Kamera va maxfiylik

- **Video hech qayerga yuborilmaydi.** Kamera tasviri faqat sizning
  kompyuteringizda, xotirada qayta ishlanadi (Google MediaPipe, lokal).
  Hech qanday kadr, rasm yoki qo'l ma'lumoti internetga jo'natilmaydi.
- **Hech narsa saqlanmaydi.** Ilova video yoki rasm fayl qilib yozmaydi.
  Har bir kadr ishlangach o'chib ketadi.
- **Telemetriya yo'q.** Foydalanish statistikasi, analitika yoki kuzatuv yo'q.
- Kamera faqat ilova ishlab turganda yoqiladi; tray'dan **Chiqish** bilan
  to'liq o'chadi.

## Tarmoq (internet)

Ilova faqat **bitta** marta internetga murojaat qiladi:

| Qachon | Nimaga | Xavfsizlik |
|--------|--------|-----------|
| Birinchi ishga tushishda | Qo'l aniqlash modelini (~8MB) yuklab olish | HTTPS orqali Google serveridan; fayl **SHA-256** bilan tekshiriladi |

EXE versiyasida model allaqachon ichiga qadoqlangan, shuning uchun u **umuman
internetsiz** ishlaydi. Shriftlar ham ilova ichida (lokal) — sozlamalar
oynasi ochilganda hech qanday tashqi serverga (Google Fonts va h.k.) bormaydi.

## Tizimga ta'sir

- **Administrator huquqi talab qilinmaydi.** Hammasi oddiy foydalanuvchi
  huquqida ishlaydi.
- **Avtostart** (ixtiyoriy) faqat `HKCU\…\Run` registr kalitini yozadi —
  bu sizning foydalanuvchi profilingiz, tizimga emas. Istalgan vaqtda
  sozlamalardan o'chirib qo'yish mumkin.
- Ilova faqat o'z papkasiga yozadi: `config.json` (sozlamalar) va
  `logs/` (diagnostika loglari). Loglar shaxsiy ma'lumot saqlamaydi —
  faqat holat o'zgarishlari va ovoz darajasi.

## Audio

- Ilova faqat **tizim ovozi balandligini** va play/pause/mute ni boshqaradi
  (Windows Core Audio API). Boshqa ilovalaringizga, fayllaringizga yoki
  tarmoqqa kira olmaydi.

## Ochiq kod

Butun kod ochiq: har bir tarmoq chaqiruvi, har bir fayl amalini
[manba kodida](gesturedj/) tekshirishingiz mumkin. Hech qanday yashirin
xatti-harakat yo'q.

## Zaiflik haqida xabar berish

Xavfsizlik muammosini topsangiz, GitHub Issues orqali yoki to'g'ridan-to'g'ri
muallifga xabar bering.
