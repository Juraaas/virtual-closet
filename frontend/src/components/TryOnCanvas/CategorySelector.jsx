import "./CategorySelector.css";

export default function CategorySelector({ label, items, selectedIndex, onChange }) {
  if (items.length === 0) {
    return (
      <div className="category-selector category-selector--empty">
        <span className="category-selector__label">{label}</span>
        <span className="category-selector__empty-msg">Brak przedmiotów w tej kategorii</span>
      </div>
    );
  }

  const goPrev = () => {
    const nextIndex = (selectedIndex - 1 + items.length) % items.length;
    onChange(nextIndex);
  };

  const goNext = () => {
    const nextIndex = (selectedIndex + 1) % items.length;
    onChange(nextIndex);
  };

  const currentItem = items[selectedIndex];

  return (
    <div className="category-selector">
      <span className="category-selector__label">{label}</span>
      <div className="category-selector__control">
        <button className="category-selector__arrow" onClick={goPrev} aria-label={`Poprzedni ${label}`}>
          ‹
        </button>
        <span className="category-selector__item-name">{currentItem.name}</span>
        <button className="category-selector__arrow" onClick={goNext} aria-label={`Następny ${label}`}>
          ›
        </button>
      </div>
    </div>
  );
}