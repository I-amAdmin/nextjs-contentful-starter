import { Assistant } from 'next/font/google';
import { promotions } from '../../../content/promotions.js';

const assistant = Assistant({
  subsets: ['hebrew', 'latin'],
  weight: ['400', '600', '700', '800'],
});

// פלטת הצבעים של דרך השמש (לפי האתר הרשמי)
// זית כהה: #3F3F2C · זית: #666644 · זהב־זית: #A6A263 · קרם: #F5F0E1

export const metadata = {
  title: `${promotions.monthTitle} | דרך השמש`,
  description: `${promotions.monthTitle} בדרך השמש — ${promotions.tagline}`,
};

function Price({ price, unit }) {
  return (
    <span className="flex items-baseline gap-1 whitespace-nowrap">
      <span className="text-sm font-semibold text-[#8a874e]">₪</span>
      <span className="text-2xl font-extrabold text-[#3F3F2C]">{price}</span>
      {unit && <span className="text-xs text-[#666644]">{unit}</span>}
    </span>
  );
}

// סמל בהשראת הלוגו: גבעה מעוגלת עם עלה
function Emblem() {
  return (
    <svg viewBox="0 0 120 64" className="w-24 h-auto mx-auto" aria-hidden="true">
      <path
        d="M8 58 Q10 38 24 28 Q30 12 45 14 Q52 2 62 8 Q72 2 80 12 Q95 12 100 28 Q112 38 112 58 Z"
        fill="#A6A263"
      />
      <path
        d="M60 58 Q58 40 60 30 M60 38 Q50 34 46 26 Q56 26 60 34 M60 32 Q68 28 72 20 Q62 22 60 30"
        stroke="#3F3F2C"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      <rect x="4" y="58" width="112" height="3" rx="1.5" fill="#3F3F2C" />
    </svg>
  );
}

export default function PromotionsPage() {
  const p = promotions;

  return (
    <div dir="rtl" lang="he" className={`${assistant.className} min-h-screen bg-[#F5F0E1] text-[#3F3F2C]`}>
      {/* פס עליון כהה */}
      {p.notes[0] && (
        <div className="px-4 py-2 text-sm font-semibold text-center text-[#F5F0E1] bg-[#3F3F2C]">
          {p.notes[0]}
        </div>
      )}

      {/* כותרת ראשית */}
      <header className="px-6 pt-10 pb-8 text-center bg-white border-b-4 border-[#A6A263]">
        <div className="max-w-3xl mx-auto">
          <Emblem />
          <p className="mt-3 text-2xl font-extrabold tracking-wide text-[#3F3F2C]">דרך השמש</p>
          {p.storeTagline && (
            <p className="mt-1 text-sm text-[#666644]">{p.storeTagline}</p>
          )}
          <h1 className="mt-6 text-4xl font-extrabold text-[#3F3F2C] sm:text-5xl">
            {p.monthTitle}
          </h1>
          <p className="mt-3 text-xl text-[#666644]">{p.tagline}</p>
        </div>
      </header>

      <main className="max-w-3xl px-4 pb-16 mx-auto sm:px-6">
        {/* מבצעים מודגשים */}
        {p.featured?.length > 0 && (
          <section className="mt-8">
            <h2 className="flex items-center gap-2 mb-1 text-2xl font-extrabold text-[#3F3F2C]">
              <span aria-hidden="true">⭐</span> מבצעים מיוחדים
            </h2>
            {p.featuredNote && (
              <p className="mb-4 text-sm font-semibold text-[#8a874e]">{p.featuredNote}</p>
            )}
            <div className="grid gap-4 sm:grid-cols-2">
              {p.featured.map((item) => (
                <div
                  key={item.name}
                  className="p-5 bg-white border-2 shadow-sm rounded-2xl border-[#A6A263]"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-lg font-bold">{item.name}</h3>
                    <Price price={item.price} unit={item.unit} />
                  </div>
                  {item.note && <p className="mt-2 text-sm text-[#666644]">{item.note}</p>}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* קבוצות מבצעים */}
        {p.sections.map((section) => (
          <section key={section.title} className="mt-10">
            <h2 className="flex items-center gap-2 px-5 py-3 mb-0 text-xl font-extrabold text-[#F5F0E1] bg-[#666644] rounded-t-2xl">
              {section.emoji && <span aria-hidden="true">{section.emoji}</span>}
              {section.title}
            </h2>
            <ul className="overflow-hidden bg-white divide-y shadow-sm rounded-b-2xl divide-[#EAE5D3]">
              {section.items.map((item) => (
                <li key={item.name} className="flex items-center justify-between gap-3 px-5 py-4">
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    {item.note && <p className="mt-0.5 text-sm text-[#8a874e]">{item.note}</p>}
                  </div>
                  <Price price={item.price} unit={item.unit} />
                </li>
              ))}
            </ul>
          </section>
        ))}

        {/* סניפים */}
        <section className="mt-12">
          <h2 className="flex items-center gap-2 mb-4 text-2xl font-extrabold text-[#3F3F2C]">
            <span aria-hidden="true">📍</span> מחכים לכם בסניפים
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {p.branches.map((branch) => (
              <a
                key={branch.address}
                href={`https://waze.com/ul?q=${encodeURIComponent(branch.address)}&navigate=yes`}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-5 transition bg-white border border-[#EAE5D3] shadow-sm rounded-2xl hover:shadow-md hover:border-[#A6A263]"
              >
                <p className="font-bold">{branch.name}</p>
                <p className="mt-1 text-[#666644]">{branch.address}</p>
                <p className="mt-3 text-sm font-bold text-[#8a874e]">ניווט עם Waze ←</p>
              </a>
            ))}
          </div>
        </section>

        <footer className="pt-8 mt-12 text-sm text-center border-t border-[#DCD6C0] text-[#666644]">
          {p.notes.map((note) => (
            <p key={note}>{note}</p>
          ))}
          <p className="mt-1">ט.ל.ח · התמונות להמחשה בלבד</p>
          {p.websiteUrl && (
            <p className="mt-4">
              <a
                href={p.websiteUrl}
                className="inline-block px-6 py-2 font-bold text-[#F5F0E1] transition rounded-full bg-[#666644] hover:bg-[#3F3F2C]"
              >
                לאתר דרך השמש ←
              </a>
            </p>
          )}
        </footer>
      </main>
    </div>
  );
}
