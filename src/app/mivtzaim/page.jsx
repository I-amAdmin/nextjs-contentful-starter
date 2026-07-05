import { promotions } from '../../../content/promotions.js';

export const metadata = {
  title: `${promotions.monthTitle} | דרך השמש`,
  description: `${promotions.monthTitle} בדרך השמש — ${promotions.tagline}`,
};

function Price({ price, unit }) {
  return (
    <span className="flex items-baseline gap-1 whitespace-nowrap">
      <span className="text-sm font-semibold text-amber-700">₪</span>
      <span className="text-2xl font-extrabold text-amber-700">{price}</span>
      {unit && <span className="text-xs text-stone-500">{unit}</span>}
    </span>
  );
}

export default function PromotionsPage() {
  const p = promotions;

  return (
    <div dir="rtl" lang="he" className="min-h-screen bg-amber-50 text-stone-800">
      {/* כותרת ראשית */}
      <header className="px-6 pt-12 pb-10 text-center bg-gradient-to-b from-amber-400 via-amber-300 to-amber-50 sm:pt-16">
        <div className="max-w-3xl mx-auto">
          <p className="text-5xl mb-4" aria-hidden="true">🌞</p>
          <p className="text-lg font-semibold tracking-wide text-amber-900">דרך השמש</p>
          <h1 className="mt-2 text-4xl font-extrabold text-stone-900 sm:text-5xl">
            {p.monthTitle}
          </h1>
          <p className="mt-3 text-xl text-stone-800">{p.tagline}</p>
          {p.notes.map((note) => (
            <p key={note} className="mt-4 text-sm text-amber-900/80">{note}</p>
          ))}
        </div>
      </header>

      <main className="max-w-3xl px-4 pb-16 mx-auto sm:px-6">
        {/* מבצעים מודגשים */}
        {p.featured?.length > 0 && (
          <section className="mt-2">
            <h2 className="flex items-center gap-2 mb-1 text-2xl font-bold text-stone-900">
              <span aria-hidden="true">⭐</span> מבצעים מיוחדים
            </h2>
            {p.featuredNote && (
              <p className="mb-4 text-sm font-medium text-amber-800">{p.featuredNote}</p>
            )}
            <div className="grid gap-4 sm:grid-cols-2">
              {p.featured.map((item) => (
                <div
                  key={item.name}
                  className="p-5 bg-white border-2 shadow-sm rounded-2xl border-amber-400"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-lg font-bold">{item.name}</h3>
                    <Price price={item.price} unit={item.unit} />
                  </div>
                  {item.note && <p className="mt-2 text-sm text-stone-600">{item.note}</p>}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* קבוצות מבצעים */}
        {p.sections.map((section) => (
          <section key={section.title} className="mt-10">
            <h2 className="flex items-center gap-2 mb-4 text-2xl font-bold text-stone-900">
              {section.emoji && <span aria-hidden="true">{section.emoji}</span>}
              {section.title}
            </h2>
            <ul className="overflow-hidden bg-white divide-y shadow-sm rounded-2xl divide-amber-100">
              {section.items.map((item) => (
                <li key={item.name} className="flex items-center justify-between gap-3 px-5 py-4">
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    {item.note && <p className="mt-0.5 text-sm text-stone-500">{item.note}</p>}
                  </div>
                  <Price price={item.price} unit={item.unit} />
                </li>
              ))}
            </ul>
          </section>
        ))}

        {/* סניפים */}
        <section className="mt-12">
          <h2 className="flex items-center gap-2 mb-4 text-2xl font-bold text-stone-900">
            <span aria-hidden="true">📍</span> מחכים לכם בסניפים
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {p.branches.map((branch) => (
              <a
                key={branch.address}
                href={`https://waze.com/ul?q=${encodeURIComponent(`${branch.address}`)}&navigate=yes`}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-5 transition bg-white shadow-sm rounded-2xl hover:shadow-md"
              >
                <p className="font-bold">{branch.name}</p>
                <p className="mt-1 text-stone-600">{branch.address}</p>
                <p className="mt-3 text-sm font-semibold text-sky-600">ניווט עם Waze ←</p>
              </a>
            ))}
          </div>
        </section>

        <footer className="mt-12 text-sm text-center text-stone-500">
          {p.notes.map((note) => (
            <p key={note}>{note}</p>
          ))}
          <p className="mt-1">ט.ל.ח · התמונות להמחשה בלבד</p>
        </footer>
      </main>
    </div>
  );
}
